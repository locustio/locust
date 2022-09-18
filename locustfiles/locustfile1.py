from locust import HttpUser, task, between, events


class Base(HttpUser):
    wait_time = between(1, 2)

    @task
    def base(self):
        self.client.get("/")
