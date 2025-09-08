from locust import User
from locust.event import EventHook

from typing import Any

import gevent
import socketio


class SocketIOClient(socketio.Client):
    def __init__(self, request_event: EventHook, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_event = request_event

    def connect(self, *args, **kwargs):
        """
        Wraps :meth:`socketio.Client.connect`.
        """
        with self.request_event.measure("WS", "connect") as _:
            super().connect(*args, **kwargs)

    def send(self, data, namespace=None, callback=None, name="Unnamed") -> None:
        """
        Wraps :meth:`socketio.Client.send`.
        """
        exception = None
        try:
            super().send(data, namespace, callback)
        except Exception as e:
            exception = e
        self.request_event.fire(
            request_type="WSS",
            name=name,
            response_time=0,
            response_length=len(data or []),
            exception=exception,
            context={},
        )

    def emit(self, event, data=None, namespace=None, callback=None) -> None:
        """
        Wraps :meth:`socketio.Client.emit`.
        """
        exception = None
        try:
            super().emit(event, data, namespace, callback)
        except Exception as e:
            exception = e
        self.request_event.fire(
            request_type="WSE",
            name=str(event),
            response_time=0,
            response_length=len(data or []),
            exception=exception,
            context={},
        )

    def call(self, event, data=None, *args, **kwargs):
        """
        Wraps :meth:`socketio.Client.call`.
        """
        with self.request_event.measure("WSC", event) as _:
            return super().call(event, data, *args, **kwargs)

    def on_message(self, event: str, data: str) -> None:
        """
        This is the default handler for events received.
        You can register separate handlers using self.sio.on(event, handler)

        Measuring response_time isn't obvious for for WebSockets/SocketIO so we set them to 0.
        Sometimes response time can be inferred from the event data (if it contains a timestamp)
        or related to a message that you sent. Override this method in your User class to do that.
        """
        self.request_event.fire(
            request_type="WSR",
            name=event,
            response_time=0,
            response_length=len(data or []),
            exception=None,
            context={},
        )


class SocketIOUser(User):
    """
    SocketIOUser creates an instance of :class:`socketio.Client` to log requests.
    See example in :gh:`examples/socketio/socketio_ex.py`.
    """

    abstract = True
    options: dict[str, Any] = {}
    """socketio.Client options, e.g. `{"reconnection_attempts": 1, "reconnection_delay": 2, "logger": True, "engineio_logger": True}`"""
    sio: SocketIOClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sio = SocketIOClient(self.environment.events.request, **self.options)
        self.sio_greenlet = gevent.spawn(self.sio.wait)
        self.sio.on("*", self.sio.on_message)
