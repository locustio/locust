from locust import HttpUser, task
from locust.contrib.socketio import SocketIOClient, SocketIOUser

from threading import Event

import gevent
from socketio import Client


class SIOFastHttpUser(SocketIOUser, HttpUser):
    options = {
        # "logger": True,
        # "engineio_logger": True,
    }
    event: Event

    def on_start(self) -> None:
        self.ws.connect("ws://localhost:5001", wait_timeout=10)

    @task
    def my_task(self):
        self.event = Event()
        # Send message and wait for confirmation
        self.ws.call("join_room", {"room": "room1"})
        # Register an event handler
        self.ws.on("chat_message", self.on_chat_message)
        # Use socketio.Client to send a message that wont be logged as a request
        Client.call(self.ws, "send_message", {"room": "room1", "message": "foo"})
        # Emit doesnt wait for confirmation
        self.ws.emit("send_message", {"room": "room1", "message": "bar"})
        self.event.wait()  # wait for on_message to set this event
        self.ws.call("leave_room", {"room": "room1"})
        # We've used multiple inheritance to combine this with FastHttpUser, so we can also make normal HTTP requests
        self.client.get("/")

    def on_chat_message(self, event: str, data: str) -> None:
        if event == "chat_message" and data.startswith("bar"):
            self.event.set()
        self.ws.on_message(event, data)

    def on_stop(self) -> None:
        self.ws.disconnect()


class AuthenticateViaSession(HttpUser):
    """
    Because SocketIOUser creates the socketio.Client internally, it isn't
    possible to pass parameters to it, but we can use its client in a User of a different type.
    """

    ws: SocketIOClient
    use_session = False

    def on_start(self) -> None:
        resp = self.client.post("/", json={"username": "foo", "password": "bar"})
        if self.use_session:
            self.ws = SocketIOClient(self.environment.events.request, http_session=self.client)
            self.ws.connect("ws://localhost:5001")
        else:
            # use jwt
            token = resp.json()["access_token"]
            self.ws = SocketIOClient(self.environment.events.request)
            self.ws.connect(
                "ws://localhost:5001",
                # using Authorization header:
                headers={"Authorization": f"Bearer {token}"},
                # using auth:
                # auth={"token": token},
            )
        self.ws_greenlet = gevent.spawn(self.ws.wait)
        self.ws.on("*", self.ws.on_message)
        self.ws.connect("ws://localhost:5001", wait_timeout=10)

    @task
    def my_task(self):
        self.ws.call("join_room", {"room": "room1"})
        # ...

    def on_stop(self) -> None:
        self.ws.disconnect()
