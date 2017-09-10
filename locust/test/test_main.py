import shlex

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


    def test_parse_options(self):

        parser, options, args = main.parse_options()
        self.assertEqual('locustfile', options.locustfile)
        self.assertEqual(None, options.host)
        self.assertEqual([], args)

        parser, options, args = main.parse_options(args=shlex.split('--locustfile=test.py -H http://localhost:5000'))
        self.assertEqual('test.py', options.locustfile)
        self.assertEqual('http://localhost:5000', options.host)
        self.assertEqual([], args)
