from __future__ import annotations
from math import trunc

from locust import HttpUser, User, task, constant
from locust import LoadTestShape


class BaseUser(HttpUser):
    abstract = True

    @task
    def get_root(self):
        self.client.get("/")


users: list[type[User]] = []


class GeneratorShape(LoadTestShape):
    """
    A load shappe generating its user class from the time.
    """

    def get_user(self, index: int) -> type[HttpUser]:
        if index >= len(users):
            user = self.runner.register_user(f"User{index}", (HttpUser,), {"wait_time": constant(index * 0.1)})
            users.append(user)
        return users[index]

    def tick(self):
        index = trunc(self.get_run_time())
        if index >= 2:
            return None
        return (index + 1, 1, [self.get_user(index)])
