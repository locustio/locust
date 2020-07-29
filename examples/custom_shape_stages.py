from locust import HttpUser, TaskSet, task, constant
from locust import StagesShaper


class UserTasks(TaskSet):
    @task
    def one(self):
        self.client.get("/one")

    @task
    def two(self):
        self.client.get("/two")

    @task
    def three(self):
        self.client.get("/three")


class WebsiteUser(HttpUser):
    wait_time = constant(0.5)
    tasks = [UserTasks]


class myShape(StagesShaper):
    def __init__(self):
        self.stages = [
            {'duration': 60, 'users': 10, 'hatch_rate': 10, 'stop': False},
            {'duration': 80, 'users': 30, 'hatch_rate': 10, 'stop': False},
            {'duration': 100, 'users': 50, 'hatch_rate': 10, 'stop': False},
            {'duration': 120, 'users': 70, 'hatch_rate': 10, 'stop': False},
            {'duration': 180, 'users': 100, 'hatch_rate': 10, 'stop': False},
            {'duration': 300, 'users': 10, 'hatch_rate': 10, 'stop': False},
            {'duration': 320, 'users': 5, 'hatch_rate': 10, 'stop': False},
            {'duration': 360, 'users': 1, 'hatch_rate': 1, 'stop': True},
        ]
