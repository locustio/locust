from locust import HttpUser, events, task

from gevent.lock import Semaphore

all_users_spawned = Semaphore()
all_users_spawned.acquire()


@events.spawning_complete.add_listener
def on_spawning_complete(**kw):
    all_users_spawned.release()


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"

    def on_start(self):
        all_users_spawned.wait()

    @task
    def index(self):
        self.client.get("/")
