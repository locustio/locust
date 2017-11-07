from locust import main
from locust.core import HttpLocust, Locust, TaskSet

from .testcases import LocustTestCase


class TestTaskSet(LocustTestCase):
    def test_is_locust(self):
        assert not main.is_locust(("Locust", Locust))
        assert not main.is_locust(("HttpLocust", HttpLocust))
        assert not main.is_locust(("random_dict", {}))
        assert not main.is_locust(("random_list", []))
        
        class MyTaskSet(TaskSet):
            pass
        
        class MyHttpLocust(HttpLocust):
            task_set = MyTaskSet
        
        class MyLocust(Locust):
            task_set = MyTaskSet
        
        assert main.is_locust(("MyHttpLocust", MyHttpLocust))
        assert main.is_locust(("MyLocust", MyLocust))
        
        class ThriftLocust(Locust):
            pass
        
        assert not main.is_locust(("ThriftLocust", ThriftLocust))
