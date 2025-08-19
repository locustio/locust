from locust import User

import gevent
import socketio


class SocketIOUser(User):
    """
    SocketIOUser wraps the `socketio.Client` to log requests.
    See socketio_ex.py for an example of how to use it.
    """

    abstract = True
    options: dict = {}
    """socketio.Client options, e.g. `{"reconnection_attempts": 1, "reconnection_delay": 2}`"""
    client: socketio.Client
    """The underlying socketio.Client instance. Can be useful to call directly if you want to skip logging a requests."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = socketio.Client(**self.options)
        self.ws_greenlet = gevent.spawn(self.client.wait)
        self.client.on("*", self.on_message)

    # This is the default handler for events. You can override it for custom behavior,
    # or even register separate handlers using self.client.on(event, handler)
    def on_message(self, event: str, data: str) -> None:
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
        with self.environment.events.request.measure("WS", "connect") as _:
            self.client.connect(*args, **kwargs)

    def send(self, name=None, data=None, namespace=None) -> None:
        exception = None
        try:
            self.client.send(name, data, namespace)
        except Exception as e:
            exception = e
        self.environment.events.request.fire(
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
        self.environment.events.request.fire(
            request_type="WSE",
            name=name,
            response_time=0,
            response_length=len(data or []),
            exception=exception,
            context={},
        )

    def call(self, event, data, *args, **kwargs):
        with self.environment.events.request.measure("WSC", event) as _:
            return self.client.call(event, data, *args, **kwargs)

    def on_stop(self):
        self.client.disconnect()
