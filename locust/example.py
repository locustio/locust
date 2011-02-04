from locust import WebLocust, require_once
import random

def login(l):
    l.client.post("/login", {"userid":random.randint(0,10000)})

def index(l):
    l.client.get("/")

@require_once(login)
def profile(l):
    l.client.get("/profile")

class WebsiteUser(WebLocust):
    host = "http://127.0.0.1:6060"
    tasks = {index:2, profile:1}
    min_wait=2000
    max_wait=5000
