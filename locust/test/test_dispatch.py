import itertools
import time
import unittest
from typing import Dict

from locust.dispatch import (
    balance_users_among_workers,
    dispatch_users,
    number_of_users_left_to_dispatch,
)
from locust.runners import WorkerNode


class TestBalanceUsersAmongWorkers(unittest.TestCase):
    def test_balance_users_among_1_worker(self):
        worker_node1 = WorkerNode("1")

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 3, "User2": 3, "User3": 3}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_classes_count={"User1": 5, "User2": 4, "User3": 2},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 5, "User2": 4, "User3": 2}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_classes_count={"User1": 1, "User2": 1, "User3": 1},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 1, "User2": 1, "User3": 1}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_classes_count={"User1": 1, "User2": 1, "User3": 0},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 1, "User2": 1, "User3": 0}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_classes_count={"User1": 0, "User2": 0, "User3": 0},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 0, "User2": 0, "User3": 0}})

    def test_balance_users_among_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 5, "User2": 4, "User3": 2},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 1, "User3": 1},
            "2": {"User1": 2, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 2, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 1, "User2": 1, "User3": 1},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 1, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 1},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 1, "User2": 1, "User3": 0},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 1, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 0, "User2": 0, "User3": 0},
        )
        expected_balanced_users = {
            "1": {"User1": 0, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

    def test_balance_5_users_among_10_workers(self):
        worker_nodes = [WorkerNode(str(i)) for i in range(1, 11)]

        balanced_users = balance_users_among_workers(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 10, "User2": 5, "User3": 5, "User4": 5, "User5": 5},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "2": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "3": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "4": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "5": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "6": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "7": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "8": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "9": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 5, "User3": 5, "User4": 5, "User5": 5},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "2": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "3": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "4": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "5": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "6": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "7": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "8": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "9": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 5, "User3": 5, "User4": 5, "User5": 6},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "2": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "3": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "4": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "5": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "6": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "7": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "8": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "9": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 5, "User3": 5, "User4": 6, "User5": 6},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "2": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "3": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "4": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "5": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "6": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "7": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "8": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "9": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 5, "User3": 6, "User4": 6, "User5": 6},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "2": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "3": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "4": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "5": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "6": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "7": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "8": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "9": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 6, "User3": 6, "User4": 6, "User5": 6},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "2": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "3": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "4": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "5": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "6": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 3 users
            "7": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "8": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "9": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 6, "User3": 6, "User4": 6, "User5": 7},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 1, "User3": 0, "User4": 0, "User5": 1},  # 4 users
            "2": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "3": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "4": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "5": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "6": {"User1": 1, "User2": 1, "User3": 1, "User4": 0, "User5": 1},  # 4 users
            "7": {"User1": 1, "User2": 0, "User3": 1, "User4": 1, "User5": 0},  # 3 users
            "8": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "9": {"User1": 1, "User2": 0, "User3": 0, "User4": 2, "User5": 0},  # 3 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 1},  # 3 users
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 11, "User2": 6, "User3": 6, "User4": 6, "User5": 11},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 1, "User3": 1, "User4": 0, "User5": 0},  # 4 users
            "2": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "3": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "4": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "5": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "6": {"User1": 1, "User2": 1, "User3": 1, "User4": 1, "User5": 0},  # 4 users
            "7": {"User1": 1, "User2": 0, "User3": 0, "User4": 1, "User5": 2},  # 4 users
            "8": {"User1": 1, "User2": 0, "User3": 0, "User4": 0, "User5": 3},  # 4 users
            "9": {"User1": 1, "User2": 0, "User3": 0, "User4": 0, "User5": 3},  # 4 users
            "10": {"User1": 1, "User2": 0, "User3": 0, "User4": 0, "User5": 3},  # 4 users
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)


class TestDispatchUsersWithWorkersWithoutPriorUsers(unittest.TestCase):
    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        sleep_time = 1 / 0.5

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2_4(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2.4,
        )

        sleep_time = 2 / 2.4

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 0},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 0, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 0, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)


class TestDispatchUsersToWorkersHavingLessUsersThanTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        sleep_time = 1 / 0.5

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2.4,
        )

        sleep_time = 2 / 2.4

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 0, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 1, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)


class TestDispatchUsersToWorkersHavingLessAndMoreUsersThanTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        sleep_time = 1 / 0.5

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 0},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        sleep_time = 1

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2.4,
        )

        sleep_time = 2 / 2.4

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 0, "User2": 0, "User3": 1},
                "2": {"User1": 5, "User2": 0, "User3": 1},
                "3": {"User1": 0, "User2": 7, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_classes_count={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.time()
        self.assertDictEqual(
            next(users_dispatcher),
            {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)


class TestDispatchUsersToWorkersHavingMoreUsersThanTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {"User3": 15}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User2": 7}

        for spawn_rate in [0.15, 0.5, 1, 2, 2.4, 3, 4, 9]:
            users_dispatcher = dispatch_users(
                worker_nodes=[worker_node1, worker_node2, worker_node3],
                user_classes_count={"User1": 3, "User2": 3, "User3": 3},
                spawn_rate=spawn_rate,
            )

            ts = time.time()
            self.assertDictEqual(
                next(users_dispatcher),
                {
                    "1": {"User1": 1, "User2": 1, "User3": 1},
                    "2": {"User1": 1, "User2": 1, "User3": 1},
                    "3": {"User1": 1, "User2": 1, "User3": 1},
                },
            )
            delta = time.time() - ts
            self.assertTrue(0 <= delta <= 0.02, delta)

            ts = time.time()
            self.assertRaises(StopIteration, lambda: next(users_dispatcher))
            delta = time.time() - ts
            self.assertTrue(0 <= delta <= 0.02, delta)


class TestDispatchUsersToWorkersHavingTheSameUsersAsTheTarget(unittest.TestCase):
    def test_dispatch_users_to_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_classes_count = {"User1": 1, "User2": 1, "User3": 1}
        worker_node2 = WorkerNode("2")
        worker_node2.user_classes_count = {"User1": 1, "User2": 1, "User3": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_classes_count = {"User1": 1, "User2": 1, "User3": 1}

        for spawn_rate in [0.15, 0.5, 1, 2, 2.4, 3, 4, 9]:
            users_dispatcher = dispatch_users(
                worker_nodes=[worker_node1, worker_node2, worker_node3],
                user_classes_count={"User1": 3, "User2": 3, "User3": 3},
                spawn_rate=spawn_rate,
            )

            ts = time.time()
            self.assertDictEqual(
                next(users_dispatcher),
                {
                    "1": {"User1": 1, "User2": 1, "User3": 1},
                    "2": {"User1": 1, "User2": 1, "User3": 1},
                    "3": {"User1": 1, "User2": 1, "User3": 1},
                },
            )
            delta = time.time() - ts
            self.assertTrue(0 <= delta <= 0.02, delta)

            ts = time.time()
            self.assertRaises(StopIteration, lambda: next(users_dispatcher))
            delta = time.time() - ts
            self.assertTrue(0 <= delta <= 0.02, delta)


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

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3, worker_node4],
            user_classes_count={"User1": 25, "User2": 50},
            spawn_rate=5,
        )

        sleep_time = 1

        # total user count = 5
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 2, "User2": 3},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 2, "User2": 3},
                "2": {"User1": 0, "User2": 0},
                "3": {"User1": 0, "User2": 0},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)

        # total user count = 10
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 4, "User2": 6},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 4, "User2": 6},
                "2": {"User1": 0, "User2": 0},
                "3": {"User1": 0, "User2": 0},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 15
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 5, "User2": 10},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 5, "User2": 10},
                "2": {"User1": 0, "User2": 0},
                "3": {"User1": 0, "User2": 0},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 20
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 7, "User2": 13},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 0, "User2": 1},
                "3": {"User1": 0, "User2": 0},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 25
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 9, "User2": 16},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 2, "User2": 4},
                "3": {"User1": 0, "User2": 0},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 30
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 10, "User2": 20},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 3, "User2": 8},
                "3": {"User1": 0, "User2": 0},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 35
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 12, "User2": 23},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 5, "User2": 11},
                "3": {"User1": 0, "User2": 0},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 40
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 14, "User2": 26},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 6, "User2": 13},
                "3": {"User1": 1, "User2": 1},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 45
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 15, "User2": 30},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 6, "User2": 13},
                "3": {"User1": 2, "User2": 5},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 50
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 17, "User2": 33},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 6, "User2": 13},
                "3": {"User1": 4, "User2": 8},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 55
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 19, "User2": 36},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 6, "User2": 13},
                "3": {"User1": 6, "User2": 11},
                "4": {"User1": 0, "User2": 0},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 60
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 20, "User2": 40},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 6, "User2": 13},
                "3": {"User1": 6, "User2": 13},
                "4": {"User1": 1, "User2": 2},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 65
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 22, "User2": 43},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 6, "User2": 13},
                "3": {"User1": 6, "User2": 13},
                "4": {"User1": 3, "User2": 5},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 70
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 24, "User2": 46},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 6, "User2": 13},
                "3": {"User1": 6, "User2": 13},
                "4": {"User1": 5, "User2": 8},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        # total user count = 75, User1 = 25, User2 = 50
        ts = time.time()
        dispatched_users = next(users_dispatcher)
        self.assertDictEqual(
            _aggregate_dispatched_users(dispatched_users),
            {"User1": 25, "User2": 50},
        )
        self.assertDictEqual(
            dispatched_users,
            {
                "1": {"User1": 7, "User2": 12},
                "2": {"User1": 6, "User2": 13},
                "3": {"User1": 6, "User2": 13},
                "4": {"User1": 6, "User2": 12},
            },
        )
        delta = time.time() - ts
        self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)


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
        worker_nodes = [WorkerNode(str(i)) for i in range(1, 21)]

        for worker_node in worker_nodes:
            worker_node.user_classes_count = {"User1": 0}

        worker_nodes_iterator = itertools.cycle(worker_nodes)
        user_count = 0
        while user_count < 25:
            next(worker_nodes_iterator).user_classes_count["User1"] += 1
            user_count += 1

        users_dispatcher = dispatch_users(
            worker_nodes=worker_nodes,
            user_classes_count={"User1": 50},
            spawn_rate=1,
        )

        sleep_time = 1

        for dispatch_iteration in range(25):
            ts = time.time()
            dispatched_users = next(users_dispatcher)
            self.assertDictEqual(
                _aggregate_dispatched_users(dispatched_users),
                {"User1": 25 + dispatch_iteration + 1},
            )
            delta = time.time() - ts
            if dispatch_iteration == 0:
                self.assertTrue(0 <= delta <= 0.02, delta)
            else:
                self.assertTrue(sleep_time - 0.02 <= delta <= sleep_time + 0.02, delta)

        ts = time.time()
        self.assertRaises(StopIteration, lambda: next(users_dispatcher))
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.02, delta)


class TestNumberOfUsersLeftToDispatch(unittest.TestCase):
    def test_number_of_users_left_to_dispatch(self):
        user_classes_count = {"User1": 6, "User2": 2, "User3": 8}
        balanced_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }

        dispatched_users = {
            "Worker1": {"User1": 5, "User2": 2, "User3": 6},
            "Worker2": {"User1": 5, "User2": 2, "User3": 6},
        }
        result = number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_classes_count)
        self.assertEqual(0, result)

        dispatched_users = {
            "Worker1": {"User1": 2, "User2": 0, "User3": 4},
            "Worker2": {"User1": 2, "User2": 0, "User3": 4},
        }
        result = number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_classes_count)
        self.assertEqual(4, result)

        dispatched_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 0, "User3": 4},
        }
        result = number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_classes_count)
        self.assertEqual(1, result)

        dispatched_users = {
            "Worker1": {"User1": 3, "User2": 1, "User3": 4},
            "Worker2": {"User1": 3, "User2": 1, "User3": 4},
        }
        result = number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_classes_count)
        self.assertEqual(0, result)


def _aggregate_dispatched_users(d: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    user_classes = list(next(iter(d.values())).keys())
    return {u: sum(d[u] for d in d.values()) for u in user_classes}
