from locust import main
from locust.core import HttpLocust, Locust, TaskSet

from .testcases import LocustTestCase


class TestTaskSet(LocustTestCase):
    def test_is_locust(self):
        self.assertFalse(main.is_locust(("Locust", Locust)))
        self.assertFalse(main.is_locust(("HttpLocust", HttpLocust)))
        self.assertFalse(main.is_locust(("random_dict", {})))
        self.assertFalse(main.is_locust(("random_list", [])))
        
        class MyTaskSet(TaskSet):
            pass
        
        class MyHttpLocust(HttpLocust):
            task_set = MyTaskSet
        
        class MyLocust(Locust):
            task_set = MyTaskSet
        
        self.assertTrue(main.is_locust(("MyHttpLocust", MyHttpLocust)))
        self.assertTrue(main.is_locust(("MyLocust", MyLocust)))
        
        class ThriftLocust(Locust):
            pass
        
        self.assertFalse(main.is_locust(("ThriftLocust", ThriftLocust)))

    def test_is_taskset(self):
        class MyTaskSet(TaskSet):
            pass
        self.assertFalse(main.is_taskset(("TaskSet", TaskSet)))
        self.assertFalse(main.is_taskset(("random_dict", {})))
        self.assertFalse(main.is_taskset(("random_list", [])))
        self.assertTrue(main.is_taskset(("MyTaskset",MyTaskSet)))
