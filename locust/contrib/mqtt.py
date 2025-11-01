from __future__ import annotations

from locust import User
from locust.env import Environment

import random
import time
import typing

import paho.mqtt.client as mqtt

if typing.TYPE_CHECKING:
    from paho.mqtt.client import MQTTMessageInfo
    from paho.mqtt.enums import MQTTProtocolVersion
    from paho.mqtt.properties import Properties
    from paho.mqtt.reasoncodes import ReasonCode
    from paho.mqtt.subscribeoptions import SubscribeOptions


# A SUBACK response for MQTT can only contain 0x00, 0x01, 0x02, or 0x80. 0x80
# indicates a failure to subscribe.
#
# http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html#_Figure_3.26_-
SUBACK_FAILURE = 0x80
REQUEST_TYPE = "MQTT"


def _generate_random_id(
    length: int,
    alphabet: str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
):
    """Generate a random ID from the given alphabet.

    Args:
        length: the number of random characters to generate.
        alphabet: the pool of random characters to choose from.
    """
    return "".join(random.choice(alphabet) for _ in range(length))


def _generate_mqtt_event_name(event_type: str, qos: int, topic: str):
    """Generate a name to identify publish/subscribe tasks.

    This will be used to ultimately identify tasks in the Locust web console.
    This will identify publish/subscribe tasks with their QoS & associated
    topic.

    Examples:
        publish:0:my/topic
        subscribe:1:my/other/topic

    Args:
        event_type: The type of MQTT event (subscribe or publish)
        qos: The quality-of-service associated with this event
        topic: The MQTT topic associated with this event
    """
    return f"{event_type}:{qos}:{topic}"


class PublishedMessageContext(typing.NamedTuple):
    """Stores metadata about outgoing published messages."""

    qos: int
    topic: str
    start_time: float
    payload_size: int


class MqttClient(mqtt.Client):
    def __init__(
        self,
        *args,
        environment: Environment,
        client_id: str | None = None,
        protocol: MQTTProtocolVersion = mqtt.MQTTv311,
        **kwargs,
    ):
        """Initializes a paho.mqtt.Client for use in Locust swarms.

        This class passes most args & kwargs through to the underlying
        paho.mqtt constructor.

        Args:
            environment: the Locust environment with which to associate events.
            client_id: the MQTT Client ID to use in connecting to the broker.
                If not set, one will be randomly generated.
            protocol: the MQTT protocol version.
                defaults to MQTT v3.11.
        """
        # If a client ID is not provided, this class will randomly generate an ID
        # of the form: `locust-[0-9a-zA-Z]{16}` (i.e., `locust-` followed by 16
        # random characters, so that the resulting client ID does not exceed the
        # specification limit of 23 characters).

        # This is done in this wrapper class so that this locust client can
        # self-identify when firing requests, since some versions of MQTT will
        # have the broker assign IDs to clients that do not provide one: in this
        # case, there is no way to retrieve the client ID.

        # See https://github.com/eclipse/paho.mqtt.python/issues/237
        if not client_id:
            client_id = f"locust-{_generate_random_id(16)}"

        super().__init__(*args, client_id=client_id, protocol=protocol, **kwargs)
        self.environment = environment
        # we need to set client_id in case the broker assigns one to us
        self.client_id = client_id

        self.on_publish = self._on_publish_cb  # type: ignore[assignment]

        if protocol == mqtt.MQTTv5:
            self.on_disconnect = self._on_disconnect_cb_v5
            self.on_connect = self._on_connect_cb_v5
            self.on_subscribe = self._on_subscribe_cb_v5
        else:
            self.on_disconnect = self._on_disconnect_cb_v3x  # type: ignore[assignment]
            self.on_connect = self._on_connect_cb_v3x  # type: ignore[assignment]
            self.on_subscribe = self._on_subscribe_cb_v3x  # type: ignore[assignment]

        self._publish_requests: dict[int, PublishedMessageContext] = {}
        self._subscribe_requests: dict[int, tuple[int, str, float]] = {}

    def _generate_event_name(self, event_type: str, qos: int, topic: str):
        return _generate_mqtt_event_name(event_type, qos, topic)

    def _on_publish_cb(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        mid: int,
    ):
        cb_time = time.time()
        try:
            request_context = self._publish_requests.pop(mid)
        except KeyError:
            # we shouldn't hit this block of code
            self.environment.events.request.fire(
                request_type=REQUEST_TYPE,
                name="publish",
                response_time=0,
                response_length=0,
                exception=AssertionError(f"Could not find message data for mid '{mid}' in _on_publish_cb."),
                context={
                    "client_id": self.client_id,
                    "mid": mid,
                },
            )
        else:
            # fire successful publish event
            self.environment.events.request.fire(
                request_type=REQUEST_TYPE,
                name=self._generate_event_name("publish", request_context.qos, request_context.topic),
                response_time=(cb_time - request_context.start_time) * 1000,
                response_length=request_context.payload_size,
                exception=None,
                context={
                    "client_id": self.client_id,
                    **request_context._asdict(),
                },
            )

    def _on_subscribe_cb_v3x(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        mid: int,
        granted_qos: list[int],
    ):
        cb_time = time.time()
        try:
            qos, topic, start_time = self._subscribe_requests.pop(mid)
        except KeyError:
            # we shouldn't hit this block of code
            self.environment.events.request.fire(
                request_type=REQUEST_TYPE,
                name="subscribe",
                response_time=0,
                response_length=0,
                exception=AssertionError(f"Could not find message data for mid '{mid}' in _on_subscribe_cb."),
                context={
                    "client_id": self.client_id,
                    "mid": mid,
                },
            )
        else:
            if SUBACK_FAILURE in granted_qos:
                self.environment.events.request.fire(
                    request_type=REQUEST_TYPE,
                    name=self._generate_event_name("subscribe", qos, topic),
                    response_time=(cb_time - start_time) * 1000,
                    response_length=0,
                    exception=AssertionError(f"Broker returned an error response during subscription: {granted_qos}"),
                    context={
                        "client_id": self.client_id,
                        "qos": qos,
                        "topic": topic,
                        "start_time": start_time,
                    },
                )
            else:
                # fire successful subscribe event
                self.environment.events.request.fire(
                    request_type=REQUEST_TYPE,
                    name=self._generate_event_name("subscribe", qos, topic),
                    response_time=(cb_time - start_time) * 1000,
                    response_length=0,
                    exception=None,
                    context={
                        "client_id": self.client_id,
                        "qos": qos,
                        "topic": topic,
                        "start_time": start_time,
                    },
                )

    # pylint: disable=unused-argument
    def _on_subscribe_cb_v5(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        mid: int,
        reason_codes: list[ReasonCode],
        properties: Properties,
    ) -> None:
        granted_qos = [rc.value for rc in reason_codes]
        return self._on_subscribe_cb_v3x(client, userdata, mid, granted_qos)

    def _on_disconnect_cb(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        rc: int | ReasonCode,
    ):
        if rc != 0:
            self.environment.events.request.fire(
                request_type=REQUEST_TYPE,
                name="disconnect",
                response_time=0,
                response_length=0,
                exception=rc,
                context={
                    "client_id": self.client_id,
                },
            )
        else:
            self.environment.events.request.fire(
                request_type=REQUEST_TYPE,
                name="disconnect",
                response_time=0,
                response_length=0,
                exception=None,
                context={
                    "client_id": self.client_id,
                },
            )

    def _on_disconnect_cb_v3x(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        rc: int,
    ):
        return self._on_disconnect_cb(client, userdata, rc)

    # pylint: disable=unused-argument
    def _on_disconnect_cb_v5(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        disconnect_flags: mqtt.DisconnectFlags,
        reasoncode: ReasonCode,
        properties: Properties | None,
    ) -> None:
        return self._on_disconnect_cb(client, userdata, reasoncode)

    def _on_connect_cb(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        flags: dict[str, int],
        rc: int | ReasonCode,
    ):
        if rc != 0:
            self.environment.events.request.fire(
                request_type=REQUEST_TYPE,
                name="connect",
                response_time=0,
                response_length=0,
                exception=Exception(str(rc)),
                context={
                    "client_id": self.client_id,
                },
            )
        else:
            self.environment.events.request.fire(
                request_type=REQUEST_TYPE,
                name="connect",
                response_time=0,
                response_length=0,
                exception=None,
                context={
                    "client_id": self.client_id,
                },
            )

    def _on_connect_cb_v3x(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        flags: dict[str, int],
        rc: int,
    ):
        return self._on_connect_cb(client, userdata, flags, rc)

    # pylint: disable=unused-argument
    def _on_connect_cb_v5(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        connect_flags: mqtt.ConnectFlags,
        reasoncode: ReasonCode,
        properties: Properties | None,
    ) -> None:
        self._on_connect_cb(client, userdata, {}, reasoncode)

    def publish(
        self,
        topic: str,
        payload: mqtt.PayloadType | None = None,
        qos: int = 0,
        retain: bool = False,
        properties: Properties | None = None,
    ) -> MQTTMessageInfo:
        """Publish a message to the MQTT broker.

        This method wraps the underlying paho-mqtt client's method in order to
        set up & fire Locust events.
        """
        request_context = PublishedMessageContext(
            qos=qos,
            topic=topic,
            start_time=time.time(),
            payload_size=len(payload) if payload and not isinstance(payload, (int, float)) else 0,
        )

        publish_info = super().publish(topic, payload=payload, qos=qos, retain=retain, properties=properties)

        if publish_info.rc != mqtt.MQTT_ERR_SUCCESS:
            self.environment.events.request.fire(
                request_type=REQUEST_TYPE,
                name=self._generate_event_name("publish", request_context.qos, request_context.topic),
                response_time=0,
                response_length=0,
                exception=publish_info.rc,
                context={
                    "client_id": self.client_id,
                    **request_context._asdict(),
                },
            )
        else:
            # store this for use in the on_publish callback
            self._publish_requests[publish_info.mid] = request_context

        return publish_info

    def subscribe(
        self,
        topic: str
        | tuple[str, int]
        | tuple[str, SubscribeOptions]
        | list[tuple[str, int]]
        | list[tuple[str, SubscribeOptions]],
        qos: int = 0,
        options: SubscribeOptions | None = None,
        properties: Properties | None = None,
    ) -> tuple[mqtt.MQTTErrorCode, int | None]:
        """Subscribe to a given topic.

        This method wraps the underlying paho-mqtt client's method in order to
        set up & fire Locust events.
        """
        start_time = time.time()
        subscribe_topic = topic if isinstance(topic, str) else topic[0][0]

        result, mid = super().subscribe(topic, qos, options, properties)  # type: ignore[arg-type]

        if result != mqtt.MQTT_ERR_SUCCESS:
            self.environment.events.request.fire(
                request_type=REQUEST_TYPE,
                name=self._generate_event_name("subscribe", qos, subscribe_topic),
                response_time=0,
                response_length=0,
                exception=result,
                context={
                    "client_id": self.client_id,
                    "qos": qos,
                    "topic": subscribe_topic,
                    "start_time": start_time,
                },
            )
        else:
            if mid is None:
                # QoS 0 subscriptions do not have a mid, so we'll just fire a success event immediately
                self.environment.events.request.fire(
                    request_type=REQUEST_TYPE,
                    name=self._generate_event_name("subscribe", qos, subscribe_topic),
                    response_time=(time.time() - start_time) * 1000,
                    response_length=0,
                    exception=None,
                    context={
                        "client_id": self.client_id,
                        "qos": qos,
                        "topic": subscribe_topic,
                        "start_time": start_time,
                    },
                )
            else:
                self._subscribe_requests[mid] = (qos, subscribe_topic, start_time)

        return result, mid


class MqttUser(User):
    abstract = True

    host = "localhost"
    port = 1883
    transport = "tcp"
    ws_path = "/mqtt"
    tls_context = None
    client_cls: type[MqttClient] = MqttClient
    client_id = None
    username = None
    password = None
    protocol = mqtt.MQTTv311

    def __init__(self, environment: Environment):
        super().__init__(environment)
        self.client: MqttClient = self.client_cls(
            environment=self.environment,
            transport=self.transport,
            client_id=self.client_id,
            protocol=self.protocol,
        )

        if self.tls_context:
            self.client.tls_set_context(self.tls_context)

        if self.transport == "websockets" and self.ws_path:
            self.client.ws_set_options(path=self.ws_path)

        if self.username and self.password:
            self.client.username_pw_set(
                username=self.username,
                password=self.password,
            )

        self.client.connect_async(
            host=self.host,  # type: ignore
            port=self.port,
        )
        self.client.loop_start()
