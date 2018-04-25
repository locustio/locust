from locust import Locust, TaskSet, task

class DummyTaskSet(TaskSet):
    @task()
    def dummy_pass(self):
        pass

class Dummy(Locust):
    task_set = DummyTaskSet
