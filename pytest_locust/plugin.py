# This is used in pytest style locustfiles, see examples/test_pytest.py
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from locust.user.users import User


class NoOpEvent:  # Fake locust.event.EventHook
    def fire(self, *, reverse=False, **kwargs):
        pass


_config: pytest.Config


# capture Config object instead of having to pass it explicitly to fixtures, which would make them more complex to call from Locust
def pytest_configure(config):
    global _config
    _config = config


@pytest.fixture
def session(user: "User | None" = None):
    # lazy import to avoid gevent monkey patching unless you actually use this fixture
    from locust.clients import HttpSession

    s = HttpSession(
        base_url=user.host if user else _config.getoption("--host"),
        request_event=user.environment.events.request if user else NoOpEvent(),
        user=user,
    )
    yield s
    s.close()


@pytest.fixture
def fastsession(user: "User | None" = None):
    # lazy import to avoid gevent monkey patching unless you actually use this fixture
    from locust.contrib.fasthttp import FastHttpSession

    s = FastHttpSession(
        base_url=user.host if user else _config.getoption("--host"),
        request_event=user.environment.events.request if user else NoOpEvent(),
        user=user,
    )
    yield s


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--host", "-H", action="store", default=None)
