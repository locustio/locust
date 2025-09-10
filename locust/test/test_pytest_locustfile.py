# pytest style locustfiles, can be run from both pytest and locust!
#
# Example use:
#
# locust -H https://locust.cloud -f test_pytest.py -u 2 test_regular test_host
# pytest -H https://locust.cloud test_pytest.py

from locust.clients import HttpSession
from locust.contrib.fasthttp import FastHttpSession
from locust.exception import CatchResponseError

import pytest


def test_regular(session: HttpSession):
    session.get("https://locust.cloud/")


def test_fasthttp(fastsession: FastHttpSession):
    fastsession.get("https://locust.cloud/")


@pytest.mark.xfail(strict=True)
def test_failure(session: HttpSession):
    session.get("https://locust.cloud/")
    resp = session.get("https://locust.cloud/doesnt_exist")
    # the next line will raise a requests.Exception, which will be caught and ignored by Locust.
    # It still prevents the test from going to the next statement, and is useful for failing the test case when run as pytest
    resp.raise_for_status()
    session.get("https://locust.cloud/will_never_run")


def test_catch_response(session: HttpSession):
    with session.get("https://locust.cloud/", catch_response=True) as resp:
        if not resp.text or not "asdfasdf" in resp.text:
            resp.failure("important text was missing in response")
    pytest.raises(CatchResponseError, resp.raise_for_status)


def test_fasthttp_catch_response(fastsession: FastHttpSession):
    with fastsession.get("https://locust.cloud/", catch_response=True) as resp:
        if not resp.text or not "asdfasdf" in resp.text:
            resp.failure("important text was missing in response")
    pytest.raises(CatchResponseError, resp.raise_for_status)


@pytest.mark.xfail(strict=True)
def test_fasthttp_failure(fastsession: FastHttpSession):
    fastsession.get("https://locust.cloud/")
    resp = fastsession.get("https://locust.cloud/doesnt_exist")
    # the next line will raise a requests.Exception, which will be caught and ignored by Locust.
    # It still prevents the test from going to the next statement, and is useful for failing the test case when run as pytest
    resp.raise_for_status()
    fastsession.get("https://locust.cloud/will_never_run")


def test_host(fastsession: FastHttpSession):
    if not fastsession.base_url:
        pytest.skip("Set hostname with --host/-H to run this test (works for both locust and pytest)")
    resp = fastsession.get("/")
    resp.raise_for_status()
