import random
import time

import gevent

from locust import HttpUser, task, between, events
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, STATE_HATCHING
from locust.result import RESULT_PASS, RESULT_WARN, RESULT_FAIL, set_result


class MyUser(HttpUser):
    @task
    def index(self):
        self.client.get("/hello")
        self.client.get("/world")

    @task(3)
    def view_item(self):
        item_id = random.randint(1, 10000)
        self.client.get(f"/item?id={item_id}", name="/item")

    def on_start(self):
        self.client.post("/login", {"username":"foo", "password":"bar"})

    wait_time = between(5, 9)


def _check_stats(environment, force_res):
    """Small demo setting predefined results based 'force_res' argument. Actual implementation should check stats values instead.

    e.g.: : if environment.runner.stats.total.fail_ratio > 0.2 ...
    """

    if environment.runner.state == STATE_HATCHING:
        # We don't check during hatching for the purpose of demo, but we normally would
        return

    if force_res == 1:
        set_result(environment.runner, RESULT_WARN, "Getting close to limit!")
        return RESULT_WARN

    if force_res == 2:
        set_result(
            environment.runner,
            RESULT_FAIL,
            "Limit exceeded by a large amount. This reason is too long, it will be truncated but you can mouse-over the result box to see it!",
        )
        return RESULT_FAIL

    if force_res > 2:
        set_result(environment.runner, RESULT_PASS, "Looking good.")
        return RESULT_PASS


def _checker_loop(environment):
    """Loop for checking stats during test."""
    ii = 0
    while not environment.runner.state in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
        time.sleep(2)

        res = _check_stats(environment, ii)
        if res == RESULT_FAIL:
            environment.runner.quit()

        ii += 1


@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    gevent.spawn(_checker_loop, environment)


@events.test_stop.add_listener
def on_test_stop(environment, **_kwargs):
    _check_stats(environment, 100)
