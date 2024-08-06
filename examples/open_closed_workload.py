from locust import HttpUser, constant, constant_pacing, task


class ClosedWorkload(HttpUser):
    wait_time = constant(10)  # sleep 10s after each task, regardless of execution time

    @task
    def t(self):
        pass


class OpenWorkload(HttpUser):
    wait_time = constant_pacing(10)  # sleep just enough so that we run one task iteration every 10s

    @task
    def t(self):
        pass


# Note: A test using constant_pacing is still limited by the number of Users you spawn,
# so if response times increase to the point where one task execution takes more than 10s,
# you still wont reach your target throughput.
