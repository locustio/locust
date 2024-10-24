"""
This shows an easy way to get testdata from a csv file into locust and use it for requests
"""

from locust import FastHttpUser, events, run_single_user, task

import csv
import os

csvfile = open(os.path.join(os.path.dirname(__file__), "testdata_from_csv.csv"))
iter = csv.reader(csvfile)


class DemoUser(FastHttpUser):
    @task
    def t(self):
        try:
            username, password = next(iter)
        except StopIteration:
            # go back to start of the file once its been exhausted
            csvfile.seek(0, 0)
            username, password = next(iter)
        with self.rest("POST", "/authenticate", json={"username": username, "password": password}) as resp:
            if message := resp.js and resp.js.get("message"):
                if not "Welcome" in message:
                    resp.failure(f"bad response: {message}")


# We'll now add endpoints to Locust's own WebUI to use as a target for the test.
# This means so you can't use headless or run_single_user, unless you also start a "headful" Locust instance.
#
# It is not very relevant to what this example is explaining, so feel free to ignore it.

FastHttpUser.host = "http://127.0.0.1:8089"

from flask import request


@events.init.add_listener
def locust_init(environment, **kwargs):
    if environment.web_ui:

        @environment.web_ui.app.route("/authenticate", methods=["POST"])
        def authenticate():
            username = request.get_json()["username"]
            return {"message": f"Welcome {username}!"}

        @environment.web_ui.app.route("/checkout/confirm", methods=["POST"])
        def checkout_confirm():
            foo = request.get_json()["foo"]
            return {"orderId": 42}


if __name__ == "__main__":
    run_single_user(DemoUser)
