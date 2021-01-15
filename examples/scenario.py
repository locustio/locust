import math
from locust import HttpUser, TaskSet, task, constant, Scenario


class UserTasks(TaskSet):
    @task
    def get_root(self):
        self.client.get("/")


class AdminTasks(TaskSet):
    @task
    def get_root(self):
        self.client.get("/")


class WebsiteUser(HttpUser):
    wait_time = constant(0.5)
    tasks = [UserTasks]


class AdminUser(HttpUser):
    wait_time = constant(0.5)
    tasks = [UserTasks, AdminTasks]


class User(Scenario):
    name = "User only"
    users = [WebsiteUser]


class Admim(Scenario):
    name = "Admin only"
    users = [AdminUser]


class AdminAndUser(Scenario):
    name = "User and admin"
    users = [WebsiteUser, AdminUser]
