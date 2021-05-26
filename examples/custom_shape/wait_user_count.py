from collections import namedtuple
import math
import time
import random

from locust import HttpUser, TaskSet, task, constant
from locust import LoadTestShape


class UserTasks(TaskSet):
    @task
    def get_root(self):
        self.client.get("/")


class WebsiteUser(HttpUser):
    wait_time = constant(0.5)
    tasks = [UserTasks]

    def __init__(self, *args, **kwargs):
        # we arbitrarily make the users very slow to create, and also
        # unpredictably slow. One way this might happen in real use cases is if
        # the User has a slow initialization for gathering data to randomly
        # select.
        time.sleep(random.randint(0, 5))
        super(WebsiteUser, self).__init__(*args, **kwargs)


Step = namedtuple("Step", ["users", "dwell"])


class StepLoadShape(LoadTestShape):
    """
    A step load shape that waits until the target user count has
    been reached before waiting on a per-step timer.

    The purpose here is to ensure that a target number of users is always reached,
    regardless of how slow the user spawn rate is. The dwell time is there to
    observe the steady state at that number of users.

    Keyword arguments:

        targets_with_times -- iterable of 2-tuples, with the desired user count first,
            and the dwell (hold) time with that user count second

    """

    targets_with_times = (Step(10, 10), Step(20, 15), Step(10, 10))

    def __init__(self, *args, **kwargs):
        self.step = 0
        self.time_active = False
        super(StepLoadShape, self).__init__(*args, **kwargs)

    def tick(self):
        if self.step >= len(self.targets_with_times):
            return None

        target = self.targets_with_times[self.step]
        users = self.get_current_user_count()

        if target.users == users:
            if not self.time_active:
                self.reset_time()
                self.time_active = True
            run_time = self.get_run_time()
            if run_time > target.dwell:
                self.step += 1
                self.time_active = False

        # Spawn rate is the second value here. It is not relevant because we are
        # rate-limited by the User init rate.  We set it arbitrarily high, which
        # means "spawn as fast as you can"
        return (target.users, 100)
