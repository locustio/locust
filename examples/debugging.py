from locust import HttpUser, task
from locust.debug import run_single_user


class QuickstartUser(HttpUser):
    host = "http://localhost"

    @task
    def hello_world(self):
        with self.client.get("/hello", catch_response=True) as resp:
            pass  # maybe set a breakpoint here to analyze the resp object?


if __name__ == "__main__":
    run_single_user(QuickstartUser)
