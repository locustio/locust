import time
import unittest
from operator import attrgetter
from typing import Dict

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

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=0.5)

        sleep_time = 1 / 0.5

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

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=1)

        sleep_time = 1

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

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3, worker_node4], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=1)

        sleep_time = 1

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

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=2)

        sleep_time = 1

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

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=2.4)

        sleep_time = 2 / 2.4

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

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)

        sleep_time = 1

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

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=4)

        sleep_time = 1

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

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3], user_classes=[User1, User2, User3]
        )
        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=9)

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

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=0.5)

        sleep_time = 1 / 0.5

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

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=1)

        sleep_time = 1

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

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=1)

        sleep_time = 1

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

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=2)

        sleep_time = 1

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

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=2.4)

        sleep_time = 2 / 2.4

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

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=3)

        sleep_time = 1

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

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=4)

        sleep_time = 1

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

        users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=9)

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
        for user1_weight, user2_weight, user3_weight, user4_weight, user5_weight, user6_weight in [
            (1, 1, 1, 1, 1, 1),
            (1, 2, 3, 4, 5, 6),
            (1, 3, 5, 7, 9, 12),
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

            class User6(User):
                weight = user6_weight

            all_user_classes = [User1, User2, User3, User4, User5, User6]

            for number_of_user_classes in range(1, len(all_user_classes) + 1):
                user_classes = all_user_classes[:number_of_user_classes]

                for max_user_count, min_user_count in [(30, 15), (45, 15), (54, 21), (14165, 1476)]:
                    for worker_count in [1, 3, 4, 5, 9]:
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

            users_dispatcher.new_dispatch(target_user_count=user_count, spawn_rate=spawn_rate)

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
    class User01(User):
        weight = 5

    class User02(User):
        weight = 55

    class User03(User):
        weight = 37

    class User04(User):
        weight = 2

    class User05(User):
        weight = 97

    class User06(User):
        weight = 41

    class User07(User):
        weight = 33

    class User08(User):
        weight = 19

    class User09(User):
        weight = 19

    class User10(User):
        weight = 34

    class User11(User):
        weight = 78

    class User12(User):
        weight = 76

    class User13(User):
        weight = 28

    class User14(User):
        weight = 62

    class User15(User):
        weight = 69

    class User16(User):
        weight = 5

    class User17(User):
        weight = 55

    class User18(User):
        weight = 37

    class User19(User):
        weight = 2

    class User20(User):
        weight = 97

    class User21(User):
        weight = 41

    class User22(User):
        weight = 33

    class User23(User):
        weight = 19

    class User24(User):
        weight = 19

    class User25(User):
        weight = 34

    class User26(User):
        weight = 78

    class User27(User):
        weight = 76

    class User28(User):
        weight = 28

    class User29(User):
        weight = 62

    class User30(User):
        weight = 69

    class User31(User):
        weight = 41

    class User32(User):
        weight = 33

    class User33(User):
        weight = 19

    class User34(User):
        weight = 19

    class User35(User):
        weight = 34

    class User36(User):
        weight = 78

    class User37(User):
        weight = 76

    class User38(User):
        weight = 28

    class User39(User):
        weight = 62

    class User40(User):
        weight = 69

    class User41(User):
        weight = 41

    class User42(User):
        weight = 33

    class User43(User):
        weight = 19

    class User44(User):
        weight = 19

    class User45(User):
        weight = 34

    class User46(User):
        weight = 78

    class User47(User):
        weight = 76

    class User48(User):
        weight = 28

    class User49(User):
        weight = 62

    class User50(User):
        weight = 69

    user_classes = [
        User01,
        User02,
        User03,
        User04,
        User05,
        User06,
        User07,
        User08,
        User09,
        User10,
        User11,
        User12,
        User13,
        User14,
        User15,
        User16,
        User17,
        User18,
        User19,
        User20,
        User21,
        User22,
        User23,
        User24,
        User25,
        User26,
        User27,
        User28,
        User29,
        User30,
        User31,
        User32,
        User33,
        User34,
        User35,
        User36,
        User37,
        User38,
        User39,
        User40,
        User41,
        User42,
        User43,
        User44,
        User45,
        User46,
        User47,
        User48,
        User49,
        User50,
    ]

    def test_distribute_users(self):
        workers = [WorkerNode(str(i)) for i in range(10_000)]

        target_user_count = 1_000_000

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=self.user_classes)

        ts = time.perf_counter()
        users_on_workers, user_gen, worker_gen, active_users = users_dispatcher._distribute_users(
            target_user_count=target_user_count
        )
        delta = time.perf_counter() - ts

        # Because tests are run with coverage, the code will be slower.
        # We set the pass criterion to 5000ms, but in real life, the
        # `_distribute_users` method runs faster than this.
        self.assertLessEqual(1000 * delta, 5000)

        self.assertEqual(_user_count(users_on_workers), target_user_count)

    def test_ramp_up_from_0_to_100_000_users_with_50_user_classes_and_1000_workers_and_5000_spawn_rate(self):
        workers = [WorkerNode(str(i)) for i in range(1000)]

        target_user_count = 100_000

        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=self.user_classes)
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
            user_count_on_workers = [sum(user_classes_count.values()) for user_classes_count in dispatch_users.values()]
            self.assertLessEqual(
                max(user_count_on_workers) - min(user_count_on_workers),
                1,
                "One or more workers have too much users compared to the other workers when user count is {}".format(
                    _user_count(dispatch_users)
                ),
            )

        for i, dispatch_users in enumerate(all_dispatched_users):
            aggregated_dispatched_users = _aggregate_dispatched_users(dispatch_users)
            for user_class in self.user_classes:
                target_relative_weight = user_class.weight / sum(map(attrgetter("weight"), self.user_classes))
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
        initial_user_count = 100_000

        workers = [WorkerNode(str(i)) for i in range(1000)]

        # Ramp-up
        users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=self.user_classes)
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
            user_count_on_workers = [sum(user_classes_count.values()) for user_classes_count in dispatch_users.values()]
            self.assertLessEqual(
                max(user_count_on_workers) - min(user_count_on_workers),
                1,
                "One or more workers have too much users compared to the other workers when user count is {}".format(
                    _user_count(dispatch_users)
                ),
            )

        for dispatch_users in all_dispatched_users[:-1]:
            aggregated_dispatched_users = _aggregate_dispatched_users(dispatch_users)
            for user_class in self.user_classes:
                target_relative_weight = user_class.weight / sum(map(attrgetter("weight"), self.user_classes))
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

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)

        sleep_time = 1

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

        users_dispatcher.remove_worker(worker_nodes[1].id)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

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

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)

        sleep_time = 1

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

        users_dispatcher.remove_worker(worker_nodes[1].id)
        users_dispatcher.remove_worker(worker_nodes[2].id)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)

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

        users_dispatcher.remove_worker(worker_nodes[1].id)

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)

        sleep_time = 1

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 5)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

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

        users_dispatcher.remove_worker(worker_nodes[1].id)
        users_dispatcher.remove_worker(worker_nodes[2].id)

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)

        sleep_time = 1

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 9)

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

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)

        sleep_time = 1

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

        users_dispatcher.remove_worker(worker_nodes[1].id)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 6)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 6)

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

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)

        sleep_time = 1

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

        users_dispatcher.remove_worker(worker_nodes[1].id)
        users_dispatcher.remove_worker(worker_nodes[2].id)

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 12)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 9)


class TestAddWorker(unittest.TestCase):
    def test_add_worker_during_ramp_up(self):
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

        sleep_time = 1

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

        users_dispatcher.add_worker(worker_nodes[1])

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 2)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

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

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)

        sleep_time = 1

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

        users_dispatcher.add_worker(worker_nodes[1])
        users_dispatcher.add_worker(worker_nodes[2])

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 2, "User2": 2, "User3": 2})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 2)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 2)

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

        users_dispatcher.add_worker(worker_nodes[1])

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)

        sleep_time = 1

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

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

        users_dispatcher.add_worker(worker_nodes[1])
        users_dispatcher.add_worker(worker_nodes[2])

        users_dispatcher.new_dispatch(target_user_count=18, spawn_rate=3)

        sleep_time = 1

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)

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

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)

        sleep_time = 1

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

        users_dispatcher.add_worker(worker_nodes[1])

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

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

        users_dispatcher.new_dispatch(target_user_count=9, spawn_rate=3)

        sleep_time = 1

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

        users_dispatcher.add_worker(worker_nodes[1])
        users_dispatcher.add_worker(worker_nodes[2])

        # Re-balance
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= _TOLERANCE, "Expected re-balance dispatch to be instantaneous but got {}s".format(delta)
        )
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 4, "User3": 4})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 4)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 4)

        # Dispatch iteration 3
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 3, "User2": 3, "User3": 3})
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[0].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[1].id), 3)
        self.assertEqual(_user_count_on_worker(dispatched_users, worker_nodes[2].id), 3)


def _aggregate_dispatched_users(d: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    user_classes = list(next(iter(d.values())).keys())
    return {u: sum(d[u] for d in d.values()) for u in user_classes}


def _user_count(d: Dict[str, Dict[str, int]]) -> int:
    return sum(map(sum, map(dict.values, d.values())))


def _user_count_on_worker(d: Dict[str, Dict[str, int]], worker_node_id: str) -> int:
    return sum(d[worker_node_id].values())
