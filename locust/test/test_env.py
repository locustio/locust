from locust import (
    constant,
)
from locust.env import Environment
from locust.user import (
    User,
    task,
)
from .testcases import LocustTestCase
from .fake_module1_for_env_test import MyUserWithSameName as MyUserWithSameName1
from .fake_module2_for_env_test import MyUserWithSameName as MyUserWithSameName2


class TestEnvironment(LocustTestCase):
    def test_user_classes_count(self):
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

    def test_user_classes_with_same_name_is_error(self):
        with self.assertRaises(ValueError) as e:
            environment = Environment(user_classes=[MyUserWithSameName1, MyUserWithSameName2])

        self.assertEqual(
            e.exception.args[0],
            "The following user classes have the same class name: locust.test.fake_module1_for_env_test.MyUserWithSameName, locust.test.fake_module2_for_env_test.MyUserWithSameName",
        )
