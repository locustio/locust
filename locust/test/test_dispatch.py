import time
import unittest

from locust.dispatch import (
    balance_users_among_workers,
    dispatch_users,
)
from locust.runners import WorkerNode


class TestBalanceUsersAmongWorkers(unittest.TestCase):
    maxDiff = None

    def test_balance_users_among_1_worker(self):
        worker_node1 = WorkerNode("1")

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 3, "User2": 3, "User3": 3}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 5, "User2": 4, "User3": 2},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 5, "User2": 4, "User3": 2}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 1, "User2": 1, "User3": 1},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 1, "User2": 1, "User3": 1}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 1, "User2": 1, "User3": 0},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 1, "User2": 1, "User3": 0}})

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1],
            user_class_occurrences={"User1": 0, "User2": 0, "User3": 0},
        )
        self.assertDictEqual(balanced_users, {"1": {"User1": 0, "User2": 0, "User3": 0}})

    def test_balance_users_among_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 5, "User2": 4, "User3": 2},
        )
        expected_balanced_users = {
            "1": {"User1": 2, "User2": 2, "User3": 1},
            "2": {"User1": 2, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 1, "User2": 1, "User3": 1},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 1, "User2": 1, "User3": 0},
        )
        expected_balanced_users = {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)

        balanced_users = balance_users_among_workers(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 0, "User2": 0, "User3": 0},
        )
        expected_balanced_users = {
            "1": {"User1": 0, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            '3': {"User1": 0, "User2": 0, "User3": 0},
        }
        self.assertDictEqual(balanced_users, expected_balanced_users)


class TestDispatchUsersWithWorkersWithoutUsers(unittest.TestCase):
    maxDiff = None

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 0, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 0, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node2 = WorkerNode("2")
        worker_node3 = WorkerNode("3")

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))


class TestDispatchUsersToWorkersHavingLessUsersThanTheTarget(unittest.TestCase):
    maxDiff = None

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 0, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 0, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 0},
            "2": {"User1": 1, "User2": 1, "User3": 0},
            "3": {"User1": 1, "User2": 1, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 1}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))


class TestDispatchUsersToWorkersHavingMoreUsersThanTheTarget(unittest.TestCase):
    maxDiff = None

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_0_5(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=0.5,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 0, "User2": 0, "User3": 1},
            "2": {"User1": 5, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 7, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 0, "User2": 0, "User3": 1},
            "2": {"User1": 5, "User2": 0, "User3": 1},
            "3": {"User1": 0, "User2": 7, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(1.99 <= delta <= 2.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_1(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=1,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 0, "User2": 0, "User3": 1},
            "2": {"User1": 5, "User2": 0, "User3": 0},
            "3": {"User1": 0, "User2": 7, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 0, "User2": 0, "User3": 1},
            "2": {"User1": 5, "User2": 0, "User3": 1},
            "3": {"User1": 0, "User2": 7, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_2(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=2,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 0, "User2": 0, "User3": 1},
            "2": {"User1": 5, "User2": 0, "User3": 1},
            "3": {"User1": 0, "User2": 7, "User3": 0},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0.99 <= delta <= 1.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_3(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=3,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_4(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=4,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))

    def test_dispatch_users_to_3_workers_with_spawn_rate_of_9(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 5}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User2": 7}

        users_dispatcher = dispatch_users(
            worker_nodes=[worker_node1, worker_node2, worker_node3],
            user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
            spawn_rate=9,
        )

        ts = time.time()
        self.assertDictEqual(next(users_dispatcher), {
            "1": {"User1": 1, "User2": 1, "User3": 1},
            "2": {"User1": 1, "User2": 1, "User3": 1},
            "3": {"User1": 1, "User2": 1, "User3": 1},
        })
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 0.01, delta)

        self.assertRaises(StopIteration, lambda: next(users_dispatcher))


class TestDispatchUsersToWorkersHavingTheSameUsersAsTheTarget(unittest.TestCase):
    maxDiff = None

    def test_dispatch_users_to_3_workers(self):
        worker_node1 = WorkerNode("1")
        worker_node1.user_class_occurrences = {"User1": 1, "User2": 1, "User3": 1}
        worker_node2 = WorkerNode("2")
        worker_node2.user_class_occurrences = {"User1": 1, "User2": 1, "User3": 1}
        worker_node3 = WorkerNode("3")
        worker_node3.user_class_occurrences = {"User1": 1, "User2": 1, "User3": 1}

        for spawn_rate in [0.5, 1, 2, 3, 4, 9]:
            users_dispatcher = dispatch_users(
                worker_nodes=[worker_node1, worker_node2, worker_node3],
                user_class_occurrences={"User1": 3, "User2": 3, "User3": 3},
                spawn_rate=spawn_rate,
            )

            ts = time.time()
            self.assertDictEqual(next(users_dispatcher), {
                "1": {"User1": 1, "User2": 1, "User3": 1},
                "2": {"User1": 1, "User2": 1, "User3": 1},
                "3": {"User1": 1, "User2": 1, "User3": 1},
            })
            delta = time.time() - ts
            self.assertTrue(0 <= delta <= 0.01, delta)

            self.assertRaises(StopIteration, lambda: next(users_dispatcher))
