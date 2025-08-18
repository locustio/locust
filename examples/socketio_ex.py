from locust import run_single_user, task
from locust.contrib.socketio import SocketIOUser

from threading import Event


class MyUser(SocketIOUser):
    options = {
        # "logger": True,
        # "engineio_logger": True,
    }
    event: Event

    def on_start(self) -> None:
        self.client.connect("ws://localhost:5001", wait_timeout=10)

    def on_stop(self):
        self.client.disconnect()

    @task
    def my_task(self):
        self.event = Event()
        self.call("join_room", {"room": "room1"})
        self.call("send_message", {"room": "room1", "message": "Message 1"})
        self.emit("send_message", {"room": "room1", "message": "Message 2, Sent without waiting for response"})
        self.event.wait()  # wait for on_message to set this event
        self.call("leave_room", {"room": "room1"})

    def on_message(self, event, data: str) -> None:
        if event == "chat_message" and data.startswith("Message 2,"):
            self.event.set()
        super().on_message(event, data)


if __name__ == "__main__":
    run_single_user(MyUser)
