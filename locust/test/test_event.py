from locust import User, constant, task
from locust.env import Environment
from locust.event import EventHook
from locust.exception import InterruptTaskSet, RescheduleTask, RescheduleTaskImmediately, StopTest, StopUser

import gevent
import pytest


@pytest.mark.parametrize(
    "exception_type", [InterruptTaskSet, RescheduleTask, RescheduleTaskImmediately, StopTest, StopUser]
)
def test_measure_preserves_task_control_exceptions(exception_type):
    event = EventHook()
    requests = []
    event.add_listener(lambda **kwargs: requests.append(kwargs))
    error = exception_type()

    with pytest.raises(exception_type) as caught:
        with event.measure("custom", "operation"):
            raise error

    assert caught.value is error
    assert len(requests) == 1
    assert requests[0]["exception"] is None
    assert requests[0]["response_time"] >= 0


def test_measure_still_records_request_errors():
    event = EventHook()
    requests = []
    event.add_listener(lambda **kwargs: requests.append(kwargs))
    error = ValueError("request failed")

    with event.measure("custom", "operation"):
        raise error

    assert len(requests) == 1
    assert requests[0]["exception"] is error


def test_measured_task_stops_user():
    calls = []

    class MeasuredUser(User):
        wait_time = constant(0)

        @task
        def measured(self):
            calls.append("task")
            # Keep this test bounded if measure swallows the first StopUser.
            if len(calls) > 2:
                raise StopUser()
            with self.environment.events.request.measure("custom", "operation"):
                raise StopUser()
            calls.append("after stop")

    environment = Environment(user_classes=[MeasuredUser])
    user = MeasuredUser(environment)
    greenlet = gevent.spawn(user.run)
    try:
        greenlet.join(timeout=1)
        assert greenlet.ready()
        assert calls == ["task"]
    finally:
        greenlet.kill()
