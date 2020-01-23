import random
from time import time
from locust import runners
import logging


def between(min_wait, max_wait):
    """
    Returns a function that will return a random number between min_wait and max_wait.
    
    Example::
    
        class User(Locust):
            # wait between 3.0 and 10.5 seconds after each task
            wait_time = between(3.0, 10.5)
    """
    return lambda instance: min_wait + random.random() * (max_wait - min_wait)


def constant(wait_time):
    """
    Returns a function that just returns the number specified by the wait_time argument
    
    Example::
    
        class User(Locust):
            wait_time = constant(3)
    """
    return lambda instance: wait_time


def constant_pacing(wait_time):
    """
    Returns a function that will track the run time of the tasks, and for each time it's 
    called it will return a wait time that will try to make the total time between task 
    execution equal to the time specified by the wait_time argument. 
    
    In the following example the task will always be executed once every second, no matter 
    the task execution time::
    
        class User(Locust):
            wait_time = constant_pacing(1)
            class task_set(TaskSet):
                @task
                def my_task(self):
                    time.sleep(random.random())
    
    If a task execution exceeds the specified wait_time, the wait will be 0 before starting 
    the next task.
    """
    def wait_time_func(self):
        if not hasattr(self, "_cp_last_run"):
            self._cp_last_wait_time = wait_time
            self._cp_last_run = time()
            return wait_time
        else:
            run_time = time() - self._cp_last_run - self._cp_last_wait_time
            self._cp_last_wait_time = max(0, wait_time - run_time)
            self._cp_last_run = time()
            return self._cp_last_wait_time
    return wait_time_func


def constant_rps(rps):
    """
    This behaves exactly the same as constant_pacing but with an inverted parameter.
    It takes requests per second as a parameter instead of time between requests.
    """

    return constant_pacing(1 / rps)


def constant_rps_total(rps):
    """
    Returns a function that will track the run time of all tasks in this locust process, 
    and for each time it's called it will return a wait time that will try to make the 
    execution equal to the time specified by the wait_time argument. 
    
    This is similar to constant_rps, but looks at all clients/locusts in a locust process.

    Note that in a distributed run, the RPS limit is applied per-slave, not globally.

    During rampup, the RPS is intentionally constrained to be the requested rps * the share of running clients.

    Will output a warning if RPS target is missed twice in a row
    """

    def wait_time_func(self):
        lr = runners.locust_runner
        if not lr:
            logging.warning(
                "You asked for constant total rps, but you seem to be running a locust directly. Hopefully you are only running one locust, in which case this will give a somewhat reasonable estimate."
            )
            return 1 / rps
        current_time = float(time())
        unstarted_clients = lr.num_clients - len(lr.locusts)
        if not hasattr(self, "_cp_last_run"):
            self._cp_last_run = 0
            self._cp_target_missed = False
        next_time = self._cp_last_run + (lr.num_clients + unstarted_clients) / rps
        if current_time > next_time:
            if lr.state == runners.STATE_RUNNING and self._cp_target_missed and not lr.rps_warning_emitted:
                logging.warning("Failed to reach target rps, even after rampup has finished")
                lr.rps_warning_emitted = True  # stop logging
            self._cp_target_missed = True
            self._cp_last_run = current_time
            return 0
        self._cp_target_missed = False
        self._cp_last_run = next_time
        return next_time - current_time

    return wait_time_func
