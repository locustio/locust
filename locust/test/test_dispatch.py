import time
import unittest
from operator import attrgetter
from typing import Dict, List, Tuple, Type

from locust import User
from locust.dispatch import UsersDispatcher
from locust.runners import WorkerNode
from locust.test.util import clear_all_functools_lru_cache

_TOLERANCE = 0.025


class TestRampUpUsersFromZero(unittest.TestCase):
    def test_ramp_up_users_to_3_workers_with_spawn_rate_of_0_5(self):
        """Final distribution should be {"User1": 3, "User2": 3, "User3": 3}"""

        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        sleep_time = 0.2  # Speed-up test

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=0.5)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_up_users_to_3_workers_with_spawn_rate_of_1(self):
        """Final distribution should be {"User1": 3, "User2": 3, "User3": 3}"""

        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        sleep_time = 0.2  # Speed-up test

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_up_users_to_4_workers_with_spawn_rate_of_1(self):
        """Final distribution should be {"User1": 3, "User2": 3, "User3": 3}"""

        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")
        worker_node4 = WorkerNode("4")

        sleep_time = 0.2  # Speed-up test

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3, worker_node4], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
                "4": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
                "4": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
                "4": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 1},
                "3": {"User1": 0, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 0, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_up_users_to_3_workers_with_spawn_rate_of_2(self):
        """Final distribution should be {"User1": 3, "User2": 3, "User3": 3}"""

        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        sleep_time = 0.2  # Speed-up test

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=2)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_up_users_to_3_workers_with_spawn_rate_of_2_4(self):
        """Final distribution should be {"User1": 3, "User2": 3, "User3": 3}"""

        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        sleep_time = 0.2  # Speed-up test

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=2.4)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_up_users_to_3_workers_with_spawn_rate_of_3(self):
        """Final distribution should be {"User1": 3, "User2": 3, "User3": 3}"""

        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        sleep_time = 0.2  # Speed-up test

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_up_users_to_3_workers_with_spawn_rate_of_4(self):
        """Final distribution should be {"User1": 3, "User2": 3, "User3": 3}"""

        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        sleep_time = 0.2  # Speed-up test

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=4)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_up_users_to_3_workers_with_spawn_rate_of_9(self):
        """Final distribution should be {"User1": 3, "User2": 3, "User3": 3}"""

        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        sleep_time = 0.2  # Speed-up test

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=9)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_users_are_distributed_evenly_across_hosts(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        worker_node1 = WorkerNode("hostname1_worker1")
        worker_node2 = WorkerNode("hostname1_worker2")
        worker_node3 = WorkerNode("hostname2_worker1")
        worker_node4 = WorkerNode("hostname2_worker2")

        sleep_time = 0.2  # Speed-up test

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3, worker_node4], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=6, spawn_rate=2)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "hostname1_worker1": {"User1": 1, "User2": 0, "User3": 0},
                "hostname1_worker2": {"User1": 0, "User2": 0, "User3": 0},
                "hostname2_worker1": {"User1": 0, "User2": 1, "User3": 0},
                "hostname2_worker2": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "hostname1_worker1": {"User1": 1, "User2": 0, "User3": 0},
                "hostname1_worker2": {"User1": 0, "User2": 0, "User3": 1},
                "hostname2_worker1": {"User1": 0, "User2": 1, "User3": 0},
                "hostname2_worker2": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "hostname1_worker1": {"User1": 1, "User2": 1, "User3": 0},
                "hostname1_worker2": {"User1": 0, "User2": 0, "User3": 1},
                "hostname2_worker1": {"User1": 0, "User2": 1, "User3": 1},
                "hostname2_worker2": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)


class TestWaitBetweenDispatch(unittest.TestCase):
    def test_wait_between_dispatch(self):
        class User1(User):
            weight = 1

        user_classes = [User1]

        workers = [WorkerNode("1")]

        for spawn_rate, expected_wait_between_dispatch in [
            (0.5, 1 / 0.5),
            (1, 1),
            (2, 1),
            (2.4, 2 / 2.4),
            (4, 1),
            (9, 1),
        ]:
            users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
            users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=spawn_rate)
            self.assertEqual(users_dispatcher._wait_between_dispatch, expected_wait_between_dispatch)


class TestRampDownUsersToZero(unittest.TestCase):
    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_0_5(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        workers = [WorkerNode(str(i + 1)) for i in range(3)]

        initial_user_count = 9

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
        users_dispatcher.new_dispatch(target_user_count=initial_user_count, spawn_rate=initial_user_count)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=0.5)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_1(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        workers = [WorkerNode(str(i + 1)) for i in range(3)]

        initial_user_count = 9

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
        users_dispatcher.new_dispatch(target_user_count=initial_user_count, spawn_rate=initial_user_count)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_down_users_to_4_workers_with_spawn_rate_of_1(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        workers = [WorkerNode(str(i + 1)) for i in range(4)]

        initial_user_count = 9

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
        users_dispatcher.new_dispatch(target_user_count=initial_user_count, spawn_rate=initial_user_count)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 1},
                "3": {"User1": 0, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
                "4": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
                "4": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
                "4": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
                "4": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
                "4": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_2(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        workers = [WorkerNode(str(i + 1)) for i in range(3)]

        initial_user_count = 9

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
        users_dispatcher.new_dispatch(target_user_count=initial_user_count, spawn_rate=initial_user_count)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=2)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_2_4(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        workers = [WorkerNode(str(i + 1)) for i in range(3)]

        initial_user_count = 9

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
        users_dispatcher.new_dispatch(target_user_count=initial_user_count, spawn_rate=initial_user_count)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=2.4)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 3, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_3(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        workers = [WorkerNode(str(i + 1)) for i in range(3)]

        initial_user_count = 9

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
        users_dispatcher.new_dispatch(target_user_count=initial_user_count, spawn_rate=initial_user_count)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_4(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        workers = [WorkerNode(str(i + 1)) for i in range(3)]

        initial_user_count = 9

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
        users_dispatcher.new_dispatch(target_user_count=initial_user_count, spawn_rate=initial_user_count)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=4)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_9(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        workers = [WorkerNode(str(i + 1)) for i in range(3)]

        initial_user_count = 9

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
        users_dispatcher.new_dispatch(target_user_count=initial_user_count, spawn_rate=initial_user_count)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=9)
        users_dispatcher._wait_between_dispatch = sleep_time

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)


class TestRampUpThenDownThenUp(unittest.TestCase):
    def test_ramp_up_then_down_then_up(self):
        for user1_weight, user2_weight, user3_weight, user4_weight, user5_weight in [
            (1, 1, 1, 1, 1),
            (1, 2, 3, 4, 5),
            (1, 3, 5, 7, 9),
        ]:

            class User1(User):
                weight = user1_weight

            class User2(User):
                weight = user2_weight

            class User3(User):
                weight = user3_weight

            class User4(User):
                weight = user4_weight

            class User5(User):
                weight = user5_weight

            all_user_classes = [User1, User2, User3, User4, User5]

            for number_of_user_classes in range(1, len(all_user_classes) + 1):
                user_classes = all_user_classes[:number_of_user_classes]

                for max_user_count, min_user_count in [(30, 15), (54, 21), (14165, 1476)]:
                    for worker_count in [1, 3, 5, 9]:
                        workers = [WorkerNode(str(i + 1)) for i in range(worker_count)]

                        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)

                        # Ramp-up to go to `min_user_count` #########

                        users_dispatcher.new_dispatch(target_user_count=min_user_count, spawn_rate=1)
                        users_dispatcher._wait_between_dispatch = 0

                        all_dispatched_users_ramp_up_to_min_user_count = list(users_dispatcher)

                        # Ramp-up to go to `max_user_count` #########

                        users_dispatcher.new_dispatch(target_user_count=max_user_count, spawn_rate=1)
                        users_dispatcher._wait_between_dispatch = 0

                        list(users_dispatcher)

                        # Ramp-down go back to `min_user_count` #########

                        users_dispatcher.new_dispatch(target_user_count=min_user_count, spawn_rate=1)
                        users_dispatcher._wait_between_dispatch = 0

                        all_dispatched_users_ramp_down_to_min_user_count = list(users_dispatcher)

                        # Assertions #########

                        self.assertDictEqual(
                            all_dispatched_users_ramp_up_to_min_user_count[-1],
                            all_dispatched_users_ramp_down_to_min_user_count[-1],
                        )


class TestDispatchUsersToWorkersHavingTheSameUsersAsTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers(self):
        """Final distribution should be {"User1": 3, "User2": 3, "User3": 3}"""

        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        user_count = 9

        for spawn_rate in [0.15, 0.5, 1, 2, 2.4, 3, 4, 9]:
            workers = [WorkerNode(str(i + 1)) for i in range(3)]

            users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
            users_dispatcher.new_dispatch(target_user_count=user_count, spawn_rate=user_count)
            users_dispatcher._wait_between_dispatch = 0
            list(users_dispatcher)

            sleep_time = 0.2  # Speed-up test

            users_dispatcher.new_dispatch(target_user_count=user_count, spawn_rate=spawn_rate)
            users_dispatcher._wait_between_dispatch = sleep_time

            ts = time.perf_counter()
            self.assertDictEqual(
                next(users_dispatcher),
                {
                    "1": {"User1": 3, "User2": 0, "User3": 0},
                    "2": {"User1": 0, "User2": 3, "User3": 0},
                    "3": {"User1": 0, "User2": 0, "User3": 3},
                },
            )
            delta = time.perf_counter() - ts
            self.assertTrue(0 <= delta <= _TOLERANCE, delta)

            ts = time.perf_counter()
            self.assertRaises(StopIteration, lambda: next(users_dispatcher))
            delta = time.perf_counter() - ts
            self.assertTrue(0 <= delta <= _TOLERANCE, delta)

            clear_all_functools_lru_cache()


class TestDistributionIsRespectedDuringDispatch(unittest.TestCase):
    def test_dispatch_75_users_to_4_workers_with_spawn_rate_of_5(self):
        """
        Test case covering reported issue in https://github.com/locustio/locust/pull/1621#issuecomment-853624275.

        The case is to ramp-up from 0 to 75 users with two user classes. `User1` has a weight of 1 and `User2`
        has a weight of 2. The original issue was with 500 users, but to keep the test shorter, we use 75 users.

        Final distribution should be {"User1": 25, "User2": 50}
        """

        class User1(User):
            weight = 1

        class User2(User):
            weight = 2

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")
        worker_node4 = WorkerNode("4")

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3, worker_node4], user_classes=[User1, User2]
        )
        users_dispatcher.new_dispatch(target_user_count=75, spawn_rate=5)
        users_dispatcher._wait_between_dispatch = 0

        # total user count = 5
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 3})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 1, "User2": 1},
                "2": {"User1": 1, "User2": 0},
                "3": {"User1": 0, "User2": 1},
                "4": {"User1": 0, "User2": 1},
            },
        )

        # total user count = 10
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 7})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 1, "User2": 2},
                "2": {"User1": 1, "User2": 2},
                "3": {"User1": 0, "User2": 2},
                "4": {"User1": 1, "User2": 1},
            },
        )

        # total user count = 15
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 5, "User2": 10})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 1, "User2": 3},
                "2": {"User1": 2, "User2": 2},
                "3": {"User1": 1, "User2": 3},
                "4": {"User1": 1, "User2": 2},
            },
        )

        # total user count = 20
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 7, "User2": 13})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 2, "User2": 3},
                "2": {"User1": 2, "User2": 3},
                "3": {"User1": 1, "User2": 4},
                "4": {"User1": 2, "User2": 3},
            },
        )

        # total user count = 25
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 8, "User2": 17})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 2, "User2": 5},
                "2": {"User1": 2, "User2": 4},
                "3": {"User1": 2, "User2": 4},
                "4": {"User1": 2, "User2": 4},
            },
        )

        # total user count = 30
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 10, "User2": 20})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 3, "User2": 5},
                "2": {"User1": 3, "User2": 5},
                "3": {"User1": 2, "User2": 5},
                "4": {"User1": 2, "User2": 5},
            },
        )

        # total user count = 35
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 12, "User2": 23})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 3, "User2": 6},
                "2": {"User1": 3, "User2": 6},
                "3": {"User1": 3, "User2": 6},
                "4": {"User1": 3, "User2": 5},
            },
        )

        # total user count = 40
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 13, "User2": 27})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 3, "User2": 7},
                "2": {"User1": 4, "User2": 6},
                "3": {"User1": 3, "User2": 7},
                "4": {"User1": 3, "User2": 7},
            },
        )

        # total user count = 45
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 15, "User2": 30})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 4, "User2": 8},
                "2": {"User1": 4, "User2": 7},
                "3": {"User1": 3, "User2": 8},
                "4": {"User1": 4, "User2": 7},
            },
        )

        # total user count = 50
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 17, "User2": 33})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 4, "User2": 9},
                "2": {"User1": 5, "User2": 8},
                "3": {"User1": 4, "User2": 8},
                "4": {"User1": 4, "User2": 8},
            },
        )

        # total user count = 55
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 18, "User2": 37})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 5, "User2": 9},
                "2": {"User1": 5, "User2": 9},
                "3": {"User1": 4, "User2": 10},
                "4": {"User1": 4, "User2": 9},
            },
        )

        # total user count = 60
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 20, "User2": 40})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 5, "User2": 10},
                "2": {"User1": 5, "User2": 10},
                "3": {"User1": 5, "User2": 10},
                "4": {"User1": 5, "User2": 10},
            },
        )

        # total user count = 65
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 22, "User2": 43})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 6, "User2": 11},
                "2": {"User1": 6, "User2": 10},
                "3": {"User1": 5, "User2": 11},
                "4": {"User1": 5, "User2": 11},
            },
        )

        # total user count = 70
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 23, "User2": 47})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 6, "User2": 12},
                "2": {"User1": 6, "User2": 12},
                "3": {"User1": 5, "User2": 12},
                "4": {"User1": 6, "User2": 11},
            },
        )

        # total user count = 75, User1 = 25, User2 = 50
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 25, "User2": 50})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 6, "User2": 13},
                "2": {"User1": 7, "User2": 12},
                "3": {"User1": 6, "User2": 13},
                "4": {"User1": 6, "User2": 12},
            },
        )

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))


class TestLargeScale(unittest.TestCase):
    # fmt: off
    weights = [
        5, 55, 37, 2, 97, 41, 33, 19, 19, 34, 78, 76, 28, 62, 69, 5, 55, 37, 2, 97, 41, 33, 19, 19, 34,
        78, 76, 28, 62, 69, 41, 33, 19, 19, 34, 78, 76, 28, 62, 69, 41, 33, 19, 19, 34, 78, 76, 28, 62, 69
    ]
    # fmt: on
    numerated_weights = dict(zip(range(len(weights)), weights))

    weighted_user_classes = [type(f"User{i}", (User,), {"weight": w}) for i, w in numerated_weights.items()]
    fixed_user_classes_10k = [type(f"FixedUser10k{i}", (User,), {"fixed_count": 2000}) for i in range(50)]
    fixed_user_classes_1M = [type(f"FixedUser1M{i}", (User,), {"fixed_count": 20000}) for i in range(50)]
    mixed_users = weighted_user_classes[:25] + fixed_user_classes_10k[25:]

    def test_distribute_users(self):
        for user_classes in [self.weighted_user_classes, self.fixed_user_classes_1M, self.mixed_users]:
            workers = [WorkerNode(str(i)) for i in range(10_000)]

            target_user_count = 1_000_000

            users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)

            ts = time.perf_counter()
            users_on_workers, user_gen, worker_gen, active_users = users_dispatcher._distribute_users(
                target_user_count=target_user_count
            )
            delta = time.perf_counter() - ts

            # Because tests are run with coverage, the code will be slower.
            # We set the pass criterion to 7000ms, but in real life, the
            # `_distribute_users` method runs faster than this.
            self.assertLessEqual(1000 * delta, 7000)

            self.assertEqual(_user_count(users_on_workers), target_user_count)

    def test_ramp_up_from_0_to_100_000_users_with_50_user_classes_and_1000_workers_and_5000_spawn_rate(self):
        for user_classes in [
            self.weighted_user_classes,
            self.fixed_user_classes_1M,
            self.fixed_user_classes_10k,
            self.mixed_users,
        ]:
            workers = [WorkerNode(str(i)) for i in range(1000)]

            target_user_count = 100_000

            users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
            users_dispatcher.new_dispatch(target_user_count=target_user_count, spawn_rate=5_000)
            users_dispatcher._wait_between_dispatch = 0

            all_dispatched_users = list(users_dispatcher)

            tol = 0.2
            self.assertTrue(
                all(
                    dispatch_iteration_duration <= tol
                    for dispatch_iteration_duration in users_dispatcher.dispatch_iteration_durations
                ),
                "One or more dispatch took more than {:.0f}s to compute (max = {}ms)".format(
                    tol * 1000, 1000 * max(users_dispatcher.dispatch_iteration_durations)
                ),
            )

            self.assertEqual(_user_count(all_dispatched_users[-1]), target_user_count)

            for dispatch_users in all_dispatched_users:
                user_count_on_workers = [
                    sum(user_classes_count.values()) for user_classes_count in dispatch_users.values()
                ]
                self.assertLessEqual(
                    max(user_count_on_workers) - min(user_count_on_workers),
                    1,
                    "One or more workers have too much users compared to the other workers when user count is {}".format(
                        _user_count(dispatch_users)
                    ),
                )

            for i, dispatch_users in enumerate(all_dispatched_users):
                aggregated_dispatched_users = _aggregate_dispatched_users(dispatch_users)
                for user_class in [u for u in user_classes if not u.fixed_count]:
                    target_relative_weight = user_class.weight / sum(
                        map(attrgetter("weight"), [u for u in user_classes if not u.fixed_count])
                    )
                    relative_weight = aggregated_dispatched_users[user_class.__name__] / _user_count(dispatch_users)
                    error_percent = 100 * (relative_weight - target_relative_weight) / target_relative_weight
                    if i == len(all_dispatched_users) - 1:
                        # We want the distribution to be as good as possible at the end of the ramp-up
                        tol = 0.5
                    else:
                        tol = 15
                    self.assertLessEqual(
                        error_percent,
                        tol,
                        "Distribution for user class {} is off by more than {}% when user count is {}".format(
                            user_class, tol, _user_count(dispatch_users)
                        ),
                    )

    def test_ramp_down_from_100_000_to_0_users_with_50_user_classes_and_1000_workers_and_5000_spawn_rate(self):
        for user_classes in [
            self.weighted_user_classes,
            self.fixed_user_classes_1M,
            self.fixed_user_classes_10k,
            self.mixed_users,
        ]:
            initial_user_count = 100_000

            workers = [WorkerNode(str(i)) for i in range(1000)]

            # Ramp-up
            users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)
            users_dispatcher.new_dispatch(target_user_count=initial_user_count, spawn_rate=initial_user_count)
            users_dispatcher._wait_between_dispatch = 0
            list(users_dispatcher)

            # Ramp-down
            users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=5000)
            users_dispatcher._wait_between_dispatch = 0

            all_dispatched_users = list(users_dispatcher)

            tol = 0.2
            self.assertTrue(
                all(
                    dispatch_iteration_duration <= tol
                    for dispatch_iteration_duration in users_dispatcher.dispatch_iteration_durations
                ),
                "One or more dispatch took more than {:.0f}ms to compute (max = {}ms)".format(
                    tol * 1000, 1000 * max(users_dispatcher.dispatch_iteration_durations)
                ),
            )

            self.assertEqual(_user_count(all_dispatched_users[-1]), 0)

            for dispatch_users in all_dispatched_users[:-1]:
                user_count_on_workers = [
                    sum(user_classes_count.values()) for user_classes_count in dispatch_users.values()
                ]
                self.assertLessEqual(
                    max(user_count_on_workers) - min(user_count_on_workers),
                    1,
                    "One or more workers have too much users compared to the other workers when user count is {}".format(
                        _user_count(dispatch_users)
                    ),
                )

            for dispatch_users in all_dispatched_users[:-1]:
                aggregated_dispatched_users = _aggregate_dispatched_users(dispatch_users)
                for user_class in [u for u in user_classes if not u.fixed_count]:
                    target_relative_weight = user_class.weight / sum(
                        map(attrgetter("weight"), [u for u in user_classes if not u.fixed_count])
                    )
                    relative_weight = aggregated_dispatched_users[user_class.__name__] / _user_count(dispatch_users)
                    error_percent = 100 * (relative_weight - target_relative_weight) / target_relative_weight
                    tol = 15
                    self.assertLessEqual(
                        error_percent,
                        tol,
                        "Distribution for user class {} is off by more than {}% when user count is {}".format(
                            user_class, tol, _user_count(dispatch_users)
                        ),
                    )


class TestSmallConsecutiveRamping(unittest.TestCase):
    def test_consecutive_ramp_up_and_ramp_down(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        user_classes = [User1, User2]

        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")

        worker_nodes = [worker_node1, worker_node2]

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes=user_classes)

        # user count = 1
        users_dispatcher.new_dispatch(target_user_count=1, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = 0

        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 1, "User2": 0})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node1.id), 1)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node2.id), 0)

        # user count = 2
        users_dispatcher.new_dispatch(target_user_count=2, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = 0

        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 1, "User2": 1})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node1.id), 1)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node2.id), 1)

        # user count = 3
        users_dispatcher.new_dispatch(target_user_count=3, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = 0

        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 1})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node1.id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node2.id), 1)

        # user count = 4
        users_dispatcher.new_dispatch(target_user_count=4, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = 0

        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node1.id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node2.id), 2)

        # user count = 3
        users_dispatcher.new_dispatch(target_user_count=3, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = 0

        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 1})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node1.id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node2.id), 1)

        # user count = 2
        users_dispatcher.new_dispatch(target_user_count=2, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = 0

        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 1, "User2": 1})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node1.id), 1)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node2.id), 1)

        # user count = 1
        users_dispatcher.new_dispatch(target_user_count=1, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = 0

        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 1, "User2": 0})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node1.id), 1)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node2.id), 0)

        # user count = 0
        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=1)
        users_dispatcher._wait_between_dispatch = 0

        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 0, "User2": 0})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node1.id), 0)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_node2.id), 0)


class TestRampingMiscellaneous(unittest.TestCase):
    def test_spawn_rate_greater_than_target_user_count(self):
        class User1(User):
            weight = 1

        user_classes = [User1]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(1)]

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=1, spawn_rate=100)
        users_dispatcher._wait_between_dispatch = 0
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(dispatched_users, {"1": {"User1": 1}})

        users_dispatcher.new_dispatch(target_user_count=11, spawn_rate=100)
        users_dispatcher._wait_between_dispatch = 0
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(dispatched_users, {"1": {"User1": 11}})

        users_dispatcher.new_dispatch(target_user_count=10, spawn_rate=100)
        users_dispatcher._wait_between_dispatch = 0
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(dispatched_users, {"1": {"User1": 10}})

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=100)
        users_dispatcher._wait_between_dispatch = 0
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(dispatched_users, {"1": {"User1": 0}})


class TestRemoveWorker(unittest.TestCase):
    def test_remove_worker_during_ramp_up(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes=user_classes)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 1, "User2": 1, "User3": 1})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 1)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 1)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 1)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 2)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.remove_worker(worker_nodes[1])

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

    def test_remove_two_workers_during_ramp_up(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes=user_classes)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 1, "User2": 1, "User3": 1})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 1)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 1)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 1)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 2)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.remove_worker(worker_nodes[1])
        users_dispatcher.remove_worker(worker_nodes[2])

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 9)

    def test_remove_worker_between_two_ramp_ups(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = 0

        list(users_dispatcher)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.remove_worker(worker_nodes[1])

        self.assertTrue(users_dispatcher._rebalance)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 6)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 5, "User2": 5, "User3": 5})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 8)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 7)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 6, "User2": 6, "User3": 6})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 9)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 9)

    def test_remove_two_workers_between_two_ramp_ups(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = 0

        list(users_dispatcher)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.remove_worker(worker_nodes[1])
        users_dispatcher.remove_worker(worker_nodes[2])

        self.assertTrue(users_dispatcher._rebalance)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 9)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 12)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 5, "User2": 5, "User3": 5})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 15)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 6, "User2": 6, "User3": 6})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 18)

    def test_remove_worker_during_ramp_down(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 5, "User2": 5, "User3": 5})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 5)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.remove_worker(worker_nodes[1])

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 6)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

    def test_remove_two_workers_during_ramp_down(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 5, "User2": 5, "User3": 5})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 5)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.remove_worker(worker_nodes[1])
        users_dispatcher.remove_worker(worker_nodes[2])

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 12)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 9)

    def test_remove_last_worker(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(1)]

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = 0

        # Dispatch iteration 1
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 1, "User2": 1, "User3": 1})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)

        # Dispatch iteration 2
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.remove_worker(worker_nodes[0])

        self.assertFalse(users_dispatcher._rebalance)


class TestAddWorker(unittest.TestCase):
    def test_add_worker_during_ramp_up(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [
            WorkerNode("hostname1_worker1"),
            WorkerNode("hostname1_worker2"),
            WorkerNode("hostname2_worker1"),
        ]

        users_dispatcher = UsersDispatcher(worker_nodes=[worker_nodes[0], worker_nodes[2]], user_classes=user_classes)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=11, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 1, "User2": 1, "User3": 1})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 1)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.add_worker(worker_nodes[1])

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 2)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

        # Dispatch iteration 4
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 4)
        # without host-based balancing the following two values would be reversed
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

    def test_add_two_workers_during_ramp_up(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=[worker_nodes[0]], user_classes=user_classes)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 1, "User2": 1, "User3": 1})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.add_worker(worker_nodes[1])
        users_dispatcher.add_worker(worker_nodes[2])

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 2)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

    def test_add_worker_between_two_ramp_ups(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=[worker_nodes[0], worker_nodes[2]], user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = 0

        list(users_dispatcher)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.add_worker(worker_nodes[1])

        self.assertTrue(users_dispatcher._rebalance)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 5, "User2": 5, "User3": 5})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 5)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 6, "User2": 6, "User3": 6})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 6)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 6)

    def test_add_two_workers_between_two_ramp_ups(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=[worker_nodes[0]], user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = 0

        list(users_dispatcher)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.add_worker(worker_nodes[1])
        users_dispatcher.add_worker(worker_nodes[2])

        self.assertTrue(users_dispatcher._rebalance)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 5, "User2": 5, "User3": 5})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 5)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 6, "User2": 6, "User3": 6})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 6)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 6)

    def test_add_worker_during_ramp_down(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=[worker_nodes[0], worker_nodes[2]], user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 5, "User2": 5, "User3": 5})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 8)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 7)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 6)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.add_worker(worker_nodes[1])

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

    def test_add_two_workers_during_ramp_down(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        worker_nodes = [WorkerNode(str(i + 1)) for i in range(3)]

        users_dispatcher = UsersDispatcher(worker_nodes=[worker_nodes[0]], user_classes=user_classes)

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = 0
        list(users_dispatcher)

        sleep_time = 0.2  # Speed-up test

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)
        users_dispatcher._wait_between_dispatch = sleep_time

        # Dispatch iteration 1
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 5, "User2": 5, "User3": 5})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 15)

        # Dispatch iteration 2
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 12)

        self.assertFalse(users_dispatcher._rebalance)

        users_dispatcher.add_worker(worker_nodes[1])
        users_dispatcher.add_worker(worker_nodes[2])

        self.assertTrue(users_dispatcher._rebalance)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, f"Expected re-balance dispatch to be instantaneous but got {delta}s")
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

        self.assertFalse(users_dispatcher._rebalance)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)


class TestRampUpUsersFromZeroWithFixed(unittest.TestCase):
    class RampUpCase:
        def __init__(self, fixed_counts: Tuple[int], weights: Tuple[int], target_user_count: int):
            self.fixed_counts = fixed_counts
            self.weights = weights
            self.target_user_count = target_user_count

        def __str__(self):
            return "<RampUpCase fixed_counts={} weights={} target_user_count={}>".format(
                self.fixed_counts, self.weights, self.target_user_count
            )

    def case_handler(self, cases: List[RampUpCase], expected: List[Dict[str, int]], user_classes: List[Type[User]]):
        self.assertEqual(len(cases), len(expected))

        for case_num in range(len(cases)):
            # Reset to default values
            for user_class in user_classes:
                user_class.weight, user_class.fixed_count = 1, 0

            case = cases[case_num]
            self.assertEqual(
                len(case.fixed_counts) + len(case.weights),
                len(user_classes),
                msg="Invalid test case or user list.",
            )

            fixed_users = user_classes[: len(case.fixed_counts)]
            weighted_users_list = user_classes[len(case.fixed_counts) :]

            for user, fixed_count in zip(fixed_users, case.fixed_counts):
                user.fixed_count = fixed_count

            for user, weight in zip(weighted_users_list, case.weights):
                user.weight = weight

            worker_node1 = WorkerNode("1")

            users_dispatcher = UsersDispatcher(worker_nodes=[worker_node1], user_classes=user_classes)
            users_dispatcher.new_dispatch(target_user_count=case.target_user_count, spawn_rate=0.5)
            users_dispatcher._wait_between_dispatch = 0

            iterations = list(users_dispatcher)
            self.assertDictEqual(iterations[-1]["1"], expected[case_num], msg=f"Wrong case {case}")

    def test_ramp_up_2_weigted_user_with_1_fixed_user(self):
        class User1(User):
            ...

        class User2(User):
            ...

        class User3(User):
            ...

        self.case_handler(
            cases=[
                self.RampUpCase(fixed_counts=(1,), weights=(1, 1), target_user_count=3),
                self.RampUpCase(fixed_counts=(1,), weights=(1, 1), target_user_count=9),
                self.RampUpCase(fixed_counts=(8,), weights=(1, 1), target_user_count=10),
                self.RampUpCase(fixed_counts=(2,), weights=(1, 1), target_user_count=1000),
                self.RampUpCase(fixed_counts=(100,), weights=(1, 1), target_user_count=1000),
                self.RampUpCase(fixed_counts=(960,), weights=(1, 1), target_user_count=1000),
                self.RampUpCase(fixed_counts=(9990,), weights=(1, 1), target_user_count=10000),
                self.RampUpCase(fixed_counts=(100,), weights=(1, 1), target_user_count=100),
            ],
            expected=[
                {"User1": 1, "User2": 1, "User3": 1},
                {"User1": 1, "User2": 4, "User3": 4},
                {"User1": 8, "User2": 1, "User3": 1},
                {"User1": 2, "User2": 499, "User3": 499},
                {"User1": 100, "User2": 450, "User3": 450},
                {"User1": 960, "User2": 20, "User3": 20},
                {"User1": 9990, "User2": 5, "User3": 5},
                {"User1": 100, "User2": 0, "User3": 0},
            ],
            user_classes=[User1, User2, User3],
        )

    def test_ramp_up_various_count_weigted_and_fixed_users(self):
        class User1(User):
            ...

        class User2(User):
            ...

        class User3(User):
            ...

        class User4(User):
            ...

        class User5(User):
            ...

        self.case_handler(
            cases=[
                self.RampUpCase(fixed_counts=(), weights=(1, 1, 1, 1, 1), target_user_count=5),
                self.RampUpCase(fixed_counts=(1, 1), weights=(1, 1, 1), target_user_count=5),
                self.RampUpCase(fixed_counts=(5, 2), weights=(1, 1, 1), target_user_count=10),
                self.RampUpCase(fixed_counts=(9, 1), weights=(5, 3, 2), target_user_count=20),
                self.RampUpCase(fixed_counts=(996,), weights=(1, 1, 1, 1), target_user_count=1000),
                self.RampUpCase(fixed_counts=(500,), weights=(2, 1, 1, 1), target_user_count=1000),
                self.RampUpCase(fixed_counts=(250, 250), weights=(3, 1, 1), target_user_count=1000),
                self.RampUpCase(fixed_counts=(1, 1, 1, 1), weights=(100,), target_user_count=1000),
            ],
            expected=[
                {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 1},
                {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 1},
                {"User1": 5, "User2": 2, "User3": 1, "User4": 1, "User5": 1},
                {"User1": 9, "User2": 1, "User3": 5, "User4": 3, "User5": 2},
                {"User1": 996, "User2": 1, "User3": 1, "User4": 1, "User5": 1},
                {"User1": 500, "User2": 200, "User3": 100, "User4": 100, "User5": 100},
                {"User1": 250, "User2": 250, "User3": 300, "User4": 100, "User5": 100},
                {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 996},
            ],
            user_classes=[User1, User2, User3, User4, User5],
        )

    def test_ramp_up_only_fixed_users(self):
        class User1(User):
            ...

        class User2(User):
            ...

        class User3(User):
            ...

        class User4(User):
            ...

        class User5(User):
            ...

        self.case_handler(
            cases=[
                self.RampUpCase(fixed_counts=(1, 1, 1, 1, 1), weights=(), target_user_count=5),
                self.RampUpCase(fixed_counts=(13, 26, 39, 52, 1), weights=(), target_user_count=131),
                self.RampUpCase(fixed_counts=(10, 10, 10, 10, 10), weights=(), target_user_count=100),
                self.RampUpCase(fixed_counts=(10, 10, 10, 10, 10), weights=(), target_user_count=50),
            ],
            expected=[
                {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 1},
                {"User1": 13, "User2": 26, "User3": 39, "User4": 52, "User5": 1},
                {"User1": 10, "User2": 10, "User3": 10, "User4": 10, "User5": 10},
                {"User1": 10, "User2": 10, "User3": 10, "User4": 10, "User5": 10},
            ],
            user_classes=[User1, User2, User3, User4, User5],
        )

    def test_ramp_up_partially_ramp_down_and_rump_up_to_target(self):
        class User1(User):
            fixed_count = 50

        class User2(User):
            fixed_count = 50

        target_count = User1.fixed_count + User2.fixed_count

        users_dispatcher = UsersDispatcher(worker_nodes=[WorkerNode("1")], user_classes=[User1, User2])
        users_dispatcher.new_dispatch(target_user_count=30, spawn_rate=0.5)
        users_dispatcher._wait_between_dispatch = 0
        iterations = list(users_dispatcher)
        self.assertDictEqual(iterations[-1]["1"], {"User1": 15, "User2": 15})

        users_dispatcher.new_dispatch(target_user_count=20, spawn_rate=0.5)
        users_dispatcher._wait_between_dispatch = 0
        iterations = list(users_dispatcher)
        self.assertDictEqual(iterations[-1]["1"], {"User1": 10, "User2": 10})

        users_dispatcher.new_dispatch(target_user_count=target_count, spawn_rate=0.5)
        users_dispatcher._wait_between_dispatch = 0
        iterations = list(users_dispatcher)
        self.assertDictEqual(iterations[-1]["1"], {"User1": 50, "User2": 50})

    def test_ramp_up_ramp_down_and_rump_up_again(self):
        for weights, fixed_counts in [
            [(1, 1, 1, 1, 1), (100, 100, 50, 50, 200)],
            [(1, 1, 1, 1, 1), (100, 150, 50, 50, 0)],
            [(1, 1, 1, 1, 1), (200, 100, 50, 0, 0)],
            [(1, 1, 1, 1, 1), (200, 100, 0, 0, 0)],
            [(1, 1, 1, 1, 1), (200, 0, 0, 0, 0)],
            [(1, 1, 1, 1, 1), (0, 0, 0, 0, 0)],
        ]:

            u1_weight, u2_weight, u3_weight, u4_weight, u5_weight = weights
            u1_fixed_count, u2_fixed_count, u3_fixed_count, u4_fixed_count, u5_fixed_count = fixed_counts

            class User1(User):
                weight = u1_weight
                fixed_count = u1_fixed_count

            class User2(User):
                weight = u2_weight
                fixed_count = u2_fixed_count

            class User3(User):
                weight = u3_weight
                fixed_count = u3_fixed_count

            class User4(User):
                weight = u4_weight
                fixed_count = u4_fixed_count

            class User5(User):
                weight = u5_weight
                fixed_count = u5_fixed_count

            target_user_counts = [sum(fixed_counts), sum(fixed_counts) + 100]
            down_counts = [0, max(min(fixed_counts) - 1, 0)]
            user_classes = [User1, User2, User3, User4, User5]

            for worker_count in [3, 5, 9]:
                workers = [WorkerNode(str(i + 1)) for i in range(worker_count)]
                users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=user_classes)

                for down_to_count in down_counts:
                    for target_user_count in target_user_counts:

                        # Ramp-up to go to `target_user_count` #########

                        users_dispatcher.new_dispatch(target_user_count=target_user_count, spawn_rate=1)
                        users_dispatcher._wait_between_dispatch = 0

                        list(users_dispatcher)

                        for user_class in user_classes:
                            if user_class.fixed_count:
                                self.assertEqual(
                                    users_dispatcher._get_user_current_count(user_class.__name__),
                                    user_class.fixed_count,
                                )

                        # Ramp-down to go to `down_to_count`
                        # and ensure the fixed users was decreased too

                        users_dispatcher.new_dispatch(target_user_count=down_to_count, spawn_rate=1)
                        users_dispatcher._wait_between_dispatch = 0

                        list(users_dispatcher)

                        for user_class in user_classes:
                            if user_class.fixed_count:
                                self.assertNotEqual(
                                    users_dispatcher._get_user_current_count(user_class.__name__),
                                    user_class.fixed_count,
                                )

                        # Ramp-up go back to `target_user_count` and ensure
                        # the fixed users return to their counts

                        users_dispatcher.new_dispatch(target_user_count=target_user_count, spawn_rate=1)
                        users_dispatcher._wait_between_dispatch = 0

                        list(users_dispatcher)

                        for user_class in user_classes:
                            if user_class.fixed_count:
                                self.assertEqual(
                                    users_dispatcher._get_user_current_count(user_class.__name__),
                                    user_class.fixed_count,
                                )


def _aggregate_dispatched_users(d: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    user_classes = list(next(iter(d.values())).keys())
    return {u: sum(d[u] for d in d.values()) for u in user_classes}


def _user_count(d: Dict[str, Dict[str, int]]) -> int:
    return sum(map(sum, map(dict.values, d.values())))  # type: ignore


def _user_count_on_worker(d: Dict[str, Dict[str, int]], worker_node_id: str) -> int:
    return sum(d[worker_node_id].values())
