from locust import main, tests_loader
from locust.core import HttpLocust, Locust, TaskSet

from .testcases import LocustTestCase


class TestTaskSet(LocustTestCase):
    def test_is_locust(self):
        self.assertFalse(tests_loader.is_locust(("Locust", Locust)))
        self.assertFalse(tests_loader.is_locust(("HttpLocust", HttpLocust)))
        self.assertFalse(tests_loader.is_locust(("random_dict", {})))
        self.assertFalse(tests_loader.is_locust(("random_list", [])))
        
        class MyTaskSet(TaskSet):
            pass
        
        class MyHttpLocust(HttpLocust):
            task_set = MyTaskSet
        
        class MyLocust(Locust):
            task_set = MyTaskSet
        
        self.assertTrue(tests_loader.is_locust(("MyHttpLocust", MyHttpLocust)))
        self.assertTrue(tests_loader.is_locust(("MyLocust", MyLocust)))
        
        class ThriftLocust(Locust):
            pass
        
        self.assertFalse(tests_loader.is_locust(("ThriftLocust", ThriftLocust)))
