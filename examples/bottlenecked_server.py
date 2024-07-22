"""
This example uses extensions in Locust's own WebUI to simulate a bottlenecked server and runs a test against itself.

The purpose of this is mainly to generate nice graphs in the UI to teach new users how to interpret load test results.

See https://docs.locust.io/en/stable/quickstart.html#locust-s-web-interface
"""

from locust import HttpUser, constant_pacing, events, run_single_user, task

import time
from datetime import datetime
from threading import Semaphore

# Only allow up to 4 concurrent requests. Similar to how a web or backend server with 4 threads might behave.
sema = Semaphore(4)


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"

    @task
    def index(l):
        l.client.get("/fast")
        l.client.get("/slow")


# class fWebsiteUser(HttpUser):
#     host = "http://127.0.0.1:8089"
#     wait_time = constant_pacing(5)

#     @task
#     def index(l):
#         l.client.get("/fast")


# class sWebsiteUser(HttpUser):
#     host = "http://127.0.0.1:8089"
#     wait_time = constant_pacing(5)

#     @task
#     def index(l):
#         l.client.get("/slow")


# class feWebsiteUser(HttpUser):
#     host = "http://127.0.0.1:8089"
#     wait_time = constant_pacing(5)

#     @task
#     def index(l):
#         l.client.get("/fast_except_every_5_minutes")


@events.init.add_listener
def locust_init(environment, **kwargs):
    assert environment.web_ui, "you can't run this headless"

    @environment.web_ui.app.route("/slow")
    def slow():
        with sema:  # only 10 requests can hold this lock at the same time
            time.sleep(1)  # pretend each request takes 1 second to execute
        return "slow"

    @environment.web_ui.app.route("/fast")
    def fast():
        time.sleep(0.1)
        return "fast"

    # Simulate unstable response times. In real life they could, for example, be caused by scheduled db jobs
    @environment.web_ui.app.route("/fast_except_every_5_minutes")
    def fast_except_every_5_minutes():
        if datetime.now().minute % 5 == 0:
            time.sleep(1)
            return "slow"
        else:
            time.sleep(0.1)
            return "fast"


# example: locust -f examples/bottlenecked_server.py --print-stats -u 20 -r 0.2 --autostart --run-time 5m
