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


class StepLoadShape(LoadTestShape):
    '''
    A step load shape

    Arguments:

        step_time - Time between steps
        step_load - User increase amount at each step
        hatch_rate - Hatch rate to use at every step
        time_limit - Time limit in seconds
    '''
    def __init__(self,
            step_time=30,
            step_load=10,
            hatch_rate=10,
            time_limit=600
        ):
        self.step_time = step_time
        self.step_load = step_load
        self.hatch_rate = hatch_rate
        self.time_limit = time_limit

    def tick(self):
        run_time = self.get_run_time()
        current_step = math.floor(run_time / self.step_time) + 1
        return (current_step * self.step_load, self.hatch_rate, run_time > self.time_limit)
