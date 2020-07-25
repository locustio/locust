from locust import HttpUser, TaskSet, task
import random


def index(l):
    l.client.get("/")


def stats(l):
    l.client.get("/stats/requests")


class UserTasks(TaskSet):
    # one can specify tasks like this
    tasks = [index, stats]

    # but it might be convenient to use the @task decorator
    @task
    def page404(self):
        self.client.get("/does_not_exist")


class WebsiteUser(HttpUser):
    """
    User class that does requests to the locust web server running on localhost
    """

    host = "http://127.0.0.1:8089"
    # Most task inter-arrival times approximate to exponential distributions
    # We will model this wait time as exponentially distributed with a mean of 1 second
    wait_time = lambda self: random.expovariate(1)
    tasks = [UserTasks]


def strictExp(min_wait, max_wait, mu=1):
    """
    Returns an exponentially distributed time strictly between two bounds.
    """
    while True:
        x = random.expovariate(mu)
        increment = (max_wait - min_wait) / (mu * 6.0)
        result = min_wait + (x * increment)
        if result < max_wait:
            break
    return result


class StrictWebsiteUser(HttpUser):
    """
    User class that makes exponential requests but strictly between two bounds.
    """

    host = "http://127.0.0.1:8089"
    wait_time = lambda self: strictExp(3, 7)
    tasks = [UserTasks]
