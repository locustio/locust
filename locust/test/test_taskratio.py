from locust.dispatch import UsersDispatcher
from locust.runners import WorkerNode
from locust.user import TaskSet, User, task
from locust.user.inspectuser import _calc_distribution, _get_task_ratio, get_ratio

import unittest


class TestTaskRatio(unittest.TestCase):
    def test_task_ratio_command(self):
        class Tasks(TaskSet):
            @task
            def root_task1(self):
                pass

            @task
            class SubTasks(TaskSet):
                @task
                def task1(self):
                    pass

                @task
                def task2(self):
                    pass

        class MyUser(User):
            tasks = [Tasks]

        ratio_dict = _get_task_ratio(Tasks.tasks, True, 1.0)

        self.assertEqual(
            {
                "SubTasks": {"tasks": {"task1": {"ratio": 0.25}, "task2": {"ratio": 0.25}}, "ratio": 0.5},
                "root_task1": {"ratio": 0.5},
            },
            ratio_dict,
        )

    def test_task_ratio_command_with_locust_weight(self):
        class Tasks(TaskSet):
            @task(1)
            def task1(self):
                pass

            @task(3)
            def task3(self):
                pass

        class UnlikelyUser(User):
            weight = 1
            tasks = [Tasks]

        class MoreLikelyUser(User):
            weight = 3
            tasks = [Tasks]

        ratio_dict = get_ratio([UnlikelyUser, MoreLikelyUser], {"UnlikelyUser": 1, "MoreLikelyUser": 3}, True)

        self.assertDictEqual(
            {
                "UnlikelyUser": {
                    "ratio": 0.25,
                    "tasks": {
                        "Tasks": {
                            "tasks": {
                                "task1": {"ratio": 0.25 * 0.25},
                                "task3": {"ratio": 0.25 * 0.75},
                            },
                            "ratio": 0.25,
                        }
                    },
                },
                "MoreLikelyUser": {
                    "ratio": 0.75,
                    "tasks": {
                        "Tasks": {
                            "tasks": {
                                "task1": {"ratio": 0.75 * 0.25},
                                "task3": {"ratio": 0.75 * 0.75},
                            },
                            "ratio": 0.75,
                        },
                    },
                },
            },
            ratio_dict,
        )
        unlikely = ratio_dict["UnlikelyUser"]["tasks"]["Tasks"]["tasks"]
        likely = ratio_dict["MoreLikelyUser"]["tasks"]["Tasks"]["tasks"]
        assert (
            unlikely["task1"]["ratio"]
            + unlikely["task3"]["ratio"]
            + likely["task1"]["ratio"]
            + likely["task3"]["ratio"]
            == 1
        )

    def test_user_distribution_matches_dispatcher(self):
        class A(User):
            pass

        class B(User):
            pass

        class C(User):
            weight = 2

        class D(User):
            fixed_count = 1

        for user_classes in ([A, B], [A, B, C], [A, B, C, D]):
            for num_users in (1, 2, 3, 5, 7, 10):
                dispatcher = UsersDispatcher(worker_nodes=[WorkerNode("w")], user_classes=user_classes)
                dispatcher.new_dispatch(target_user_count=num_users, spawn_rate=num_users)
                spawned = list(dispatcher)[-1]["w"]
                with self.subTest(user_classes=[u.__name__ for u in user_classes], num_users=num_users):
                    self.assertEqual(spawned, _calc_distribution(user_classes, num_users))
