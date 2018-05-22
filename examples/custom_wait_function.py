from locust import HttpLocust, TaskSet, task
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
    
class WebsiteUser(HttpLocust):
    """
    Locust user class that does requests to the locust web server running on localhost
    """
    host = "http://127.0.0.1:8089"
    # Most task inter-arrival times approximate to exponential distributions
    # We will model this wait time as exponentially distributed with a mean of 1 second
    wait_function = lambda self: random.expovariate(1)*1000 # *1000 to convert to milliseconds
    task_set = UserTasks

def strictExp(min_wait,max_wait,mu=1):
    """
    Returns an exponentially distributed time strictly between two bounds.
    """
    while True:
        x = random.expovariate(mu)
        increment = (max_wait-min_wait)/(mu*6.0)
        result = min_wait + (x*increment)
        if result<max_wait:
            break
    return result

class StrictWebsiteUser(HttpLocust):
    """
    Locust user class that makes exponential requests but strictly between two bounds.
    """
    host = "http://127.0.0.1:8089"
    wait_function = lambda self: strictExp(self.min_wait, self.max_wait)*1000
    task_set = UserTasks




