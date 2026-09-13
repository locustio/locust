from locust import TaskSet, User, between, constant, constant_throughput, poisson

import random
import time

from .testcases import LocustTestCase


class TestWaitTime(LocustTestCase):
    def test_between(self):
        class MyUser(User):
            wait_time = between(3, 9)

        class TaskSet1(TaskSet):
            pass

        class TaskSet2(TaskSet):
            wait_time = between(20.0, 21.0)

        u = MyUser(self.environment)
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
        class MyUser(User):
            wait_time = constant(13)

        class TaskSet1(TaskSet):
            pass

        self.assertEqual(13, MyUser(self.environment).wait_time())
        self.assertEqual(13, TaskSet1(MyUser(self.environment)).wait_time())

    def test_default_wait_time(self):
        class MyUser(User):
            pass  # default is wait_time = constant(0)

        class TaskSet1(TaskSet):
            pass

        self.assertEqual(0, MyUser(self.environment).wait_time())
        self.assertEqual(0, TaskSet1(MyUser(self.environment)).wait_time())
        taskset = TaskSet1(MyUser(self.environment))
        start_time = time.perf_counter()
        taskset.wait()
        self.assertLess(time.perf_counter() - start_time, 0.002)

    def test_constant_throughput(self):
        class MyUser(User):
            wait_time = constant_throughput(10)

        class TS(TaskSet):
            pass

        ts = TS(MyUser(self.environment))

        ts2 = TS(MyUser(self.environment))

        previous_time = time.perf_counter()
        for i in range(7):
            ts.wait()
            since_last_run = time.perf_counter() - previous_time
            self.assertLess(abs(0.1 - since_last_run), 0.02)
            previous_time = time.perf_counter()
            time.sleep(random.random() * 0.1)
            _ = ts2.wait_time()
            _ = ts2.wait_time()

    def test_poisson_mean(self):
        # The mean wait time of an exponential distribution with rate=10 is 1/10
        # With 10000 samples the standard error of the mean is ~0.001, so a delta of 0.01 is very generous
        class MyUser(User):
            wait_time = poisson(10)

        u = MyUser(self.environment)
        waits = [u.wait_time() for _ in range(10000)]
        self.assertAlmostEqual(sum(waits) / len(waits), 0.1, delta=0.01)
        # All waits must be non-negative
        self.assertTrue(all(w >= 0 for w in waits))
        # The unbounded tail of the exponential distribution means we should see
        # some waits far above the mean (P(wait > 0.3) = e^-3 ~= 5% per sample),
        # distinguishing poisson from a uniformly distributed wait
        self.assertTrue(any(w > 0.3 for w in waits))

    def test_poisson_invalid_rate(self):
        self.assertRaises(ValueError, poisson, 0)
        self.assertRaises(ValueError, poisson, -1)
