
"""This is a mock locust file for unit testing"""

from locust import HttpUser, TaskSet, task, between


def index(l):
    l.client.get("/")

def stats(l):
    l.client.get("/stats/requests")


class UserTasks(TaskSet):
    # one can specify tasks like this
    tasks = [index, stats]


class UserSubclass(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    tasks = [UserTasks]


class NotUserSubclass():
    host = "http://localhost:8000"

