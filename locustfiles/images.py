from locust import HttpUser, task, between


class Images(HttpUser):
    wait_time = between(1, 2)

    @task
    def images(self):
        self.client.get("/imghp?hl=en&ogbl")
