import unittest

from locust.user import User, TaskSet, task
from locust.user.inspectuser import get_task_ratio_dict


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

        ratio_dict = get_task_ratio_dict(Tasks.tasks, total=True)

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

        ratio_dict = get_task_ratio_dict([UnlikelyUser, MoreLikelyUser], total=True)

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
