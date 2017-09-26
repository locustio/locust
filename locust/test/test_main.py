from locust import main
from locust import config
from locust.core import WebLocust, Locust, TaskSet

from .testcases import LocustTestCase


class TestTaskSet(LocustTestCase):
    def test_is_locust(self):
        self.assertFalse(config.is_locust(("Locust", Locust)))
        self.assertFalse(config.is_locust(("WebLocust", WebLocust)))
        self.assertFalse(config.is_locust(("random_dict", {})))
        self.assertFalse(config.is_locust(("random_list", [])))

        class MyTaskSet(TaskSet):
            pass

        class MyHttpLocust(WebLocust):
            task_set = MyTaskSet

        class MyLocust(Locust):
            task_set = MyTaskSet

        self.assertTrue(config.is_locust(("MyHttpLocust", MyHttpLocust)))
        self.assertTrue(config.is_locust(("MyLocust", MyLocust)))

        class ThriftLocust(Locust):
            pass

        self.assertFalse(config.is_locust(("ThriftLocust", ThriftLocust)))
