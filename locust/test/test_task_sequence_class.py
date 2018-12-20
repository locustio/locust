import six

from locust import InterruptTaskSet, ResponseError
from locust.core import HttpLocust, Locust, TaskSequence, events, seq_task, task
from locust.exception import (CatchResponseError, LocustError, RescheduleTask,
                              RescheduleTaskImmediately)

from .testcases import LocustTestCase, WebserverTestCase


class TestTaskSet(LocustTestCase):
    def setUp(self):
        super(TestTaskSet, self).setUp()

        class User(Locust):
            host = "127.0.0.1"
            min_wait = 1
            max_wait = 10
        self.locust = User()

    def test_task_sequence_with_list(self):
        def t1(l):
          if l._index == 1:
            l.t1_executed = True

        def t2(l):
          if l._index == 2:
            l.t2_executed = True

        def t3(l):
          if l._index == 0:
            l.t3_executed = True
          raise InterruptTaskSet(reschedule=False)

        class MyTaskSequence(TaskSequence):
            t1_executed = False
            t2_executed = False
            t3_executed = False
            tasks = [t1, t2, t3]

        l = MyTaskSequence(self.locust)

        self.assertRaises(RescheduleTask, lambda: l.run())
        self.assertTrue(l.t1_executed)
        self.assertTrue(l.t2_executed)
        self.assertTrue(l.t3_executed)

    def test_task_with_decorator(self):
        class MyTaskSequence(TaskSequence):
            t1_executed = 0
            t2_executed = 0
            t3_executed = 0

            @seq_task(1)
            def t1(self):
              if self._index == 1:
                self.t1_executed += 1

            @seq_task(2)
            @task(3)
            def t2(self):
              if self._index == 2 or self._index == 3 or self._index == 4:
                l.t2_executed += 1

            @seq_task(3)
            def t3(self):
              if self._index == 0:
                self.t3_executed += 1
              raise InterruptTaskSet(reschedule=False)

        l = MyTaskSequence(self.locust)

        self.assertRaises(RescheduleTask, lambda: l.run())
        self.assertEqual(l.t1_executed, 1)
        self.assertEqual(l.t2_executed, 3)
        self.assertEqual(l.t3_executed, 1)
