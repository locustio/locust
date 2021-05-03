"""
Example of a manual_report() function that can be used either as a context manager
(with statement), or a decorator, to manually add entries to Locust's statistics.

Usage as a context manager:

    with manual_report("stats entry name"):
        # Run time of this block will be reported under a stats entry called "stats entry name"
        # do stuff here, if an Exception is raised, it'll be reported as a failure

Usage as a decorator:

    @task
    @manual_report
    def my_task(self):
       # The run time of this task will be reported under a stats entry called "my task" (type "manual").
       # If an Exception is raised, it'll be reported as a failure
"""

import random
from contextlib import contextmanager, ContextDecorator
from time import time, sleep

from locust import User, task, constant, events


@contextmanager
def _manual_report(name):
    start_time = time()
    try:
        yield
    except Exception as e:
        events.request.fire(
            request_type="manual",
            name=name,
            response_time=(time() - start_time) * 1000,
            response_length=0,
            exception=e,
        )
        raise
    else:
        events.request.fire(
            request_type="manual",
            name=name,
            response_time=(time() - start_time) * 1000,
            response_length=0,
            exception=None,
        )


def manual_report(name_or_func):
    if callable(name_or_func):
        # used as decorator without name argument specified
        return _manual_report(name_or_func.__name__)(name_or_func)
    else:
        return _manual_report(name_or_func)


class MyUser(User):
    wait_time = constant(1)

    @task
    def successful_task(self):
        with manual_report("successful_task"):
            sleep(random.random())

    @task
    @manual_report
    def decorator_test(self):
        if random.random() > 0.5:
            raise Exception("decorator_task failed")
        sleep(random.random())

    @task
    def failing_task(self):
        with manual_report("failing_task"):
            sleep(random.random())
            raise Exception("Oh nooes!")
