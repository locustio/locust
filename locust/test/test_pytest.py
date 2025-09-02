# pytest style locustfiles, can be run from both pytest and locust!
# Make sure you install pytest first
from locust.clients import HttpSession
from locust.contrib.fasthttp import FastHttpSession


def test_thing(session: HttpSession):
    session.get("https://locust.cloud/")
    resp = session.get("https://locust.cloud/doesnt_exist")
    # the next line will raise a requests.Exception, which will be caught and ignored by Locust, but
    # it prevents the test from continuing, and is very useful for failing the test case
    # resp.raise_for_status()
    session.get("https://locust.cloud/should_never_run")


def test_other_thing(fastsession: FastHttpSession):
    fastsession.get("https://locust.cloud/")
