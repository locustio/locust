from locust import main
from locust.core import HttpLocust, Locust, TaskSet

from .testcases import LocustTestCase
import os

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


class TestLoadLocustfile(LocustTestCase):
    mock_docstring = 'This is a mock locust file for unit testing.'
    mock_locust_file_content = """\"\"\"{}\"\"\"

from locust import HttpLocust, TaskSet, task


def index(l):
    l.client.get("/")

def stats(l):
    l.client.get("/stats/requests")


class UserTasks(TaskSet):
    # one can specify tasks like this
    tasks = [index, stats]


class LocustSubclass(HttpLocust):
    host = "http://127.0.0.1:8089"
    min_wait = 2000
    max_wait = 5000
    task_set = UserTasks


class NotLocustSubclass():
    host = "http://localhost:8000"

            """.format(mock_docstring)
    directory = os.path.dirname(os.path.abspath(__file__))
    filename = 'mock_locust_file'

    def __create_mock_locust_file(self, filename):
        # Creates a mock locust file for testing
        self.filename = filename
        self.file_path = os.path.join(self.directory, self.filename)
        with open(self.file_path, 'w') as file:
            file.write(self.mock_locust_file_content)

    def setUp(self):
        pass

    def tearDown(self):
        os.remove(self.file_path)

    def test_load_locust_file_from_absolute_path(self):
        self.__create_mock_locust_file('mock_locust_file.py')
        docstring, locusts = main.load_locustfile(self.file_path)

    def test_load_locust_file_from_relative_path(self):
        self.__create_mock_locust_file('mock_locust_file.py')
        docstring, locusts = main.load_locustfile(os.path.join('./locust/test/', self.filename))

    def test_load_locust_file_with_a_dot_in_filename(self):
        self.__create_mock_locust_file('mock_locust_file.py')
        docstring, locusts = main.load_locustfile(self.file_path)
    
    def test_load_locust_file_with_multiple_dots_in_filename(self):
        self.__create_mock_locust_file('mock_locust_file.test.py')
        docstring, locusts = main.load_locustfile(self.file_path)
    
    def test_return_docstring_and_locusts(self):
        self.__create_mock_locust_file('mock_locust_file.py')
        docstring, locusts = main.load_locustfile(self.file_path)
        self.assertEqual(docstring, self.mock_docstring)
        self.assertIn('LocustSubclass', locusts)
        self.assertNotIn('NotLocustSubclass', locusts)
