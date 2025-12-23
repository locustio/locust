from locust.clients import HttpSession  # this import is just for type hints

import time


# pytest/locust will discover any functions prefixed with "test_" as test cases.
# session and fastsession are pytest fixtures provided by Locust's pytest plugin.
def test_stuff(session):
    resp = session.get("https://www.locust.io/")

    # Bad HTTP status codes in the response dont automatically raise an exception,
    # so if that is what you want, you need to call:
    resp.raise_for_status()
    # In Locust, request-related exceptions are caught (and the test case restarted),
    # in pytest any exceptions fail the test case

    # Just like with Locust, you can set a base URL using --host/-H when using pytest.
    # Or you can set a default:
    if not session.base_url:
        session.base_url = "https://www.locust.io"

    # catch_response works just like in regular locustfiles
    with session.get("/", catch_response=True) as resp:
        if not resp.text or not "Load" in resp.text:
            resp.failure("important text was missing in response")

    # raise_for_status also respects calls to resp.failure()/.success()
    # so this will raise an exception and fail the test case if "Load" was missing
    resp.raise_for_status()

    # you can call helper functions as needed
    helper_function(session)

    # unlike regular Locust Users, there's no wait_time, so use time.sleep instead
    time.sleep(0.1)


# this is not a test case and won't be detected by pytest/locust
def helper_function(session: HttpSession):
    session.get("/")
