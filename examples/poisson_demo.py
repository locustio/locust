from locust import HttpUser, poisson, task


class PoissonDemoUser(HttpUser):
    """On average 5 tasks per second, but with randomly distributed (Poisson) intervals.

    Run this next to a user with ``wait_time = constant_throughput(5)`` to see the
    difference between randomly distributed arrivals and a fixed pace.
    """

    wait_time = poisson(5)

    @task
    def demo_task(self):
        self.client.get("/")
