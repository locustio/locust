from locust import HttpLocust, TaskSet, task, events, between

from gevent.lock import Semaphore

all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()

def on_hatch_complete(**kw):
    all_locusts_spawned.release()

events.hatch_complete += on_hatch_complete

class UserTasks(TaskSet):
    def on_start(self):
        all_locusts_spawned.wait()
        self.wait()
    
    @task
    def index(self):
        self.client.get("/")
    
class WebsiteUser(HttpLocust):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    task_set = UserTasks
