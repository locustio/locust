import random
from time import time


def between(min_wait, max_wait):
    """
    Returns a function that will return a random number between min_wait and max_wait.

    Example::

        class MyUser(User):
            # wait between 3.0 and 10.5 seconds after each task
            wait_time = between(3.0, 10.5)
    """
    return lambda instance: min_wait + random.random() * (max_wait - min_wait)


def constant(wait_time):
    """
    Returns a function that just returns the number specified by the wait_time argument

    Example::

        class MyUser(User):
            wait_time = constant(3)
    """
    return lambda instance: wait_time


def constant_pacing(wait_time):
    """
    Returns a function that will track the run time of the tasks, and for each time it's
    called it will return a wait time that will try to make the total time between task
    execution equal to the time specified by the wait_time argument.

    In the following example the task will always be executed once every 10 seconds, no matter
    the task execution time::

        class MyUser(User):
            wait_time = constant_pacing(10)
            @task
            def my_task(self):
                time.sleep(random.random())

    If a task execution exceeds the specified wait_time, the wait will be 0 before starting
    the next task.
    """

    def wait_time_func(self):
        if not hasattr(self, "_cp_last_wait_time"):
            self._cp_last_wait_time = 0
        run_time = time() - self._cp_last_run - self._cp_last_wait_time
        self._cp_last_wait_time = max(0, wait_time - run_time)
        self._cp_last_run = time()
        return self._cp_last_wait_time

    return wait_time_func


def constant_throughput(task_runs_per_second):
    """
    Returns a function that will track the run time of the tasks, and for each time it's
    called it will return a wait time that will try to make the number of task runs per second
    execution equal to the time specified by the task_runs_per_second argument.

    If you have multiple requests in a task your RPS will of course be higher than the
    specified throughput.

    This is the mathematical inverse of constant_pacing.

    In the following example the task will always be executed once every 10 seconds, no matter
    the task execution time::

        class MyUser(User):
            wait_time = constant_throughput(0.1)
            @task
            def my_task(self):
                time.sleep(random.random())

    If a task execution exceeds the specified wait_time, the wait will be 0 before starting
    the next task.
    """
    return constant_pacing(1 / task_runs_per_second)
