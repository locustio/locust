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

    Keyword arguments:

        min_users -- minimum users
        peak_one -- first peak size
        peak_two -- second peak size
        amplitude -- size of the test
        time_limit -- total length of test
    """
    def __init__(self, min_users=20, peak_one=1, peak_two=1.5, amplitude=150, time_limit=600):
        self.min_users = min_users
        self.peak_one = peak_one
        self.peak_two = peak_two
        self.amplitude = amplitude
        self.time_limit = time_limit

        self.first_peak_time = round(self.time_limit / 3)
        self.first_peak_users = round(self.peak_one * self.amplitude)
        self.second_peak_time = round(self.first_peak_time * 2)
        self.second_peak_users = round(self.peak_two * self.amplitude)

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.time_limit:
            user_count = self.second_peak_users * math.e ** -((run_time/(math.sqrt(self.time_limit)*2))-4) ** 2 + self.first_peak_users * math.e ** - ((run_time/(math.sqrt(self.time_limit)*2))-8) ** 2 + self.min_users
            return (round(user_count), round(user_count), False)
        else:
            return (0, 0, True)
