from locust import HttpUser, task, between


class Search(HttpUser):
    wait_time = between(1, 2)

    @task
    def search(self):
        self.client.get("/search/howsearchworks/?fg=1")
