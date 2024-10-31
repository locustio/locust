from locust import HttpUser, run_single_user, task

import random


class ForwardedForUser(HttpUser):
    subnet = "10.10."

    def __init__(self, environment):
        super().__init__(environment)
        self.fake_ip = self.subnet + str(random.randint(0, 254)) + "." + str(random.randint(0, 254))
        self.client.headers["X-Forwarded-For"] = self.fake_ip


class WebsiteUser(ForwardedForUser):
    @task
    def index(self):
        with self.client.get("/", catch_response=True) as resp:
            pass


if __name__ == "__main__":
    run_single_user(WebsiteUser)
