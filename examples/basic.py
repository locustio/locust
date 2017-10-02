from locust import WebLocust, TaskSet, task


def index(l):
    l.client.http.get("/")

def stats(l):
    l.client.http.get("/stats/requests")

class UserTasks(TaskSet):
    # one can specify tasks like this
    tasks = [index, stats]

    # but it might be convenient to use the @task decorator
    @task
    def page404(self):
        self.client.http.get("/does_not_exist")

class WebsiteUser(WebLocust):
    """
    Locust user class that does requests to the locust web server running on localhost
    """
    host = "http://127.0.0.1:8089"
    min_wait = 2000
    max_wait = 5000
    task_set = UserTasks
