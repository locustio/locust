from locust.clients import HttpSession
from locust.contrib.fasthttp import FastHttpSession


def test_thing(session: HttpSession):
    session.get("https://locust.cloud/")
    resp = session.get("https://locust.cloud/doesnt_exist")
    resp.raise_for_status()
    session.get("https://locust.cloud/should_never_run")


def test_other_thing(fastsession: FastHttpSession):
    resp = fastsession.get("https://locust.cloud/")
    resp.raise_for_status()
