from locust.core import HttpLocust, Locust, TaskSet
from locust import main

from .testcases import LocustTestCase


class TestTaskSet(LocustTestCase):
    def test_is_locust(self):
        class MyTaskSet(TaskSet):
            pass
        
        class MyHttpLocust(HttpLocust):
            task_set = MyTaskSet
        
        class MyLocust(Locust):
            task_set = MyTaskSet

        self.assertFalse(main.is_locust(("Locust", Locust)))
        self.assertFalse(main.is_locust(("HttpLocust", HttpLocust)))
        self.assertFalse(main.is_locust(("random_dict", {})))
        self.assertFalse(main.is_locust(("random_list", [])))
        
        self.assertTrue(main.is_locust(("MyHttpLocust", MyHttpLocust)))
        self.assertTrue(main.is_locust(("MyLocust", MyLocust)))
        
        class ThriftLocust(Locust):
            pass
        
        self.assertFalse(main.is_locust(("ThriftLocust", ThriftLocust)))

    def test_run_programmatically(self):
        class MyTaskSet(TaskSet):
            pass
        
        class MyHttpLocust(HttpLocust):
            task_set = MyTaskSet
        
        class MyLocust(Locust):
            task_set = MyTaskSet

        default_options = main.create_options(list_commands=True, locustfile="locust/test/locustfile_test.py")
        # Test that it runs with locustfile
        self.assertEqual(set(main.run_locust(default_options)), set(["LocustfileHttpLocust","LocustfileLocust"]))

        # Test locustfile conflicts with locust_classes
        class LocustfileLocust(Locust):
            task_set = MyTaskSet
        conflict_options = default_options
        conflict_options.locust_classes=[LocustfileLocust]
        self.assertRaises(ValueError,lambda: main.run_locust(conflict_options))

        # Test that it runs with locustfile and locust options
        locustfile_and_classes = default_options
        locustfile_and_classes.locust_classes=[MyLocust, MyHttpLocust]

        self.assertEqual(
                set(main.run_locust(locustfile_and_classes)), 
                set(["LocustfileHttpLocust", "LocustfileLocust", "MyLocust", "MyHttpLocust"]))

        # Test that it runs without locustfile
        no_locustfile = locustfile_and_classes
        no_locustfile.locustfile=None
        main.run_locust(no_locustfile)
        self.assertEqual(set(main.run_locust(no_locustfile)), set(["MyLocust", "MyHttpLocust"]))

        # Test that arguments and locust_classes work correctly
        self.assertEqual(set(main.run_locust(no_locustfile, arguments=["MyLocust"])),set(["MyLocust", "MyHttpLocust"]))



