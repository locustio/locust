from locust import (
    constant,
)
from locust.env import Environment, LoadTestShape
from locust.user import (
    User,
    task,
)
from locust.user.task import TaskSet
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

    def test_assign_equal_weights(self):
        def verify_tasks(u, target_tasks):
            self.assertEqual(len(u.tasks), len(target_tasks))
            tasks = [t.__name__ for t in u.tasks]
            self.assertEqual(len(tasks), len(set(tasks)))
            self.assertEqual(set(tasks), set(target_tasks))

        # Base case
        class MyUser1(User):
            wait_time = constant(0)

            @task(4)
            def my_task(self):
                pass

            @task(1)
            def my_task_2(self):
                pass

        environment = Environment(user_classes=[MyUser1])
        environment.assign_equal_weights()
        u = environment.user_classes[0]
        verify_tasks(u, ["my_task", "my_task_2"])

        # Testing nested task sets
        class MyUser2(User):
            @task
            class TopLevelTaskSet(TaskSet):
                @task
                class IndexTaskSet(TaskSet):
                    @task(10)
                    def index(self):
                        self.client.get("/")

                    @task
                    def stop(self):
                        self.client.get("/hi")

                @task(2)
                def stats(self):
                    self.client.get("/stats/requests")

        environment = Environment(user_classes=[MyUser2])
        environment.assign_equal_weights()
        u = environment.user_classes[0]
        verify_tasks(u, ["index", "stop", "stats"])

        # Testing task assignment via instance variable
        def outside_task():
            pass

        def outside_task_2():
            pass

        class SingleTaskSet(TaskSet):
            tasks = [outside_task, outside_task, outside_task_2]

        class MyUser3(User):
            tasks = [SingleTaskSet, outside_task]

        environment = Environment(user_classes=[MyUser3])
        environment.assign_equal_weights()
        u = environment.user_classes[0]
        verify_tasks(u, ["outside_task", "outside_task_2"])

        # Testing task assignment via dict
        class DictTaskSet(TaskSet):
            def dict_task_1():
                pass

            def dict_task_2():
                pass

            def dict_task_3():
                pass

            tasks = {
                dict_task_1: 5,
                dict_task_2: 3,
                dict_task_3: 1,
            }

        class MyUser4(User):
            tasks = [DictTaskSet, SingleTaskSet, SingleTaskSet]

        # Assign user tasks in dict
        environment = Environment(user_classes=[MyUser4])
        environment.assign_equal_weights()
        u = environment.user_classes[0]
        verify_tasks(u, ["outside_task", "outside_task_2", "dict_task_1", "dict_task_2", "dict_task_3"])

        class MyUser5(User):
            tasks = {
                DictTaskSet: 5,
                SingleTaskSet: 3,
                outside_task: 6,
            }

        environment = Environment(user_classes=[MyUser5])
        environment.assign_equal_weights()
        u = environment.user_classes[0]
        verify_tasks(u, ["outside_task", "outside_task_2", "dict_task_1", "dict_task_2", "dict_task_3"])

    def test_user_classes_with_zero_weight_are_removed(self):
        class MyUser1(User):
            wait_time = constant(0)
            weight = 0

            @task
            def my_task(self):
                pass

        class MyUser2(User):
            wait_time = constant(0)
            weight = 1

            @task
            def my_task(self):
                pass

        environment = Environment(user_classes=[MyUser1, MyUser2])

        self.assertEqual(len(environment.user_classes), 1)
        self.assertIs(environment.user_classes[0], MyUser2)

    def test_all_user_classes_with_zero_weight_raises_exception(self):
        class MyUser1(User):
            wait_time = constant(0)
            weight = 0

            @task
            def my_task(self):
                pass

        class MyUser2(User):
            wait_time = constant(0)
            weight = 0

            @task
            def my_task(self):
                pass

        with self.assertRaises(ValueError) as e:
            environment = Environment(user_classes=[MyUser1, MyUser2])

        self.assertEqual(
            e.exception.args[0],
            "There are no users with weight > 0.",
        )

    def test_shape_class_attribute(self):
        class SubLoadTestShape(LoadTestShape):
            """Inherited from locust.env.LoadTestShape"""

        with self.assertRaisesRegex(
            ValueError, r"instance of LoadTestShape or subclass LoadTestShape", msg="exception message is mismatching"
        ):
            Environment(user_classes=[MyUserWithSameName1], shape_class=SubLoadTestShape)
