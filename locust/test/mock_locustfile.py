import os
import random
import time

from contextlib import contextmanager


MOCK_LOUCSTFILE_CONTENT = '''
"""This is a mock locust file for unit testing"""

from locust import HttpLocust, TaskSet, task, between


def index(l):
    l.client.get("/")

def stats(l):
    l.client.get("/stats/requests")


class UserTasks(TaskSet):
    # one can specify tasks like this
    tasks = [index, stats]


class LocustSubclass(HttpLocust):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    task_set = UserTasks


class NotLocustSubclass():
    host = "http://localhost:8000"

'''

class MockedLocustfile:
    __slots__ = ["filename", "directory", "file_path"]


@contextmanager
def mock_locustfile(filename_prefix="mock_locustfile", content=MOCK_LOUCSTFILE_CONTENT):
    mocked = MockedLocustfile()
    mocked.directory = os.path.dirname(os.path.abspath(__file__))
    mocked.filename = "%s_%s_%i.py" % (
        filename_prefix, 
        str(time.time()).replace(".", "_"), 
        random.randint(0,100000),
    )
    mocked.file_path = os.path.join(mocked.directory, mocked.filename)
    with open(mocked.file_path, 'w') as file:
        file.write(content)
    
    yield mocked
    os.remove(mocked.file_path)
