import random
import time

from locust.core import HttpLocust, Locust, TaskSet, events, task
from locust.exception import MissingWaitTimeError
from locust.wait_time import between, constant, constant_pacing

from .testcases import LocustTestCase, WebserverTestCase


class TestWaitTime(LocustTestCase):
    def test_between(self):
        class User(Locust):
            wait_time = between(3, 9)
        class TaskSet1(TaskSet):
            pass
        class TaskSet2(TaskSet):
            wait_time = between(20.0, 21.0)
        
        u = User()
        ts1 = TaskSet1(u)
        ts2 = TaskSet2(u)
        for i in range(100):
            w = u.wait_time()
            self.assertGreaterEqual(w, 3)
            self.assertLessEqual(w, 9)
            w = ts1.wait_time()
            self.assertGreaterEqual(w, 3)
            self.assertLessEqual(w, 9)
        for i in range(100):
            w = ts2.wait_time()
            self.assertGreaterEqual(w, 20)
            self.assertLessEqual(w, 21)
    
    def test_constant(self):
        class User(Locust):
            wait_time = constant(13)
        class TaskSet1(TaskSet):
            pass
        self.assertEqual(13, User().wait_time())
        self.assertEqual(13, TaskSet1(User()).wait_time())
    
    def test_constant_zero(self):
        class User(Locust):
            wait_time = constant(0)
        class TaskSet1(TaskSet):
            pass
        self.assertEqual(0, User().wait_time())
        self.assertEqual(0, TaskSet1(User()).wait_time())
        start_time = time.time()
        TaskSet1(User()).wait()
        self.assertLess(time.time() - start_time, 0.002)
    
    def test_constant_pacing(self):
        class User(Locust):
            wait_time = constant_pacing(0.1)
        class TS(TaskSet):
            pass
        ts = TS(User())
        
        ts2 = TS(User())      
        
        previous_time = time.time()
        for i in range(7):
            ts.wait()
            since_last_run = time.time() - previous_time
            self.assertLess(abs(0.1 - since_last_run), 0.02)
            previous_time = time.time()
            time.sleep(random.random() * 0.1)
            _ = ts2.wait_time()
            _ = ts2.wait_time()

    def test_missing_wait_time(self):
        class User(Locust):
            pass
        class TS(TaskSet):
            pass
        self.assertRaises(MissingWaitTimeError, lambda: TS(User()).wait_time())

