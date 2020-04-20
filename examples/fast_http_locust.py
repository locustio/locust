from locust import HttpUser, TaskSet, task, between
from locust.contrib.fasthttp import FastHttpUser


class UserTasks(TaskSet):
    @task
    def index(self):
        self.client.get("/")
    
    @task
    def stats(self):
        self.client.get("/stats/requests")

    
class WebsiteUser(FastHttpUser):
    """
    User class that does requests to the locust web server running on localhost,
    using the fast HTTP client
    """
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    tasks = [UserTasks]

