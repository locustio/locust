from locust.contrib.fasthttp import FastHttpSession

import time


# pytest will automatically discover any functions prefixed with "test_" as test cases
# session and fastsession are pytest fixtures provided by Locust's pytest plugin
def test_stuff(fastsession: FastHttpSession):
    resp = fastsession.get("https://locust.cloud/")

    # In Locust, standard request exception are ignored (and the function restarted)
    # In pytest it fails the test
    resp.raise_for_status()

    # catch_response works just like in regular locustfiles
    with fastsession.get("/", catch_response=True) as resp:
        if not resp.text or not "success" in resp.text:
            resp.failure("missing text in response")

    helper_function(fastsession)  # you can call helper functions as needed

    if fastsession.base_url:  # use --host/-H for relative paths (works for both locust and pytest)
        fastsession.get("/")

    # unlike regular Locust Users, there's no wait_time, so use time.sleep instead
    time.sleep(0.1)


# this is not a test case and won't be detected by pytest/locust
def helper_function(fastsession: FastHttpSession):
    fastsession.get("https://locust.cloud/")
