import random
from locust import HttpUser, task, between


class MyUser(HttpUser):
    @task
    def index(self):
        self.client.get("/hello")
        self.client.get("/world")

    @task(3)
    def view_item(self):
        item_id = random.randint(1, 10000)
        self.client.get(f"/item?id={item_id}", name="/item")

    def on_start(self):
        self.client.post("/login", {"username": "foo", "password": "bar"})

    wait_time = between(5, 9)
