from locust import (
    constant,
)
from locust.env import Environment
from locust.user import (
    User,
    task,
)
from .testcases import LocustTestCase


class TestEnvironment(LocustTestCase):
    def test_user_class_occurrences(self):
        class MyUser1(User):
            wait_time = constant(0)

            @task
            def my_task(self):
                pass

        class MyUser2(User):
            wait_time = constant(0)

            @task
            def my_task(self):
                pass

        environment = Environment(user_classes=[MyUser1, MyUser2])

        self.assertDictEqual({"MyUser1": MyUser1, "MyUser2": MyUser2}, environment.user_classes_by_name)
