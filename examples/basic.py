from locust import Locust, task
import random

def login(l):
    l.client.post("/login", {"userid":random.randint(0,10000)})

def index(l):
    l.client.get("/")

def stats(l):
    l.client.get("/stats/requests")

def profile(l):
    l.client.get("/profile")

class WebsiteUser(Locust):
    host = "http://127.0.0.1:8089"
    #tasks = [(index, 2), (profile, 1)]
    tasks = [index, stats]
    min_wait=2000
    max_wait=5000
    
    @task
    def page404(self):
        self.client.get("/does_not_exist")
