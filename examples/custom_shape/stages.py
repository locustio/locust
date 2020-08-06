from locust import HttpUser, TaskSet, task, constant
from locust import LoadTestShape


class UserTasks(TaskSet):
    @task
    def get_root(self):
        self.client.get("/")


class WebsiteUser(HttpUser):
    wait_time = constant(0.5)
    tasks = [UserTasks]


class StagesShape(LoadTestShape):
    """
    A simply load test shape class that has different user and hatch_rate at
    different stages.

    Keyword arguments:

        stages -- A list of dicts, each representing a stage with the following keys:
            duration -- When this many seconds pass the test is advanced to the next stage
            users -- Total user count
            hatch_rate -- Hatch rate
            stop -- A boolean that can stop that test at a specific stage

        stop_at_end -- Can be set to stop once all stages have run.
    """
    def __init__(self,
            stages=[
                {'duration': 60, 'users': 10, 'hatch_rate': 10},
                {'duration': 80, 'users': 30, 'hatch_rate': 10},
                {'duration': 100, 'users': 50, 'hatch_rate': 10},
                {'duration': 120, 'users': 70, 'hatch_rate': 10},
                {'duration': 180, 'users': 100, 'hatch_rate': 10},
                {'duration': 220, 'users': 10, 'hatch_rate': 10},
                {'duration': 230, 'users': 5, 'hatch_rate': 10},
                {'duration': 240, 'users': 1, 'hatch_rate': 1},
            ],
            stop_at_end=True
            ):
        self.stages = sorted(stages, key=lambda k: k["duration"])
        self.stop_at_end = stop_at_end

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["hatch_rate"], stage.get('stop', False))
                self.last_stage = tick_data
                return tick_data

        if self.stop_at_end:
            return (0, 0, True)
        else:
            return self.last_stage
