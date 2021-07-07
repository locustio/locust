import itertools
import json
import time
import unittest
from typing import Dict

from locust.dispatch import UsersDispatcher
from locust.runners import WorkerNode
from locust.test.util import clear_all_functools_lru_cache

_TOLERANCE = 0.025


class TestAssignUsersToWorkers(unittest.TestCase):
    def test_assign_users_to_1_worker(self):
        worker_node1 = WorkerNode("1")

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1], user_classes_count={"User1": 3, "User2": 3, "User3": 3}, spawn_rate=1
        )
        self.assertDictEqual(
            users_dispatcher._desired_users_assigned_to_workers, {"1": {"User1": 3, "User2": 3, "User3": 3}}
        )

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1], user_classes_count={"User1": 5, "User2": 4, "User3": 2}, spawn_rate=1
        )
        self.assertDictEqual(
            users_dispatcher._desired_users_assigned_to_workers, {"1": {"User1": 5, "User2": 4, "User3": 2}}
        )

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1], user_classes_count={"User1": 1, "User2": 1, "User3": 1}, spawn_rate=1
        )
        self.assertDictEqual(
            users_dispatcher._desired_users_assigned_to_workers, {"1": {"User1": 1, "User2": 1, "User3": 1}}
        )

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1], user_classes_count={"User1": 1, "User2": 1, "User3": 0}, spawn_rate=1
        )
        self.assertDictEqual(
            users_dispatcher._desired_users_assigned_to_workers, {"1": {"User1": 1, "User2": 1, "User3": 0}}
        )

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1], user_classes_count={"User1": 0, "User2": 0, "User3": 0}, spawn_rate=1
        )
        self.assertDictEqual(
            users_dispatcher._desired_users_assigned_to_workers, {"1": {"User1": 0, "User2": 0, "User3": 0}}
        )

    def test_assign_users_to_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 5, "User2": 4, "User3": 2},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 1, "User3": 1},
            "2": {"User1": 2, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 2, "User3": 0},
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 1, "User2": 1, "User3": 1},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 1, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 1},
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 1, "User2": 1, "User3": 0},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 1, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 0, "User2": 0, "User3": 0},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "1": {"User1": 0, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

    def test_assign_5_users_to_10_workers(self):
        # Prepend "0" to worker name under 10, because workers are sorted in alphabetical orders.
        # It's simply makes the test easier to read, but in reality, the worker "10" would come
        # before worker "1".
        worker_nodes = [WorkerNode("0{}".format(i) if i < 10 else str(i)) for i in range(1, 11)]

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 10, "User2": 5, "User3": 5, "User4": 5, "User5": 5},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "01": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "02": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "03": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "04": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "05": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "06": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "07": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "08": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "09": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 5, "User3": 5, "User4": 5, "User5": 5},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "01": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "02": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "03": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "04": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "05": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "06": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "07": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "08": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "09": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 5, "User3": 5, "User4": 5, "User5": 6},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "01": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "02": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "03": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "04": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "05": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "06": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "07": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "08": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "09": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 5, "User3": 5, "User4": 6, "User5": 6},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "01": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "02": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "03": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "04": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "05": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "06": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "07": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "08": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "09": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 5, "User3": 6, "User4": 6, "User5": 6},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "01": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "02": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "03": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "04": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "05": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "06": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "07": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "08": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "09": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 6, "User3": 6, "User4": 6, "User5": 6},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "01": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "02": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "03": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "04": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "05": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "06": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "07": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "08": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "09": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 6, "User3": 6, "User4": 6, "User5": 7},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "01": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "02": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "03": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "04": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "05": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "06": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "07": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "08": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "09": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)

        users_dispatcher = UsersDispatcher(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 6, "User3": 6, "User4": 6, "User5": 11},
            spawn_rate=1,
        )
        expected_balanced_users = {
            "01": {"User1": 2, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 4 users
            "02": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "03": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "04": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "05": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "06": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "07": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 2},  # 4 users
            "08": {"User1": 1, "User2": 0, "User3": 0, "User4": 0, "User5": 3},  # 4 users
            "09": {"User1": 1, "User2": 0, "User3": 0, "User4": 0, "User5": 3},  # 4 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 0, "User5": 3},  # 4 users
        }
        self.assertDictEqual(users_dispatcher._desired_users_assigned_to_workers, expected_balanced_users)


class TestDispatchUsersWithWorkersWithoutPriorUsers(unittest.TestCase):
    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

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
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
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
                "3": {"User1": 0, "User2": 0, "User3": 1},
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
                "3": {"User1": 1, "User2": 0, "User3": 1},
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
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

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
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        ts = time.perf_counter()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
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
                "3": {"User1": 0, "User2": 0, "User3": 1},
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
                "3": {"User1": 1, "User2": 0, "User3": 1},
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
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

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
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
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
                "3": {"User1": 0, "User2": 0, "User3": 1},
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
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

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
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
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
                "3": {"User1": 0, "User2": 0, "User3": 1},
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
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

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
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
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
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

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
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 1},
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

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

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


class TestDispatchUsersToWorkersHavingTheSameUsersAsTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {"User1": 1, "User2": 1, "User3": 1}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1, "User2": 1, "User3": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User1": 1, "User2": 1, "User3": 1}

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


class TestDistributionIsKeptDuringDispatch(unittest.TestCase):
    def test_dispatch_75_users_to_4_workers_with_spawn_rate_of_5(self):
        """
        Test case covering reported issue in https://github.com/locustio/locust/pull/1621#issuecomment-853624275.

        The case is to ramp-up from 0 to 75 users with two user classes. `User1` has a weight of 1 and `User2`
        has a weight of 2. The original issue was with 500 users, but to keep the test shorter, we use 75 users.
        """
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")
        worker_node4 = WorkerNode("4")

        users_dispatcher = UsersDispatcher(
            worker_nodes=[worker_node1, worker_node2, worker_node3, worker_node4],
            user_classes_count={"User1": 25, "User2": 50},
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
                "2": {"User1": 0, "User2": 1},
                "3": {"User1": 0, "User2": 1},
                "4": {"User1": 1, "User2": 0},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(0 <= delta <= _TOLERANCE, delta)

        # total user count = 10
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 4, "User2": 6})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 1, "User2": 2},
                "2": {"User1": 1, "User2": 2},
                "3": {"User1": 1, "User2": 1},
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
                "1": {"User1": 2, "User2": 2},
                "2": {"User1": 1, "User2": 3},
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
                "2": {"User1": 1, "User2": 4},
                "3": {"User1": 2, "User2": 3},
                "4": {"User1": 2, "User2": 3},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 25
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 9, "User2": 16})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 3, "User2": 4},
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
                "2": {"User1": 2, "User2": 6},
                "3": {"User1": 2, "User2": 5},
                "4": {"User1": 3, "User2": 4},
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
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 14, "User2": 26})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 4, "User2": 6},
                "2": {"User1": 3, "User2": 7},
                "3": {"User1": 3, "User2": 7},
                "4": {"User1": 4, "User2": 6},
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
                "2": {"User1": 3, "User2": 8},
                "3": {"User1": 4, "User2": 7},
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
                "1": {"User1": 5, "User2": 8},
                "2": {"User1": 4, "User2": 9},
                "3": {"User1": 4, "User2": 8},
                "4": {"User1": 4, "User2": 8},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 55
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 19, "User2": 36})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 5, "User2": 9},
                "2": {"User1": 4, "User2": 10},
                "3": {"User1": 5, "User2": 9},
                "4": {"User1": 5, "User2": 8},
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
                "2": {"User1": 5, "User2": 11},
                "3": {"User1": 5, "User2": 11},
                "4": {"User1": 6, "User2": 10},
            },
        )
        delta = time.perf_counter() - ts
        self.assertTrue(sleep_time - _TOLERANCE <= delta <= sleep_time + _TOLERANCE, delta)

        # total user count = 70
        ts = time.perf_counter()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(_aggregate_dispatched_users(dispatched_users), {"User1": 24, "User2": 46})
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 6, "User2": 12},
                "2": {"User1": 6, "User2": 12},
                "3": {"User1": 6, "User2": 11},
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
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 6, "User2": 13},
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
