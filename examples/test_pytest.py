from locust.contrib.fasthttp import FastHttpSession

import time


def test_stuff(fastsession: FastHttpSession):  # session and fastsession are fixtures provided by Locust's pytest plugin
    resp = fastsession.get("https://locust.cloud/")

    # The next line will raise a requests.Exception if the request failed.
    # In Locust, the exception is ignored (and the function restarted), in pytest it will fail the test
    resp.raise_for_status()

    # catch_response works just like in regular locustfiles
    with fastsession.get("/", catch_response=True) as resp:
        if not resp.text or not "success" in resp.text:
            resp.failure("missing text in response")

    helper_function(fastsession)  # you can call helper functions as needed

    if fastsession.base_url:  # Set hostname with --host/-H to run this (works for both locust and pytest)
        fastsession.get("/")

    time.sleep(0.1)  # wait_time is not implemented in pytest, but you can use time.sleep() as needed


# This function doesn't have the test_ prefix/suffix and wont be detected as a test.
# Locust uses pytest's collection method, so it won't see it either.
def helper_function(fastsession: FastHttpSession):
    fastsession.get("https://locust.cloud/")
