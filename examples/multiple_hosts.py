import os

from locust import HttpUser, TaskSet, task, between
from locust.clients import HttpSession


class MultipleHostsUser(HttpUser):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_client = HttpSession(
            base_url=os.environ["API_HOST"], request_event=self.client.request_event, user=self
        )


class UserTasks(TaskSet):
    # but it might be convenient to use the @task decorator
    @task
    def index(self):
        self.user.client.get("/")

    @task
    def index_other_host(self):
        self.user.api_client.get("/stats/requests")


class WebsiteUser(MultipleHostsUser):
    """
    User class that does requests to the locust web server running on localhost
    """

    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    tasks = [UserTasks]
