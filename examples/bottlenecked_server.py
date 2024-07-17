"""
This example uses extensions in Locust's own WebUI to simulate a bottlenecked server and runs a test against itself.

The purpose of this is mainly to generate nice graphs in the UI to teach new users how to interpret load test results.

See https://docs.locust.io/en/stable/quickstart.html#locust-s-web-interface
"""

from locust import HttpUser, events, run_single_user, task

import time
from threading import Semaphore

# Only allow up to 10 concurrent requests. Similar to how a server with 10 threads might behave.
sema = Semaphore(10)


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"

    @task
    def index(l):
        l.client.get("/slow")


@events.init.add_listener
def locust_init(environment, **kwargs):
    assert environment.web_ui, "you can't run this headless"

    @environment.web_ui.app.route("/slow")
    def my_added_page():
        with sema:  # only 10 requests can hold this lock at the same time
            time.sleep(1)  # pretend each request takes 1 second to execute
        return "Another page"


if __name__ == "__main__":
    run_single_user(WebsiteUser)
