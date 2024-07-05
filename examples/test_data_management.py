# This example shows the various ways to run things before/outside of the normal task execution flow,
# which is very useful for fetching test data.
#
# 1. Locustfile parse time
# 2. Locust start (init)
# 3. Test start
# 4. User start
# 5. Inside a task
# M1. CPU & memory usage
# M2. master sent heartbeat to worker 1-N
# M3. worker 1-N received heartbeat from master
# (M* are repeated as long as locust is running)
# ...
# 6. Test run stopping
# 7. User stop
# 8. Test run stop
# (3-8 are repeated if you restart the test in the UI)
# 9. Locust quitting
# 10. Locust quit
#
# try it out by running:
#  locust -f test_data_management.py --headless -u 2 -t 5 --processes 2
from __future__ import annotations

from locust import HttpUser, events, task
from locust.env import Environment
from locust.runners import MasterRunner
from locust.user.wait_time import constant

import datetime
from typing import Any

import requests


def timestring() -> str:
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%m:%S.%f")[:-5]


print("1. Parsing locustfile, happens before anything else")

# If you want to get something over HTTP at this time you can use `requests` directly:
global_test_data = requests.post(
    "https://postman-echo.com/post",
    data="global_test_data_" + timestring(),
).json()["data"]

test_run_specific_data = None


@events.init.add_listener
def init(environment: Environment, **_kwargs: Any) -> None:
    print("2. Initializing locust, happens after parsing the locustfile but before test start")


@events.quitting.add_listener
def quitting(environment: Environment, **_kwargs: Any) -> None:
    print("9. locust is about to shut down")


@events.test_start.add_listener
def test_start(environment: Environment, **_kwargs) -> None:
    # happens only once in headless runs, but can happen multiple times in web ui-runs
    global test_run_specific_data
    print("3. Starting test run")
    # in a distributed run, the master does not typically need any test data
    if not isinstance(environment.runner, MasterRunner):
        test_run_specific_data = requests.post(
            "https://postman-echo.com/post",
            data="test-run-specific_" + timestring(),
        ).json()["data"]


@events.heartbeat_sent.add_listener
def heartbeat_sent(client_id: str, timestamp: float) -> None:
    print(f"M2. master sent heartbeat to worker {client_id} at {datetime.datetime.fromtimestamp(timestamp)}")


@events.heartbeat_received.add_listener
def heartbeat_received(client_id: str, timestamp: float) -> None:
    print(f"M3. worker {client_id} received heartbeat from master at {datetime.datetime.fromtimestamp(timestamp)}")


@events.usage_monitor.add_listener
def usage_monitor(environment: Environment, cpu_usage: float, memory_usage: int) -> None:
    # convert from bytes to Mebibytes
    memory_usage = memory_usage / 1024 / 1024
    print(f"M1. {environment.runner.__class__.__name__}: cpu={cpu_usage}%, memory={memory_usage}M")


@events.quit.add_listener
def quit(exit_code: int, **kwargs: Any) -> None:
    print(f"10. Locust has shut down with code {exit_code}")


@events.test_stopping.add_listener
def test_stopping(environment: Environment, **_kwargs: Any) -> None:
    print("6. stopping test run")


@events.test_stop.add_listener
def test_stop(environment: Environment, **_kwargs: Any) -> None:
    print("8. test run stopped")


class MyUser(HttpUser):
    host = "https://postman-echo.com"
    wait_time = constant(180)  # be nice to postman-echo
    first_start = True

    def on_start(self) -> None:
        if MyUser.first_start:
            MyUser.first_start = False
            # This is useful for similar things as to test_start, but happens in the context of a User
            # In the case of a distributed run, this would be run once per worker.
            # It will not be re-run on repeated runs (unless you clear the first_start flag)
            print("X. Here's where you would put things you want to run the first time a User is started")

        print("4. A user was started")
        # This is a good place to fetch user-specific test data. It is executed once per User
        # If you do not want the request logged, you can replace self.client.<method> with requests.<method>
        self.user_specific_testdata = self.client.post(
            "https://postman-echo.com/post",
            data="user-specific_" + timestring(),
        ).json()["data"]

    @task
    def t(self) -> None:
        self.client.get(f"/get?{global_test_data}")
        self.client.get(f"/get?{test_run_specific_data}")
        self.client.get(f"/get?{self.user_specific_testdata}")

        print("5. Getting task-run-specific testdata")
        # If every iteration is meant to use new test data this is the most common way to do it
        task_run_specific_testdata = self.client.post(
            "https://postman-echo.com/post",
            data="task_run_specific_testdata_" + timestring(),
        ).json()["data"]
        self.client.get(f"/get?{task_run_specific_testdata}")

    def on_stop(self) -> None:
        # this is a good place to clean up/release any user-specific test data
        print("7. a user was stopped")
