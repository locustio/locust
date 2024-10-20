"""
This shows some useful ways to validate responses and how to exit tasks early on failure.
"""

from locust import FastHttpUser, events, run_single_user, task
from locust.exception import RescheduleTask


class BadUser(FastHttpUser):
    @task
    def t(self):
        self.client.request("POST", "/authenticate", json={"username": "foo", "password": "bar"})
        # ...
        self.client.request("POST", "/checkout/confirm", json={"foo": "bar"})


class GoodUser(FastHttpUser):
    @task
    def t(self):
        with self.rest("POST", "/authenticate", json={"username": "foo", "password": "bar"}) as resp:
            # check if there was an error field in the response:
            if error := resp.js.get("error"):
                resp.failure(error)
            # to be even more sure things went well, lets validate a success criteria:
            elif message := resp.js.get("message"):
                if message != "Welcome foo!":
                    resp.failure(f"Wrong welcome message: {message}")
        # ...
        # If you have long flows and can't be bothered to add validations
        # for each step then at least do it for the final step:
        with self.rest("POST", "/checkout/confirm", json={"foo": "bar"}) as resp:
            if not resp.js.get("orderId"):
                resp.failure("orderId missing")


# Break tasks early if there is a failed request
@events.init.add_listener
def register_request_listener(environment, **kwargs):
    @events.request.add_listener
    def request(exception, **kwargs):
        if exception:
            raise RescheduleTask()


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
    run_single_user(GoodUser)
