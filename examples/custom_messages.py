from locust import HttpUser, task, events, between
from locust.runners import MasterRunner, WorkerRunner

usernames = []


def setup_test_users(environment, msg, **kwargs):
    # Fired when the worker recieves a message of type 'test_users'
    usernames.extend(map(lambda u: u["name"], msg.data))
    environment.runner.send_message("acknowledge_users", f"Thanks for the {len(msg.data)} users!")


def on_acknowledge(msg, **kwargs):
    # Fired when the master recieves a message of type 'acknowledge_users'
    print(msg.data)


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if not isinstance(environment.runner, MasterRunner):
        environment.runner.register_message("test_users", setup_test_users)
    if not isinstance(environment.runner, WorkerRunner):
        environment.runner.register_message("acknowledge_users", on_acknowledge)


@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    # When the test is started, evenly divides list between
    # worker nodes to ensure unique data across threads
    if not isinstance(environment.runner, WorkerRunner):
        users = []
        for i in range(environment.runner.target_user_count):
            users.append({"name": f"User{i}"})

        worker_count = environment.runner.worker_count
        chunk_size = int(len(users) / worker_count)

        for i, worker in enumerate(environment.runner.clients):
            start_index = i * chunk_size

            if i + 1 < worker_count:
                end_index = start_index + chunk_size
            else:
                end_index = len(users)

            data = users[start_index:end_index]
            environment.runner.send_message("test_users", data, worker)


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)

    def __init__(self, parent):
        self.username = usernames.pop()
        super(WebsiteUser, self).__init__(parent)

    @task
    def task(self):
        print(self.username)
