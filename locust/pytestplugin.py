from locust.clients import HttpSession
from locust.contrib.fasthttp import FastHttpSession
from locust.event import EventHook
from locust.user.users import User

import pytest


class NoOpEvent(EventHook):
    pass


_config: pytest.Config


# capture Config object instead of having to pass it explicitly to fixtures, which would make them more complex to call from Locust
def pytest_configure(config):
    global _config
    _config = config


@pytest.fixture
def session(user: User | None = None):
    s = HttpSession(
        base_url=user.host if user else _config.getoption("--host"),
        request_event=user.environment.events.request if user else NoOpEvent(),
        user=user,
    )
    yield s
    s.close()


@pytest.fixture
def fastsession(user: User | None = None):
    s = FastHttpSession(
        base_url=user.host if user else _config.getoption("--host"),
        request_event=user.environment.events.request if user else NoOpEvent(),
        user=user,
    )
    yield s


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--host", "-H", action="store", default=None)
