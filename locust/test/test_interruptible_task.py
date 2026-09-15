from locust import SequentialTaskSet, User, constant, task
from locust.env import Environment
from locust.exception import StopUser

from collections import defaultdict
from unittest import TestCase


class InterruptibleTaskSet(SequentialTaskSet):
    counter: defaultdict[str, int] = defaultdict(int)

    def on_start(self):
        super().on_start()
        self.counter["on_start"] += 1

    @task
    def t1(self):
        self.counter["t1"] += 1
        self.interrupt(reschedule=False)

    @task
    def t2(self):
        self.counter["t2"] += 1

    def on_stop(self):
        super().on_stop()
        self.counter["on_stop"] += 1
        if self.counter["on_stop"] >= 2:
            raise StopUser()


class TestInterruptibleTask(TestCase):
    def setUp(self):
        super().setUp()

        class InterruptibleUser(User):
            host = "127.0.0.1"
            tasks = [InterruptibleTaskSet]
            wait_time = constant(0)

        self.locust = InterruptibleUser(Environment(catch_exceptions=True))

    def test_interruptible_task(self):
        self.locust.run()
        self.assertEqual(InterruptibleTaskSet.counter.get("on_start"), 2)
        self.assertEqual(InterruptibleTaskSet.counter.get("t1"), 2)
        self.assertEqual(InterruptibleTaskSet.counter.get("t2", 0), 0)
        self.assertEqual(InterruptibleTaskSet.counter.get("on_stop"), 2)
