# This example shows the various ways to run things before/outside of the normal task execution flow,
# which is very useful for fetching test data.
#
# 1. Locustfile parse time
# 2. Locust start
# 3. Test start
# 4. User start
# 5. Inside a task
# ...
# 6. User stop
# 7. Test run stop
# 8. (not shown in this example) Locust quit
#
# try it out by running:
#  locust -f test_data_management.py --headless -u 2 -t 5
from locust.user.wait_time import constant
from locust import HttpUser, task
from locust import events
from locust.runners import MasterRunner
import requests
import datetime


def timestring():
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
def _(environment, **_kwargs):
    print("2. Initializing locust, happens after parsing the locustfile but before test start")


@events.quitting.add_listener
def _(environment, **_kwargs):
    print("locust is shutting down")


@events.test_start.add_listener
def _(environment, **_kwargs):
    # happens only once in headless runs, but can happen multiple times in web ui-runs
    global test_run_specific_data
    print("3. Starting test run")
    # in a distributed run, the master does not typically need any test data
    if not isinstance(environment.runner, MasterRunner):
        test_run_specific_data = requests.post(
            "https://postman-echo.com/post",
            data="test-run-specific_" + timestring(),
        ).json()["data"]


@events.test_stop.add_listener
def _(environment, **_kwargs):
    print("stopping test run")


class MyUser(HttpUser):
    host = "https://postman-echo.com"
    wait_time = constant(180)  # be nice to postman-echo

    def on_start(self):
        print("4. A user was started")
        # This is a good place to fetch user-specific test data. It is executed once per User
        # If you do not want the request logged, you can replace self.client.<method> with requests.<method>
        self.user_specific_testdata = self.client.post(
            "https://postman-echo.com/post",
            data="user-specific_" + timestring(),
        ).json()["data"]

    @task
    def t(self):
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

    def on_stop(self):
        # this is a good place to clean up/release any user-specific test data
        print("a user was stopped")
