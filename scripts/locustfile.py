import math

from locust import HttpUser, task, constant
from locust import LoadTestShape


class UserA(HttpUser):
    wait_time = constant(600)

    # host = "https://example.com"

    @task
    def get_root(self):
        self.client.get("/", name="UserA")


class UserB(HttpUser):
    wait_time = constant(600)

    # host = "https://example.com"

    @task
    def get_root(self):
        self.client.get("/", name="UserB")


class UserC(HttpUser):
    wait_time = constant(600)

    # host = "https://example.com"

    @task
    def get_root(self):
        self.client.get("/", name="UserC")


# class StepLoadShape(LoadTestShape):
#     step_time = 30
#     step_load = 10
#     spawn_rate = 1
#     time_limit = 300
#
#     def tick(self):
#         run_time = self.get_run_time()
#
#         if run_time > self.time_limit:
#             return None
#
#         current_step = math.floor(run_time / self.step_time) + 1
#         return current_step * self.step_load, self.spawn_rate


class RampUpThenDownLoadShape(LoadTestShape):
    stages = [
        {"duration": 5, "users": 1, "spawn_rate": 1},
        {"duration": 35, "users": 30, "spawn_rate": 1},
        {"duration": 35, "users": 1, "spawn_rate": 1},
        {"duration": 35, "users": 73, "spawn_rate": 6},
        {"duration": 35, "users": 1, "spawn_rate": 6},
        {"duration": 35, "users": 153, "spawn_rate": 17},
        {"duration": 10, "users": 145, "spawn_rate": 1},
        {"duration": 60, "users": 130, "spawn_rate": 0.25},
        {"duration": 15, "users": 50, "spawn_rate": 25},
        {"duration": 20, "users": 1, "spawn_rate": 5},
    ]

    for previous_stage, stage in zip(stages[:-1], stages[1:]):
        stage["duration"] += previous_stage["duration"]

    for previous_stage, stage in zip(stages[:-1], stages[1:]):
        assert stage["duration"] > previous_stage["duration"]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None
