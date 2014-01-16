import unittest

from locust.core import HttpLocust, Locust
from locust import main
from .testcases import LocustTestCase, WebserverTestCase

class TestTaskSet(LocustTestCase):
    def test_is_locust(self):
        self.assertFalse(main.is_locust(("Locust", Locust)))
        self.assertFalse(main.is_locust(("HttpLocust", HttpLocust)))
        self.assertFalse(main.is_locust(("random_dict", {})))
        self.assertFalse(main.is_locust(("random_list", [])))
        
        class MyHttpLocust(HttpLocust):
            pass
        
        class MyLocust(Locust):
            pass
        
        self.assertTrue(main.is_locust(("MyHttpLocust", MyHttpLocust)))
        self.assertTrue(main.is_locust(("MyLocust", MyLocust)))
        
        class ThriftLocust(Locust):
            abstract = True
        
        self.assertFalse(main.is_locust(("ThriftLocust", ThriftLocust)))
