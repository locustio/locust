from locust import HttpLocust, Locust, TaskSet

class MyTaskSet(TaskSet):
    pass
        
class LocustfileHttpLocust(HttpLocust):
    task_set = MyTaskSet
        
class LocustfileLocust(Locust):
    task_set = MyTaskSet