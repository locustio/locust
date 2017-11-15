import os

from locust import HttpLocust, TaskSet, task
from locust.clients import HttpSession

class MultipleHostsLocust(HttpLocust):
    abstract = True
    
    def __init__(self, *args, **kwargs):
        super(MultipleHostsLocust, self).__init__(*args, **kwargs)
        self.api_client = HttpSession(base_url=os.environ["API_HOST"])
    

class UserTasks(TaskSet):
    # but it might be convenient to use the @task decorator
    @task
    def index(self):
        self.locust.client.get("/")
    
    @task
    def index_other_host(self):
        self.locust.api_client.get("/stats/requests")
    
class WebsiteUser(MultipleHostsLocust):
    """
    Locust user class that does requests to the locust web server running on localhost
    """
    host = "http://127.0.0.1:8089"
    min_wait = 2000
    max_wait = 5000
    task_set = UserTasks
