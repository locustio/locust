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
    
    def test_task_ratio_command_with_locust_weight(self):
        class Tasks(TaskSet):
            @task(1)
            def task1(self):
                pass

            @task(3)
            def task3(self):
                pass

        class UnlikelyLocust(Locust):
            weight = 1
            task_set = Tasks

        class MoreLikelyLocust(Locust):
            weight = 3
            task_set = Tasks

        ratio_dict = get_task_ratio_dict([UnlikelyLocust, MoreLikelyLocust], total=True)

        self.assertEquals({
               'UnlikelyLocust':   {'tasks': {'task1': {'ratio': 0.25*0.25}, 'task3': {'ratio': 0.25*0.75}}, 'ratio': 0.25},
               'MoreLikelyLocust': {'tasks': {'task1': {'ratio': 0.75*0.25}, 'task3': {'ratio': 0.75*0.75}}, 'ratio': 0.75}
               }, ratio_dict)
        unlikely = ratio_dict['UnlikelyLocust']['tasks']
        likely = ratio_dict['MoreLikelyLocust']['tasks']
        assert unlikely['task1']['ratio'] + unlikely['task3']['ratio'] + likely['task1']['ratio'] + likely['task3']['ratio'] == 1
