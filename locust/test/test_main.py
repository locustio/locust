import os

from locust import main
from locust.argument_parser import parse_options
from locust.main import create_environment
from locust.core import HttpLocust, Locust, TaskSet
from .testcases import LocustTestCase
from .mock_locustfile import mock_locustfile


class TestLoadLocustfile(LocustTestCase):
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
    
    def test_load_locust_file_from_absolute_path(self):
        with mock_locustfile() as mocked:
            docstring, locusts = main.load_locustfile(mocked.file_path)
            self.assertIn('LocustSubclass', locusts)
            self.assertNotIn('NotLocustSubclass', locusts)

    def test_load_locust_file_from_relative_path(self):
        with mock_locustfile() as mocked:
            docstring, locusts = main.load_locustfile(os.path.join('./locust/test/', mocked.filename))

    def test_load_locust_file_with_a_dot_in_filename(self):
        with mock_locustfile(filename_prefix="mocked.locust.file") as mocked:
            docstring, locusts = main.load_locustfile(mocked.file_path)
    
    def test_return_docstring_and_locusts(self):
        with mock_locustfile() as mocked:
            docstring, locusts = main.load_locustfile(mocked.file_path)
            self.assertEqual("This is a mock locust file for unit testing", docstring)
            self.assertIn('LocustSubclass', locusts)
            self.assertNotIn('NotLocustSubclass', locusts)
    
    def test_create_environment(self):
        options = parse_options(args=[
            "--host", "https://custom-host",
            "--reset-stats",
        ])
        env = create_environment(options)
        self.assertEqual("https://custom-host", env.host)
        self.assertTrue(env.reset_stats)
        
        options = parse_options(args=[])
        env = create_environment(options)
        self.assertEqual(None, env.host)
        self.assertFalse(env.reset_stats)

