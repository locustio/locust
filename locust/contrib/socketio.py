from locust import User, events

import gevent
import socketio


class SocketIOClient(socketio.Client):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws_greenlet = gevent.spawn(self.wait)
        self.user = user
        self.on("*", self.user.on_message)


class SocketIOUser(User):
    abstract = True
    options: dict = {}  # socketio.Client options, e.g. {"reconnection_attempts": 1, "reconnection_delay": 2}
    client: SocketIOClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = SocketIOClient(self, **self.options)

    # This is the default handler for events. You can override it for custom behavior,
    # or even register separate handlers using self.client.on(event, handler)
    def on_message(self, event, data) -> None:
        self.environment.events.request.fire(
            request_type="WSR",
            name=event,
            # Response times are hard for WebSockets. Sometimes a response time can be inferred from the event data (if it contains a timestamp) or related to an event that you sent, but the default is just to set it to zero.
            response_time=0,
            response_length=len(data or []),
            exception=None,
            context={},
        )

    def connect(self, *args, **kwargs):
        with events.request.measure("WS", "connect") as _:
            self.client.connect(*args, **kwargs)

    def send(self, name=None, data=None, namespace=None) -> None:
        exception = None
        try:
            self.client.send(name, data, namespace)
        except Exception as e:
            exception = e
        events.request.fire(
            request_type="WSS",
            name=name,
            response_time=0,
            response_length=len(data or []),
            exception=exception,
            context={},
        )

    def emit(self, name=None, data=None, namespace=None, callback=None) -> None:
        exception = None
        try:
            self.client.emit(name, data, namespace, callback)
        except Exception as e:
            exception = e
        events.request.fire(
            request_type="WSE",
            name=name,
            response_time=0,
            response_length=len(data or []),
            exception=exception,
            context={},
        )

    def call(self, event, data, *args, **kwargs):
        with events.request.measure("WSC", event) as _:
            return self.client.call(event, data, *args, **kwargs)

    def on_stop(self):
        self.client.disconnect()
