from locust import SequentialTaskSet, User, constant, task
from locust.env import Environment
from locust.exception import StopUser

from collections import defaultdict
from typing import DefaultDict
from unittest import TestCase


class InterruptableTaskSet(SequentialTaskSet):
    counter: DefaultDict[str, int] = defaultdict(int)

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


class TestInterruptableTask(TestCase):
    def setUp(self):
        super().setUp()

        class InterruptableUser(User):
            host = "127.0.0.1"
            tasks = [InterruptableTaskSet]
            wait_time = constant(0)

        self.locust = InterruptableUser(Environment(catch_exceptions=True))

    def test_interruptable_task(self):
        self.locust.run()
        self.assertEqual(InterruptableTaskSet.counter.get("on_start"), 2)
        self.assertEqual(InterruptableTaskSet.counter.get("t1"), 2)
        self.assertEqual(InterruptableTaskSet.counter.get("t2", 0), 0)
        self.assertEqual(InterruptableTaskSet.counter.get("on_stop"), 2)
