# pytest style locustfiles, can be run from both pytest and locust!
#
# Example use:
#
# locust -H http://localhost/ -f test_pytest.py -u 2 test_regular test_host
# pytest -H http://localhost/ test_pytest.py

from locust.clients import HttpSession
from locust.contrib.fasthttp import FastHttpSession
from locust.exception import CatchResponseError
from locust.test.util import local_http_server

import pytest


def test_regular(session: HttpSession):
    with local_http_server() as server:
        session.get(f"{server.url}/")


def test_fasthttp(fastsession: FastHttpSession):
    with local_http_server() as server:
        fastsession.get(f"{server.url}/")


@pytest.mark.xfail(strict=True)
def test_failure(session: HttpSession):
    with local_http_server() as server:
        session.get(f"{server.url}/")
        resp = session.get(f"{server.url}/doesnt_exist")
        # the next line will raise a requests.Exception, which will be caught and ignored by Locust.
        # It still prevents the test from going to the next statement, and is useful for failing the test case when run as pytest
        resp.raise_for_status()
        session.get(f"{server.url}/will_never_run")


def test_catch_response(session: HttpSession):
    with local_http_server() as server:
        with session.get(f"{server.url}/", catch_response=True) as resp:
            if not resp.text or not "asdfasdf" in resp.text:
                resp.failure("important text was missing in response")
        with pytest.raises(CatchResponseError):
            resp.raise_for_status()


def test_fasthttp_catch_response(fastsession: FastHttpSession):
    with local_http_server() as server:
        with fastsession.get(f"{server.url}/", catch_response=True) as resp:
            if not resp.text or not "asdfasdf" in resp.text:
                resp.failure("important text was missing in response")
        with pytest.raises(CatchResponseError):
            resp.raise_for_status()


@pytest.mark.xfail(strict=True)
def test_fasthttp_failure(fastsession: FastHttpSession):
    with local_http_server() as server:
        fastsession.get(f"{server.url}/")
        resp = fastsession.get(f"{server.url}/doesnt_exist")
        # the next line will raise a requests.Exception, which will be caught and ignored by Locust.
        # It still prevents the test from going to the next statement, and is useful for failing the test case when run as pytest
        resp.raise_for_status()
        fastsession.get(f"{server.url}/will_never_run")


host = "https://www.locust.io/"


def test_host(fastsession: FastHttpSession):
    if not fastsession.base_url:
        pytest.skip("Set hostname with --host/-H to run this test (works for both locust and pytest)")
    resp = fastsession.get("/")
    resp.raise_for_status()
