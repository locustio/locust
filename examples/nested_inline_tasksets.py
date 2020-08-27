from locust import HttpUser, TaskSet, task, between


class WebsiteUser(HttpUser):
    """
    Example of the ability of inline nested TaskSet classes
    """

    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)

    @task
    class TopLevelTaskSet(TaskSet):
        @task
        class IndexTaskSet(TaskSet):
            @task(10)
            def index(self):
                self.client.get("/")

            @task(1)
            def stop(self):
                self.interrupt()

        @task
        def stats(self):
            self.client.get("/stats/requests")
