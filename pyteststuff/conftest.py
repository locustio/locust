from locust.clients import HttpSession
from locust.contrib.fasthttp import FastHttpSession
from locust.event import EventHook

import pytest


class NoOpEvent(EventHook):
    pass


@pytest.fixture
def session(user=None):
    """Provide a real requests.Session object to tests."""
    s = HttpSession(
        base_url=None,
        request_event=user.environment.events.request if user else NoOpEvent(),
        user=user,
    )
    yield s
    s.close()


@pytest.fixture
def fastsession(user=None):
    """Provide a real requests.Session object to tests."""
    s = FastHttpSession(
        base_url=None,
        request_event=user.environment.events.request if user else NoOpEvent(),
        user=user,
    )
    yield s
