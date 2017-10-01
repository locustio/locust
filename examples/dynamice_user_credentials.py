# locustfile.py

from locust import HttpLocust, TaskSet, task

USER_CREDENTIALS = [
    ("user1", "password"),
    ("user2", "password"),
    ("user3", "password"),
]

class UserBehaviour(TaskSet):
    def on_start(self):
        if len(USER_CREDENTIALS) > 0:
            user, passw = USER_CREDENTIALS.pop()
            self.client.post("/login", {"username":user, "password":passw})
    
    @task
    def some_task(self):
        # user should be logged in here (unless the USER_CREDENTIALS ran out)
        self.client.get("/protected/resource")

class User(HttpLocust):
    task_set = UserBehaviour
    min_wait = 5000
    max_wait = 60000
