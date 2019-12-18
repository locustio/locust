import warnings

from locust import InterruptTaskSet, ResponseError
from locust.core import HttpLocust, Locust, TaskSet, events, task
from locust.exception import (CatchResponseError, LocustError, RescheduleTask,
                              RescheduleTaskImmediately)
from locust.wait_time import between, constant

from .testcases import LocustTestCase, WebserverTestCase


class TestOldWaitApi(LocustTestCase):
    def setUp(self):
        super(TestOldWaitApi, self).setUp()
    
    def test_wait_function(self):
        with warnings.catch_warnings(record=True) as w:
            class User(Locust):
                wait_function = lambda self: 5000
            class MyTaskSet(TaskSet):
                pass
            taskset = MyTaskSet(User())
            self.assertEqual(5, taskset.wait_time())
            self.assertEqual(1, len(w))
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("wait_function", str(w[0].message))
    
    def test_wait_function_on_taskset(self):
        with warnings.catch_warnings(record=True) as w:
            class User(Locust):
                pass
            class MyTaskSet(TaskSet):
                wait_function = lambda self: 5000
            taskset = MyTaskSet(User())
            self.assertEqual(5, taskset.wait_time())
            self.assertEqual(1, len(w))
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("wait_function", str(w[0].message))
    
    def test_min_max_wait(self):
        with warnings.catch_warnings(record=True) as w:
            class User(Locust):
                min_wait = 1000
                max_wait = 1000
            class TS(TaskSet):
                @task
                def t(self):
                    pass
            taskset = TS(User())
            self.assertEqual(1, taskset.wait_time())
            self.assertEqual(1, len(w))
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("min_wait", str(w[0].message))
            self.assertIn("max_wait", str(w[0].message))
    
    def test_zero_min_max_wait(self):
        return
        with warnings.catch_warnings(record=True) as w:
            class User(Locust):
                min_wait = 0
                max_wait = 0
            class TS(TaskSet):
                @task
                def t(self):
                    pass
            taskset = TS(User())
            self.assertEqual(0, taskset.wait_time())
            self.assertEqual(1, len(w))
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("min_wait", str(w[0].message))
            self.assertIn("max_wait", str(w[0].message))
    
    def test_min_max_wait_combined_with_wait_time(self):
        with warnings.catch_warnings(record=True) as w:
            class User(Locust):
                min_wait = 1000
                max_wait = 1000
            class TS(TaskSet):
                wait_time = constant(3)
                @task
                def t(self):
                    pass
            taskset = TS(User())
            self.assertEqual(3, taskset.wait_time())
            self.assertEqual(1, len(w))
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("min_wait", str(w[0].message))
            self.assertIn("max_wait", str(w[0].message))
    
    def test_min_max_wait_on_taskset(self):
        with warnings.catch_warnings(record=True) as w:
            class User(Locust):
                wait_time = constant(3)
            class TS(TaskSet):
                min_wait = 1000
                max_wait = 1000                
                @task
                def t(self):
                    pass
            taskset = TS(User())
            self.assertEqual(3, taskset.wait_time())
            self.assertEqual(1, len(w))
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("min_wait", str(w[0].message))
            self.assertIn("max_wait", str(w[0].message))
        
