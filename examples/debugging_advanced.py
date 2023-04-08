from locust import HttpUser, task, run_single_user
from locust.exception import StopUser


class User1(HttpUser):
    host = "http://localhost"

    @task
    def hello_world(self):
        with self.client.get("/hello1", catch_response=True) as resp:
            pass
        raise StopUser()


class User2(HttpUser):
    host = "http://localhost"

    @task
    def hello_world(self):
        with self.client.get("/hello2", catch_response=True) as resp:
            pass
        raise StopUser()


if __name__ == "__main__":
    print("running User1")
    run_single_user(User1)
    print("running User2")
    run_single_user(User2)
    print("done!")
