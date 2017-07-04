import unittest

from locust.core import Locust, TaskSet, task
from locust.inspectlocust import (
    get_task_dict_with_order, get_task_execution_order
)

class TestTaskOrder(unittest.TestCase):

    def test_task_order_command_without_locust_order(self):
        class Tasks(TaskSet):
            @task
            def root_task1(self):
                pass

            @task
            class SubTasks(TaskSet):
                @task
                def task1(self):
                    pass

                @task
                def task2(self):
                    pass

        class User(Locust):
            task_set = Tasks

        order_dict = get_task_dict_with_order(User.task_set.tasks)

        self.assertEqual({
            'SubTasks': {
                'tasks': {
                    'task1': {'order': None},
                    'task2': {'order': None}
                },
                'order': None
            },
            'root_task1': {'order': None}
        }, order_dict)

    def test_task_order_command_with_locust_order(self):
        class Tasks(TaskSet):
            @task(order=2)
            def task1(self):
                pass

            @task(order=1)
            def task2(self):
                pass

        class OrderedLocust(Locust):
            task_set = Tasks

        order_dict = get_task_dict_with_order([OrderedLocust])

        self.assertEquals({
            'OrderedLocust': {
                'tasks': {
                    'task1': {
                        'order': 2
                    },
                    'task2': {
                        'order': 1
                    }
                },
                'order': None
            },
        }, order_dict)

    def test_task_order_command_with_multiple_locust(self):
        class Tasks1(TaskSet):
            @task(order=2)
            def task1(self):
                pass

            @task(order=1)
            def task2(self):
                pass
        
        class Tasks2(TaskSet):
            @task(order=1)
            def task1(self):
                pass

            @task(order=2)
            def task2(self):
                pass

        class OrderedLocust1(Locust):
            order = 2
            task_set = Tasks1

        class OrderedLocust2(Locust):
            order = 1
            task_set = Tasks2

        order_dict = get_task_dict_with_order([OrderedLocust1, OrderedLocust2])

        self.assertEquals({
            'OrderedLocust1': {
                'tasks': {
                    'task1': {
                        'order': 2
                    },
                    'task2': {
                        'order': 1
                    }
                },
                'order': 2
            },
            'OrderedLocust2': {
                'tasks': {
                    'task1': {
                        'order': 1
                    },
                    'task2': {
                        'order': 2
                    }
                },
                'order': 1
            },
        }, order_dict)

    def test_task_order_results(self):
        class Tasks(TaskSet):
            @task(order=2)
            def task1(self):
                pass

            @task(order=3)
            def task2(self):
                pass
                
            @task(order=1)
            def task3(self):
                pass

        class OrderedLocust(Locust):
            task_set = Tasks

        task_list = get_task_execution_order(OrderedLocust)

        self.assertEquals([
            'task3', 'task1', 'task2'
        ], task_list)
