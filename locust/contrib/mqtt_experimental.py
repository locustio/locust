from __future__ import annotations

from locust.contrib.mqtt import MqttClient, MqttUser
from locust.env import Environment

import selectors
import typing
from contextlib import suppress

import paho.mqtt.client as mqtt

if typing.TYPE_CHECKING:
    pass


class ExperimentalMqttClient(MqttClient):
    def __init__(self, *args, environment, client_id=None, protocol=mqtt.MQTTv311, **kwargs):
        super().__init__(*args, environment=environment, client_id=client_id, protocol=protocol, **kwargs)

    def _loop(self, timeout: float = 1.0) -> mqtt.MQTTErrorCode:
        if timeout < 0.0:
            raise ValueError("Invalid timeout.")

        sel = selectors.DefaultSelector()

        eventmask = selectors.EVENT_READ

        with suppress(IndexError):
            packet = self._out_packet.popleft()
            self._out_packet.appendleft(packet)
            eventmask = selectors.EVENT_WRITE | eventmask

        # used to check if there are any bytes left in the (SSL) socket
        pending_bytes = 0
        if hasattr(self._sock, "pending"):
            pending_bytes = self._sock.pending()  # type: ignore

        # if bytes are pending do not wait in select
        if pending_bytes > 0:
            timeout = 0.0

        try:
            if self._sockpairR is None:
                sel.register(self._sock, eventmask)  # type: ignore
            else:
                sel.register(self._sock, eventmask)  # type: ignore
                sel.register(self._sockpairR, selectors.EVENT_READ)

            events = sel.select(timeout)

        except TypeError:
            # Socket isn't correct type, in likelihood connection is lost
            return mqtt.MQTT_ERR_CONN_LOST
        except ValueError:
            # Can occur if we just reconnected but rlist/wlist contain a -1 for
            # some reason.
            return mqtt.MQTT_ERR_CONN_LOST
        except Exception:
            # Note that KeyboardInterrupt, etc. can still terminate since they
            # are not derived from Exception
            return mqtt.MQTT_ERR_UNKNOWN

        socklist: list[list] = [[], []]

        for key, _event in events:
            if key.events & selectors.EVENT_READ:
                socklist[0].append(key.fileobj)

            if key.events & selectors.EVENT_WRITE:
                socklist[1].append(key.fileobj)

        if self._sock in socklist[0] or pending_bytes > 0:
            rc = self.loop_read()
            if rc or self._sock is None:
                return rc

        if self._sockpairR and self._sockpairR in socklist[0]:
            # Stimulate output write even though we didn't ask for it, because
            # at that point the publish or other command wasn't present.
            socklist[1].insert(0, self._sock)
            # Clear sockpairR - only ever a single byte written.
            with suppress(BlockingIOError):
                # Read many bytes at once - this allows up to 10000 calls to
                # publish() inbetween calls to loop().
                self._sockpairR.recv(10000)

        if self._sock in socklist[1]:
            rc = self.loop_write()
            if rc or self._sock is None:
                return rc

        sel.close()

        return self.loop_misc()


class ExperimentalMqttUser(MqttUser):
    abstract = True

    client_cls: type[MqttClient] = ExperimentalMqttClient

    def __init__(self, environment: Environment):
        super().__init__(environment)
