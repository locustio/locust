from locust import core

from locust import config
import random

with config.configure() as config:
    config.host = 'google.com'

class UserWorkflow(core.TaskSet):

    def on_start(self):
        self.context['persistent_var'] = 'version 1'

    def on_task_start(self):
        self.context['persistent_var'] = 'version 2'
        pass

    def on_task_end(self):
        pass

    @core.task(1)
    def task(self):
        self.client.http.get("/")
        self.client.http.post("/")
        self.client.http.get("/")
        import time; time.sleep(1)

    @core.task(1)
    @core.mod_context('persistent_var', 'version 3')
    def task_2(self):
        if random.random() > 0.5:
            self.client.http.get("/")
        else:
            self.client.http.post("/")
        import time; time.sleep(1)

    @core.task(1)
    def task_1(self):
        if random.random() > 0.5:
            self.client.http.get("/")
        else:
            self.client.http.post("/")
        import time; time.sleep(1)

class TestLocust(core.WebLocust):
    task_set = UserWorkflow
