import itertools
import json
import math
import time
import unittest
from operator import attrgetter
from typing import Dict, List, Type

from locust import User
from locust.dispatch import UsersDispatcher
from locust.runners import WorkerNode
from locust.test.util import clear_all_functools_lru_cache

_TOLERANCE = 0.025


# TODO: Test case when `previous_target_user_count` is good but users on one or more workers is not as expected.


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
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes=[User1, User2, User3],
            previous_target_user_count=0,
            target_user_count=9,
            spawn_rate=0.5,
        )

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
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes=[User1, User2, User3],
            previous_target_user_count=0,
            target_user_count=9,
            spawn_rate=1,
        )

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
            worker_nodes=[worker_node1, worker_node2, worker_node3, worker_node4],
            user_classes=[User1, User2, User3],
            previous_target_user_count=0,
            target_user_count=9,
            spawn_rate=1,
        )

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
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes=[User1, User2, User3],
            previous_target_user_count=0,
            target_user_count=9,
            spawn_rate=2,
        )

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
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes=[User1, User2, User3],
            previous_target_user_count=0,
            target_user_count=9,
            spawn_rate=2.4,
        )

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
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes=[User1, User2, User3],
            previous_target_user_count=0,
            target_user_count=9,
            spawn_rate=3,
        )

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
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes=[User1, User2, User3],
            previous_target_user_count=0,
            target_user_count=9,
            spawn_rate=4,
        )

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
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes=[User1, User2, User3],
            previous_target_user_count=0,
            target_user_count=9,
            spawn_rate=9,
        )

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

        previous_target_user_count = 9

        workers = _create_workers(worker_count=3, user_classes=user_classes, user_count=previous_target_user_count)

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=user_classes,
            previous_target_user_count=previous_target_user_count,
            target_user_count=0,
            spawn_rate=0.5,
        )

        sleep_time = 1 / 0.5

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
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
                "3": {"User1": 0, "User2": 0, "User3": 3},
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
                "1": {"User1": 1, "User2": 0, "User3": 0},
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
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
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
                "1": {"User1": 0, "User2": 0, "User3": 0},
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

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_1(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        previous_target_user_count = 9

        workers = _create_workers(worker_count=3, user_classes=user_classes, user_count=previous_target_user_count)

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=user_classes,
            previous_target_user_count=previous_target_user_count,
            target_user_count=0,
            spawn_rate=1,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 3, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
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
                "3": {"User1": 0, "User2": 0, "User3": 3},
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
                "1": {"User1": 1, "User2": 0, "User3": 0},
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
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 2},
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
                "1": {"User1": 0, "User2": 0, "User3": 0},
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

    def test_ramp_down_users_to_4_workers_with_spawn_rate_of_1(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        previous_target_user_count = 9

        workers = _create_workers(worker_count=4, user_classes=user_classes, user_count=previous_target_user_count)

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=user_classes,
            previous_target_user_count=previous_target_user_count,
            target_user_count=0,
            spawn_rate=1,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 1, "User3": 1},
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
                "1": {"User1": 0, "User2": 1, "User3": 1},
                "2": {"User1": 0, "User2": 0, "User3": 1},
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
                "1": {"User1": 0, "User2": 1, "User3": 1},
                "2": {"User1": 0, "User2": 0, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 0},
                "4": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 1, "User3": 1},
                "2": {"User1": 0, "User2": 0, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 0},
                "4": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 0, "User2": 0, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 0},
                "4": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 1, "User2": 0, "User3": 0},
                "4": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
                "4": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
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

        previous_target_user_count = 9

        workers = _create_workers(worker_count=3, user_classes=user_classes, user_count=previous_target_user_count)

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=user_classes,
            previous_target_user_count=previous_target_user_count,
            target_user_count=0,
            spawn_rate=2,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
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

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_2_4(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        previous_target_user_count = 9

        workers = _create_workers(worker_count=3, user_classes=user_classes, user_count=previous_target_user_count)

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=user_classes,
            previous_target_user_count=previous_target_user_count,
            target_user_count=0,
            spawn_rate=2.4,
        )

        sleep_time = 2 / 2.4

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 2, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 2, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
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

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_3(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        previous_target_user_count = 9

        workers = _create_workers(worker_count=3, user_classes=user_classes, user_count=previous_target_user_count)

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=user_classes,
            previous_target_user_count=previous_target_user_count,
            target_user_count=0,
            spawn_rate=3,
        )

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

        previous_target_user_count = 9

        workers = _create_workers(worker_count=3, user_classes=user_classes, user_count=previous_target_user_count)

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=user_classes,
            previous_target_user_count=previous_target_user_count,
            target_user_count=0,
            spawn_rate=4,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
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
                "1": {"User1": 0, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
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

    def test_ramp_down_users_to_3_workers_with_spawn_rate_of_9(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes = [User1, User2, User3]

        previous_target_user_count = 9

        workers = _create_workers(worker_count=3, user_classes=user_classes, user_count=previous_target_user_count)

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=user_classes,
            previous_target_user_count=previous_target_user_count,
            target_user_count=0,
            spawn_rate=9,
        )

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


class TestRampUpWithWorkersHavingIncorrectUsers(unittest.TestCase):
    # TODO
    def test_more_total_users_and_incorrect_distribution(self):
        self.assertTrue(False)

    # TODO
    def test_less_total_users_and_incorrect_distribution(self):
        self.assertTrue(False)

    # TODO
    def test_good_user_count_but_incorrect_distribution(self):
        self.assertTrue(False)


class TestRampDownWithWorkersHavingIncorrectUsers(unittest.TestCase):
    # TODO
    def test_more_total_users_and_incorrect_distribution(self):
        self.assertTrue(False)

    # TODO
    def test_less_total_users_and_incorrect_distribution(self):
        self.assertTrue(False)

    # TODO
    def test_good_user_count_but_incorrect_distribution(self):
        self.assertTrue(False)


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

        workers = _create_workers(worker_count=3, user_classes=user_classes, user_count=user_count)

        for spawn_rate in [0.15, 0.5, 1, 2, 2.4, 3, 4, 9]:
            users_dispatcher = UsersDispatcher(
                worker_nodes=workers,
                user_classes=user_classes,
                previous_target_user_count=user_count,
                target_user_count=user_count,
                spawn_rate=spawn_rate,
            )

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
            worker_nodes=[worker_node1, worker_node2, worker_node3, worker_node4],
            user_classes=[User1, User2],
            previous_target_user_count=0,
            target_user_count=75,
            spawn_rate=5,
        )

        sleep_time = 1

        # total user count = 5
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        # total user count = 10
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 15
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 20
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 25
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 30
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 35
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 40
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 45
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 50
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 55
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 60
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 65
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 70
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 75, User1 = 25, User2 = 50
        ts = time.perf_counter()
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
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)


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

    def test_ramp_up_from_0_to_100_000_users_with_50_user_classes_and_1000_workers_and_5000_spawn_rate(self):
        workers = [WorkerNode(str(i)) for i in range(1000)]

        target_user_count = 100_000

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=self.user_classes,
            previous_target_user_count=0,
            target_user_count=target_user_count,
            spawn_rate=5000,
        )

        all_dispatched_users = list(users_dispatcher)

        self.assertTrue(
            all(
                dispatch_iteration_duration <= 0.3
                for dispatch_iteration_duration in users_dispatcher.dispatch_iteration_durations
            ),
            "One or more dispatch took more than 300ms to compute",
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
        previous_target_user_count = 100_000

        workers = _create_workers(
            worker_count=1000, user_classes=self.user_classes, user_count=previous_target_user_count
        )

        users_dispatcher = UsersDispatcher(
            worker_nodes=workers,
            user_classes=self.user_classes,
            previous_target_user_count=previous_target_user_count,
            target_user_count=0,
            spawn_rate=5000,
        )

        all_dispatched_users = list(users_dispatcher)

        self.assertTrue(
            all(
                dispatch_iteration_duration <= 0.3
                for dispatch_iteration_duration in users_dispatcher.dispatch_iteration_durations
            ),
            "One or more dispatch took more than 300ms to compute",
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


def _create_workers(worker_count: int, user_classes: List[Type[User]], user_count: int = 0) -> List[WorkerNode]:
    workers = [WorkerNode(str(i)) for i in range(1, worker_count + 1)]

    if user_count == 0:
        return workers

    dispatched_users = next(
        UsersDispatcher(
            worker_nodes=workers,
            user_classes=user_classes,
            previous_target_user_count=0,
            target_user_count=user_count,
            spawn_rate=user_count,
        )
    )

    assert _user_count(dispatched_users) == user_count

    user_count_on_workers = [sum(user_classes_count.values()) for user_classes_count in dispatched_users.values()]
    assert (
        max(user_count_on_workers) - min(user_count_on_workers) <= 1
    ), "One or more workers have too much users compared to the other workers"

    aggregated_dispatched_users = _aggregate_dispatched_users(dispatched_users)
    for user_class in user_classes:
        target_relative_weight = user_class.weight / sum(map(attrgetter("weight"), user_classes))
        relative_weight = aggregated_dispatched_users[user_class.__name__] / user_count
        error_percent = 100 * (relative_weight - target_relative_weight) / target_relative_weight
        assert error_percent <= 0.5, "Distribution for user class {} is off by more than 0.5%".format(user_class)

    for worker in workers:
        worker.user_classes_count = dispatched_users[worker.id]

    return workers


@unittest.skip
class TestDispatchUsersToWorkersHavingLessUsersThanTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        sleep_time = 1 / 0.5

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2.4,
        )

        sleep_time = 2 / 2.4

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_5_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {"User1": 1, "User2": 1, "User3": 0}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1, "User2": 1, "User3": 0}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User1": 1, "User2": 1, "User3": 0}
        worker_node4 = WorkerNode("4")
        worker_node4.user_classes_count = {"User1": 1, "User2": 0, "User3": 1}
        worker_node5 = WorkerNode("5")
        worker_node5.user_classes_count = {"User1": 0, "User2": 0, "User3": 2}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3, worker_node4, worker_node5],
            user_classes_count={"User1": 5, "User2": 5, "User3": 5},
            spawn_rate=3,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 1, "User2": 1, "User3": 0},
                "4": {"User1": 1, "User2": 1, "User3": 1},
                "5": {"User1": 1, "User2": 0, "User3": 2},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
                "4": {"User1": 1, "User2": 1, "User3": 1},
                "5": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)


@unittest.skip
class TestDispatchUsersToWorkersHavingLessAndMoreUsersThanTheTargetAndMoreTotalUsers(unittest.TestCase):
    """
    Test scenario with:
        - Already more total users running than desired
        - Some workers already have more users than desired
        - Some workers have less users than desired
    """

    def test_dispatch_users_to_3_workers(self):
        for worker_node1_user_classes_count in [{}, {"User3": 1}]:
            worker_node1 = WorkerNode("1")
            worker_node1.user_classes_count = worker_node1_user_classes_count
            worker_node2 = WorkerNode("2")
            worker_node2.user_classes_count = {"User1": 5}
            worker_node3 = WorkerNode("3")
            worker_node3.user_classes_count = {"User2": 7}

            for spawn_rate in [0.5, 1, 2, 2.4, 3, 4, 9]:
                users_dispatcher = UsersDispatcher(
                    worker_nodes=[worker_node1, worker_node2, worker_node3],
                    user_classes_count={"User1": 3, "User2": 3, "User3": 3},
                    spawn_rate=spawn_rate,
                )

                ts = time.perf_counter()
                self.assertDictEqual(
                    next(users_dispatcher),
                    {
                        "1": {"User1": 1, "User2": 1, "User3": 1},
                        "2": {"User1": 1, "User2": 1, "User3": 1},
                        "3": {"User1": 1, "User2": 1, "User3": 1},
                    },
                )
                delta = time.perf_counter() - ts
                self.assertTrue(0 <= delta <= _TOLERANCE, delta)

                ts = time.perf_counter()
                self.assertRaises(StopIteration, lambda: next(users_dispatcher))
                delta = time.perf_counter() - ts
                self.assertTrue(0 <= delta <= _TOLERANCE, delta)

                clear_all_functools_lru_cache()


@unittest.skip
class TestDispatchUsersToWorkersHavingLessAndMoreUsersThanTheTargetAndLessTotalUsers(unittest.TestCase):
    """
    Test scenario with:
        - Some users are already but there are less total users running than desired
        - Some workers already have more users than desired
        - Some workers have less users than desired
    """

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5_and_one_worker_empty(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 4}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 4}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        sleep_time = 1 / 0.5

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 4, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 4, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1_and_one_worker_empty(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 4}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 4}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 4, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 4, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5_and_all_workers_non_empty(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {"User3": 1}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 3}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 4}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1_and_all_workers_non_empty(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {"User3": 1}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 3}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 4}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5_and_all_workers_non_empty_and_one_user_class_requiring_no_change(
        self,
    ):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {"User1": 1, "User3": 1}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User1": 1, "User2": 4}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        sleep_time = 1 / 0.5

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 1},
                "3": {"User1": 1, "User2": 4, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1_and_all_workers_non_empty_and_one_user_class_requiring_no_change(
        self,
    ):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {"User1": 1, "User3": 1}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User1": 1, "User2": 4}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        sleep_time = 1

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 1},
                "3": {"User1": 1, "User2": 4, "User3": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_greater_than_or_equal_to_2(self):
        worker_node1_user_classes_count_cases = [{}, {"User3": 1}, {"User3": 2}]
        worker_node2_user_classes_count_cases = [{"User1": 4}, {"User1": 3}, {"User1": 3}]
        worker_node3_user_classes_count_cases = [{"User2": 4}, {"User2": 3}, {"User2": 3}]
        for (worker_node1_user_classes_count, worker_node2_user_classes_count, worker_node3_user_classes_count) in zip(
            worker_node1_user_classes_count_cases,
            worker_node2_user_classes_count_cases,
            worker_node3_user_classes_count_cases,
        ):
            worker_node1 = WorkerNode("1")
            worker_node1.user_classes_count = worker_node1_user_classes_count
            worker_node2 = WorkerNode("2")
            worker_node2.user_classes_count = worker_node2_user_classes_count
            worker_node3 = WorkerNode("3")
            worker_node3.user_classes_count = worker_node3_user_classes_count

            for spawn_rate in [2, 2.4, 3, 4, 9]:
                users_dispatcher = UsersDispatcher(
                    worker_nodes=[worker_node1, worker_node2, worker_node3],
                    user_classes_count={"User1": 3, "User2": 3, "User3": 3},
                    spawn_rate=spawn_rate,
                )

                ts = time.perf_counter()
                self.assertDictEqual(
                    next(users_dispatcher),
                    {
                        "1": {"User1": 1, "User2": 1, "User3": 1},
                        "2": {"User1": 1, "User2": 1, "User3": 1},
                        "3": {"User1": 1, "User2": 1, "User3": 1},
                    },
                )
                delta = time.perf_counter() - ts
                self.assertTrue(0 <= delta <= _TOLERANCE, delta)

                ts = time.perf_counter()
                self.assertRaises(StopIteration, lambda: next(users_dispatcher))
                delta = time.perf_counter() - ts
                self.assertTrue(0 <= delta <= _TOLERANCE, delta)

                clear_all_functools_lru_cache()


@unittest.skip
class TestDispatchUsersToWorkersHavingMoreUsersThanTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers(self):
        worker_node1_user_classes_count_cases = [{"User3": 15}, {"User3": 3}]
        worker_node2_user_classes_count_cases = [{"User1": 5}, {"User1": 3}]
        worker_node3_user_classes_count_cases = [{"User2": 7}, {"User2": 3}]
        for (
            worker_node1_user_classes_count,
            worker_node2_user_classes_count,
            worker_node3_user_classes_count,
        ) in itertools.product(
            worker_node1_user_classes_count_cases,
            worker_node2_user_classes_count_cases,
            worker_node3_user_classes_count_cases,
        ):
            worker_node1 = WorkerNode("1")
            worker_node1.user_classes_count = worker_node1_user_classes_count
            worker_node2 = WorkerNode("2")
            worker_node2.user_classes_count = worker_node2_user_classes_count
            worker_node3 = WorkerNode("3")
            worker_node3.user_classes_count = worker_node3_user_classes_count

            for spawn_rate in [0.15, 0.5, 1, 2, 2.4, 3, 4, 9]:
                users_dispatcher = UsersDispatcher(
                    worker_nodes=[worker_node1, worker_node2, worker_node3],
                    user_classes_count={"User1": 3, "User2": 3, "User3": 3},
                    spawn_rate=spawn_rate,
                )

                ts = time.perf_counter()
                self.assertDictEqual(
                    next(users_dispatcher),
                    {
                        "1": {"User1": 1, "User2": 1, "User3": 1},
                        "2": {"User1": 1, "User2": 1, "User3": 1},
                        "3": {"User1": 1, "User2": 1, "User3": 1},
                    },
                )
                delta = time.perf_counter() - ts
                self.assertTrue(0 <= delta <= _TOLERANCE, delta)

                ts = time.perf_counter()
                self.assertRaises(StopIteration, lambda: next(users_dispatcher))
                delta = time.perf_counter() - ts
                self.assertTrue(0 <= delta <= _TOLERANCE, delta)

                clear_all_functools_lru_cache()


@unittest.skip
class TestDispatch(unittest.TestCase):
    """
    Class containing miscellaneous tests that were used to debug some issues observed when running real tests.
    """

    def test_dispatch_50_total_users_with_25_already_running_to_20_workers_with_spawn_rate_of_1(self):
        """
        Prior to 81f6d66cf69755ee966a26741e251ac560c78233, the dispatcher would have directly go from 25 to 50 users
        in one second due to bugs in the dispatcher. This test ensures that this problem can't
        reappear in the future.
        """
        # Prepend "0" to worker name under 10, because workers are sorted in alphabetical orders.
        # It's simply makes the test easier to read and debug, but in reality, the worker "10" would come
        # before worker "1".
        worker_nodes = [WorkerNode("0{}".format(i) if i < 10 else str(i)) for i in range(1, 21)]

        for worker_node in worker_nodes:
            worker_node.user_classes_count = {"User1": 0}

        worker_nodes_iterator = itertools.cycle(worker_nodes)
        user_count = 0
        while user_count < 25:
            next(worker_nodes_iterator).user_classes_count["User1"] += 1
            user_count += 1

        users_dispatcher = UsersDispatcher(worker_nodes=worker_nodes, user_classes_count={"User1": 50}, spawn_rate=1)

        sleep_time = 1

        for dispatch_iteration in range(25):
            ts = time.perf_counter()
            dispatched_users = next(users_dispatcher)
            self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 25 + dispatch_iteration + 1})
            delta = time.perf_counter() - ts
            if dispatch_iteration == 0:
                self.assertTrue(0 <= delta <= _TOLERANCE, delta)
            else:
                self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

    def test_dispatch_from_5_to_10_users_to_10_workers(self):
        """
        This test case was causing the dispatcher to go into an infinite loop.
        The test is left to prevent future regressions.
        """
        worker_nodes = [WorkerNode("0{}".format(i) if i < 10 else str(i)) for i in range(1, 11)]
        worker_nodes[1].user_classes_count = {"TestUser6": 1}
        worker_nodes[3].user_classes_count = {"TestUser4": 1}
        worker_nodes[4].user_classes_count = {"TestUser5": 1}
        worker_nodes[5].user_classes_count = {"TestUser10": 1}
        worker_nodes[9].user_classes_count = {"TestUser1": 1}

        user_classes_count = {
            "TestUser1": 1,
            "TestUser2": 1,
            "TestUser3": 1,
            "TestUser4": 1,
            "TestUser5": 1,
            "TestUser6": 1,
            "TestUser7": 1,
            "TestUser8": 1,
            "TestUser9": 1,
            "TestUser10": 1,
        }

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes, user_classes_count=user_classes_count, spawn_rate=1
        )

        dispatched_users = list(users_dispatcher)

        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users[-1]), user_classes_count)

    def test_dispatch_from_20_to_55_users_to_10_workers(self):
        """
        This test case was causing the dispatcher to go into an infinite loop.
        The test is left to prevent future regressions.
        """
        worker_nodes = [WorkerNode("0{}".format(i) if i < 10 else str(i)) for i in range(1, 11)]
        worker_nodes[0].user_classes_count = {
            "TestUser1": 1,
            "TestUser10": 1,
            "TestUser2": 0,
            "TestUser3": 0,
            "TestUser4": 0,
            "TestUser5": 0,
            "TestUser6": 0,
            "TestUser7": 0,
            "TestUser8": 0,
            "TestUser9": 0,
        }
        worker_nodes[1].user_classes_count = {
            "TestUser1": 0,
            "TestUser10": 1,
            "TestUser2": 1,
            "TestUser3": 0,
            "TestUser4": 0,
            "TestUser5": 0,
            "TestUser6": 0,
            "TestUser7": 0,
            "TestUser8": 0,
            "TestUser9": 0,
        }
        worker_nodes[2].user_classes_count = {
            "TestUser1": 0,
            "TestUser10": 0,
            "TestUser2": 1,
            "TestUser3": 1,
            "TestUser4": 0,
            "TestUser5": 0,
            "TestUser6": 0,
            "TestUser7": 0,
            "TestUser8": 0,
            "TestUser9": 0,
        }
        worker_nodes[3].user_classes_count = {
            "TestUser1": 0,
            "TestUser10": 0,
            "TestUser2": 0,
            "TestUser3": 0,
            "TestUser4": 1,
            "TestUser5": 1,
            "TestUser6": 0,
            "TestUser7": 0,
            "TestUser8": 0,
            "TestUser9": 0,
        }
        worker_nodes[4].user_classes_count = {
            "TestUser1": 0,
            "TestUser10": 0,
            "TestUser2": 0,
            "TestUser3": 0,
            "TestUser4": 1,
            "TestUser5": 1,
            "TestUser6": 0,
            "TestUser7": 0,
            "TestUser8": 0,
            "TestUser9": 0,
        }
        worker_nodes[5].user_classes_count = {
            "TestUser1": 0,
            "TestUser10": 0,
            "TestUser2": 0,
            "TestUser3": 0,
            "TestUser4": 1,
            "TestUser5": 1,
            "TestUser6": 0,
            "TestUser7": 0,
            "TestUser8": 0,
            "TestUser9": 0,
        }
        worker_nodes[6].user_classes_count = {
            "TestUser1": 0,
            "TestUser10": 0,
            "TestUser2": 0,
            "TestUser3": 0,
            "TestUser4": 0,
            "TestUser5": 0,
            "TestUser6": 1,
            "TestUser7": 1,
            "TestUser8": 0,
            "TestUser9": 0,
        }
        worker_nodes[7].user_classes_count = {
            "TestUser1": 0,
            "TestUser10": 0,
            "TestUser2": 0,
            "TestUser3": 0,
            "TestUser4": 0,
            "TestUser5": 0,
            "TestUser6": 1,
            "TestUser7": 0,
            "TestUser8": 1,
            "TestUser9": 0,
        }
        worker_nodes[8].user_classes_count = {
            "TestUser1": 0,
            "TestUser10": 0,
            "TestUser2": 0,
            "TestUser3": 0,
            "TestUser4": 0,
            "TestUser5": 0,
            "TestUser6": 1,
            "TestUser7": 0,
            "TestUser8": 0,
            "TestUser9": 1,
        }
        worker_nodes[9].user_classes_count = {
            "TestUser1": 0,
            "TestUser10": 0,
            "TestUser2": 0,
            "TestUser3": 0,
            "TestUser4": 0,
            "TestUser5": 0,
            "TestUser6": 1,
            "TestUser7": 0,
            "TestUser8": 0,
            "TestUser9": 1,
        }

        user_classes_count = {
            "TestUser1": 2,
            "TestUser10": 5,
            "TestUser2": 5,
            "TestUser3": 3,
            "TestUser4": 8,
            "TestUser5": 10,
            "TestUser6": 11,
            "TestUser7": 4,
            "TestUser8": 2,
            "TestUser9": 5,
        }

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes, user_classes_count=user_classes_count, spawn_rate=2
        )

        dispatched_users = list(users_dispatcher)

        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users[-1]), user_classes_count)

    def test_dispatch_from_38_to_61_users_to_10_workers(self):
        """
        This test case was causing the dispatcher to go into an infinite loop.
        The test is left to prevent future regressions.
        """
        worker_nodes = [WorkerNode("0{}".format(i) if i < 10 else str(i)) for i in range(1, 11)]
        worker_nodes[0].user_classes_count = {
            "TestUser01": 1,
            "TestUser02": 1,
            "TestUser03": 1,
            "TestUser05": 0,
            "TestUser06": 0,
            "TestUser07": 0,
            "TestUser08": 0,
            "TestUser09": 0,
            "TestUser10": 0,
            "TestUser11": 0,
            "TestUser12": 1,
            "TestUser14": 0,
            "TestUser15": 0,
        }
        worker_nodes[1].user_classes_count = {
            "TestUser01": 1,
            "TestUser02": 1,
            "TestUser03": 1,
            "TestUser05": 0,
            "TestUser06": 0,
            "TestUser07": 0,
            "TestUser08": 0,
            "TestUser09": 0,
            "TestUser10": 0,
            "TestUser11": 0,
            "TestUser12": 0,
            "TestUser14": 1,
            "TestUser15": 0,
        }
        worker_nodes[2].user_classes_count = {
            "TestUser01": 0,
            "TestUser02": 1,
            "TestUser03": 1,
            "TestUser05": 1,
            "TestUser06": 0,
            "TestUser07": 0,
            "TestUser08": 0,
            "TestUser09": 0,
            "TestUser10": 0,
            "TestUser11": 0,
            "TestUser12": 0,
            "TestUser14": 1,
            "TestUser15": 0,
        }
        worker_nodes[3].user_classes_count = {
            "TestUser01": 0,
            "TestUser02": 0,
            "TestUser03": 1,
            "TestUser05": 1,
            "TestUser06": 1,
            "TestUser07": 0,
            "TestUser08": 0,
            "TestUser09": 0,
            "TestUser10": 0,
            "TestUser11": 0,
            "TestUser12": 0,
            "TestUser14": 0,
            "TestUser15": 1,
        }
        worker_nodes[4].user_classes_count = {
            "TestUser01": 0,
            "TestUser02": 0,
            "TestUser03": 0,
            "TestUser05": 1,
            "TestUser06": 1,
            "TestUser07": 1,
            "TestUser08": 0,
            "TestUser09": 0,
            "TestUser10": 0,
            "TestUser11": 0,
            "TestUser12": 0,
            "TestUser14": 0,
            "TestUser15": 1,
        }
        worker_nodes[5].user_classes_count = {
            "TestUser01": 0,
            "TestUser02": 0,
            "TestUser03": 0,
            "TestUser05": 1,
            "TestUser06": 0,
            "TestUser07": 1,
            "TestUser08": 1,
            "TestUser09": 0,
            "TestUser10": 0,
            "TestUser11": 0,
            "TestUser12": 0,
            "TestUser14": 0,
            "TestUser15": 1,
        }
        worker_nodes[6].user_classes_count = {
            "TestUser01": 0,
            "TestUser02": 0,
            "TestUser03": 0,
            "TestUser05": 0,
            "TestUser06": 0,
            "TestUser07": 1,
            "TestUser08": 1,
            "TestUser09": 1,
            "TestUser10": 0,
            "TestUser11": 0,
            "TestUser12": 0,
            "TestUser14": 0,
            "TestUser15": 1,
        }
        worker_nodes[7].user_classes_count = {
            "TestUser01": 0,
            "TestUser02": 0,
            "TestUser03": 0,
            "TestUser05": 0,
            "TestUser06": 0,
            "TestUser07": 0,
            "TestUser08": 1,
            "TestUser09": 0,
            "TestUser10": 0,
            "TestUser11": 1,
            "TestUser12": 1,
            "TestUser14": 0,
            "TestUser15": 1,
        }
        worker_nodes[8].user_classes_count = {
            "TestUser01": 0,
            "TestUser02": 0,
            "TestUser03": 0,
            "TestUser05": 0,
            "TestUser06": 0,
            "TestUser07": 0,
            "TestUser08": 1,
            "TestUser09": 0,
            "TestUser10": 0,
            "TestUser11": 1,
            "TestUser12": 1,
            "TestUser14": 0,
            "TestUser15": 0,
        }
        worker_nodes[9].user_classes_count = {
            "TestUser01": 0,
            "TestUser02": 0,
            "TestUser03": 0,
            "TestUser05": 0,
            "TestUser06": 0,
            "TestUser07": 0,
            "TestUser08": 0,
            "TestUser09": 0,
            "TestUser10": 0,
            "TestUser11": 1,
            "TestUser12": 2,
            "TestUser14": 0,
            "TestUser15": 0,
        }

        user_classes_count = {
            "TestUser01": 3,
            "TestUser02": 4,
            "TestUser03": 7,
            "TestUser05": 7,
            "TestUser06": 3,
            "TestUser07": 6,
            "TestUser08": 6,
            "TestUser09": 1,
            "TestUser10": 0,
            "TestUser11": 5,
            "TestUser12": 7,
            "TestUser14": 4,
            "TestUser15": 8,
        }

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes, user_classes_count=user_classes_count, spawn_rate=8.556688078766006
        )

        dispatched_users = list(users_dispatcher)

        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users[-1]), user_classes_count)

    def test_dispatch_from_0_to_25000_users_across_5_user_classes_to_250_workers_and_spawn_rate_of_100(self):
        """25000 users at 100 spawn rate to 250 ready clients, 5 user classes (weights: 23, 23, 46, 4. 4)"""
        worker_nodes = [
            WorkerNode("00{}".format(i) if i < 10 else "0{}".format(i) if i < 100 else str(i)) for i in range(1, 251)
        ]

        user_classes_count = {
            "TestUser1": 5750,
            "TestUser2": 5750,
            "TestUser3": 11500,
            "TestUser4": 1000,
            "TestUser5": 1000,
        }

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes, user_classes_count=user_classes_count, spawn_rate=100
        )

        all_dispatched_users = []
        delta = []
        try:
            t0_rel = time.perf_counter()
            for dispatched_users in users_dispatcher:
                all_dispatched_users.append(dispatched_users)
                delta.append(time.perf_counter() - t0_rel)
                t0_rel = time.perf_counter()

            self.assertDictEqual(_aggregate_dispatched_users(all_dispatched_users[-1]), user_classes_count)
        finally:
            # from locust.dispatch import profile; profile.print_stats()
            with open("solution1.json", "wt") as file:
                file.write(json.dumps(all_dispatched_users, indent="  "))
            print(json.dumps(delta, indent="  "))

    def test_dispatch_large_scale(self):
        number_of_dispatch_workers = 40
        number_of_workers = 4000
        spawn_rate = 1000

        worker_nodes = [
            WorkerNode(
                "000{}".format(i)
                if i < 10
                else "00{}".format(i)
                if i < 100
                else "0{}".format(i)
                if i < 1000
                else str(i)
            )
            for i in range(1, (number_of_workers + 1) // number_of_dispatch_workers)
        ]

        # 1 321 740 total users
        user_classes_count = {
            "TestUser01": 4792,
            "TestUser02": 4792,
            "TestUser03": 9584,
            "TestUser04": 834,
            "TestUser05": 833,
            "TestUser06": 833,
            "TestUser07": 833,
            "TestUser08": 833,
            "TestUser09": 833,
            "TestUser10": 833,
            "TestUser11": 833,
            "TestUser12": 833,
            "TestUser13": 833,
            "TestUser14": 833,
            "TestUser15": 833,
            "TestUser16": 833,
            "TestUser17": 833,
            "TestUser18": 833,
            "TestUser19": 833,
            "TestUser20": 833,
            "TestUser21": 15000,
            "TestUser22": 15000,
            "TestUser23": 15000,
            "TestUser24": 15000,
            "TestUser25": 15000,
            "TestUser26": 35000,
            "TestUser27": 35000,
            "TestUser28": 35000,
            "TestUser29": 35000,
            "TestUser30": 35000,
            "TestUser31": 35000,
            "TestUser32": 35000,
            "TestUser33": 35000,
            "TestUser34": 47500,
            "TestUser35": 47500,
            "TestUser36": 47500,
            "TestUser37": 47500,
            "TestUser38": 47500,
            "TestUser39": 47500,
            "TestUser40": 47500,
            "TestUser41": 47500,
            "TestUser42": 47500,
            "TestUser43": 47500,
            "TestUser44": 47500,
            "TestUser45": 47500,
            "TestUser46": 47500,
            "TestUser47": 47500,
            "TestUser48": 89470,
            "TestUser49": 89470,
            "TestUser50": 89470,
        }
        user_classes_count = {k: v // number_of_dispatch_workers for k, v in user_classes_count.items()}

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes,
            user_classes_count=user_classes_count,
            spawn_rate=spawn_rate / number_of_dispatch_workers,
        )

        all_dispatched_users = []
        delta = []
        try:
            t0_rel = time.perf_counter()
            for dispatched_users in users_dispatcher:
                all_dispatched_users.append(
                    {
                        "user_count": sum(map(sum, map(dict.values, dispatched_users.values()))),
                        "dispatched_users": dispatched_users,
                    }
                )
                delta.append(time.perf_counter() - t0_rel)
                t0_rel = time.perf_counter()

            self.assertDictEqual(_aggregate_dispatched_users(all_dispatched_users[-1]), user_classes_count)
        finally:
            from locust.dispatch import profile

            profile.print_stats()
            with open("solution2.json", "wt") as file:
                file.write(json.dumps(all_dispatched_users, indent="  "))
            print(json.dumps(delta, indent="  "))

    def test_crash_dump(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {"User3": 1}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 4}

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.7,
        )

        crash_dump_content, crash_dump_filepath = users_dispatcher._crash_dump()

        self.assertIsInstance(crash_dump_content, str)
        self.assertIsInstance(crash_dump_filepath, str)

        crash_dumps = [json.loads(crash_dump_content)]

        with open(crash_dump_filepath, "rt") as f:
            crash_dumps.append(json.load(f))

        for crash_dump in crash_dumps:
            self.assertEqual(len(crash_dump), 7)
            self.assertEqual(crash_dump["spawn_rate"], 0.7)
            self.assertDictEqual(
                crash_dump["initial_dispatched_users"],
                {
                    "1": {"User1": 0, "User2": 0, "User3": 1},
                    "2": {"User1": 0, "User2": 0, "User3": 0},
                    "3": {"User1": 0, "User2": 4, "User3": 0},
                },
            )
            self.assertDictEqual(
                crash_dump["desired_users_assigned_to_workers"],
                {
                    "1": {"User1": 1, "User2": 1, "User3": 1},
                    "2": {"User1": 1, "User2": 1, "User3": 1},
                    "3": {"User1": 1, "User2": 1, "User3": 1},
                },
            )
            self.assertDictEqual(crash_dump["user_classes_count"], {"User1": 3, "User2": 3, "User3": 3})
            self.assertEqual(crash_dump["initial_user_count"], 5)
            self.assertEqual(crash_dump["desired_user_count"], 9)
            self.assertEqual(crash_dump["number_of_workers"], 3)


def _aggregate_dispatched_users(d: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    user_classes = list(next(iter(d.values())).keys())
    return {u: sum(d[u] for d in d.values()) for u in user_classes}


def _user_count(d: Dict[str, Dict[str, int]]) -> int:
    return sum(map(sum, map(dict.values, d.values())))
