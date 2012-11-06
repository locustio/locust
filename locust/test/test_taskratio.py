import unittest

from locust.core import Locust, TaskSet, task
from locust.inspectlocust import get_task_ratio_dict

class TestTaskRatio(unittest.TestCase):
    def test_task_ratio_command(self):
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
        
        ratio_dict = get_task_ratio_dict(User.task_set.tasks, total=True)
        
        self.assertEqual({
            'SubTasks': {
                'tasks': {
                    'task1': {'ratio': 0.25},
                    'task2': {'ratio': 0.25}
                },
                'ratio': 0.5
            }, 
            'root_task1': {'ratio': 0.5}
        }, ratio_dict)
    
