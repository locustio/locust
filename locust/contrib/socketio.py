from locust import User

import gevent
import socketio


class SocketIOUser(User):
    """
    SocketIOUser wraps an instance of :class:`socketio.Client` to log requests.
    See example in :gh:`examples/socketio/socketio_ex.py`.
    """

    abstract = True
    options: dict = {}
    """socketio.Client options, e.g. `{"reconnection_attempts": 1, "reconnection_delay": 2}`"""
    client: socketio.Client
    """The underlying :class:`socketio.Client` instance. Can be useful to call directly if you want to skip logging a requests."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = socketio.Client(**self.options)
        self.ws_greenlet = gevent.spawn(self.client.wait)
        self.client.on("*", self.on_message)

    #
    def on_message(self, event: str, data: str) -> None:
        """
        This is the default handler for events. You can override it for custom behavior,
        or even register separate handlers using self.client.on(event, handler)

        Measuring response_time isn't obvious for for WebSockets. Sometimes a response time
        can be inferred from the event data (if it contains a timestamp) or related to
        a message that you sent. Override this method in your User class to do that.
        """
        self.environment.events.request.fire(
            request_type="WSR",
            name=event,
            response_time=0,
            response_length=len(data or []),
            exception=None,
            context={},
        )

    def connect(self, *args, **kwargs):
        """
        Wraps :meth:`socketio.Client.connect`.
        """
        with self.environment.events.request.measure("WS", "connect") as _:
            self.client.connect(*args, **kwargs)

    def send(self, name, data=None, namespace=None) -> None:
        """
        Wraps :meth:`socketio.Client.send`.
        """
        exception = None
        try:
            self.client.send(data, namespace)
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

    def emit(self, name, data=None, namespace=None, callback=None) -> None:
        """
        Wraps :meth:`socketio.Client.emit`.
        """
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

    def call(self, event, data=None, *args, **kwargs):
        """
        Wraps :meth:`socketio.Client.call`.
        """
        with self.environment.events.request.measure("WSC", event) as _:
            return self.client.call(event, data, *args, **kwargs)

    def on_stop(self):
        self.client.disconnect()
