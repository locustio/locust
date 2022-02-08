import time
from locust import HttpUser, task, between, tag


class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    @tag('hello')
    @task
    def hello_world(self):
        print("TAG HELLO")
        self.client.get("/hello")
        self.client.get("/world")
    @tag('view')
    @task(3)
    def view(self):
        print("TAG VIEW")
        self.client.get("/view")
        self.client.get("/fromhere")

#    def on_start(self):
#        self.client.post("/login", json={"username": "foo", "password": "bar"})
