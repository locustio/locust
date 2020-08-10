import math
from locust import HttpUser, TaskSet, task, constant
from locust import LoadTestShape


class UserTasks(TaskSet):
    @task
    def get_root(self):
        self.client.get("/")


class WebsiteUser(HttpUser):
    wait_time = constant(0.5)
    tasks = [UserTasks]


class DoubleWave(LoadTestShape):
    """
    A shape to immitate some specific user behaviour. In this example, midday
    and evening meal times.

    Settings:

        min_users -- minimum users
        peak_one_users -- users in first peak
        peak_two_users -- users in second peak
        time_limit -- total length of test

    """
    min_users = 20
    peak_one_users = 60
    peak_two_users = 40
    time_limit = 600

    def __init__(self):
        self.first_peak_time = round(self.time_limit / 3)
        self.second_peak_time = round(self.first_peak_time * 2)

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.time_limit:
            user_count = (self.peak_one_users - self.min_users) * math.e ** -((run_time/(math.sqrt(self.time_limit)*2))-4) ** 2
            + (self.peak_two_users - self.min_users) * math.e ** -((run_time/(math.sqrt(self.time_limit)*2))-8) ** 2
            + self.min_users

            return (round(user_count), round(user_count), False)
        else:
            return (0, 0, True)
