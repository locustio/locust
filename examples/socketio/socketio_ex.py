from locust import HttpUser, task
from locust.contrib.socketio import SocketIOUser

from threading import Event

import gevent
from socketio import Client


class MySIOHttpUser(SocketIOUser, HttpUser):
    options = {
        # "logger": True,
        # "engineio_logger": True,
    }
    event: Event

    def on_start(self) -> None:
        self.sio.connect("ws://localhost:5001", wait_timeout=10)
        self.sio_greenlet = gevent.spawn(self.sio.wait)
        # If you need authorization, here's how to do it:
        # resp = self.client.post("/login", json={"username": "foo", "password": "bar"})
        # token = resp.json()["access_token"]
        # self.sio.connect(
        #     "ws://localhost:5001",
        #     # Option 1: using Authorization header:
        #     headers={"Authorization": f"Bearer {token}"},
        #     # Option 2: using auth:
        #     # auth={"token": token},
        # )

    @task
    def my_task(self):
        self.event = Event()
        # Send message and wait for confirmation
        self.sio.call("join_room", {"room": "room1"})
        # Register an event handler
        self.sio.on("chat_message", self.on_chat_message)
        # Use socketio.Client to send a message that wont be logged as a request
        Client.call(self.sio, "send_message", {"room": "room1", "message": "foo"})
        # Emit doesnt wait for confirmation
        self.sio.emit("send_message", {"room": "room1", "message": "bar"})
        self.event.wait()  # wait for on_chat_message to set this event
        self.sio.call("leave_room", {"room": "room1"})
        # We've used multiple inheritance to combine this with HttpUser, so we can also make normal HTTP requests
        self.client.get("/")

    def on_chat_message(self, event: str, data: str) -> None:
        if data.startswith("bar"):
            self.event.set()
        self.sio.on_message(event, data)

    def on_stop(self) -> None:
        self.sio.disconnect()
