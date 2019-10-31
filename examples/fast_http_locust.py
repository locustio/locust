from locust import HttpLocust, TaskSet, task
from locust.contrib.fasthttp import FastHttpLocust


class UserTasks(TaskSet):
    @task
    def index(self):
        self.client.get("/")
    
    @task
    def stats(self):
        self.client.get("/stats/requests")

    
class WebsiteUser(FastHttpLocust):
    """
    Locust user class that does requests to the locust web server running on localhost,
    using the fast HTTP client
    """
    host = "http://127.0.0.1:8089"
    min_wait = 2000
    max_wait = 5000
    task_set = UserTasks

