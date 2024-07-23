"""
This example uses extensions in Locust's own WebUI to simulate a bottlenecked server and runs a test against itself.

The purpose of this is mainly to generate nice graphs in the UI to teach new users how to interpret load test results.

See https://docs.locust.io/en/stable/quickstart.html#locust-s-web-interface
"""

from locust import HttpUser, constant, events, run_single_user, task

import time
from datetime import datetime
from threading import Semaphore

active_requests = 0
# Only allow up to 10 concurrent requests. Similar to how a web or backend server with 10 threads might behave.
sema = Semaphore(50)


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = constant(1)

    @task
    def index(l):
        l.client.get("/slow")


@events.init.add_listener
def locust_init(environment, **kwargs):
    assert environment.web_ui, "you can't run this headless"

    @environment.web_ui.app.route("/slow")
    def slow():
        global active_requests
        active_requests += 1
        with sema:
            # simulate a situation where concurrent requests beyond a certain level add overhead and make
            # even individual requests slower than if they were run at a reasonable load (for example if a system runs out of memory and starts swapping, or where managing the queue of requests starts taking a lot of CPU, or a DB with "hot rows" where lock synchronization gets harder and harder)
            if active_requests < 300:
                time.sleep(1)
            elif active_requests < 400:
                time.sleep(3)
            elif active_requests < 450:
                time.sleep(5)
            else:
                time.sleep(5)
                active_requests -= 1
                return "ERRORRRRR", 500
        active_requests -= 1
        return "OK"


# example: -u 500 -r 4
