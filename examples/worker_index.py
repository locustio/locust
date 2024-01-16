# How to use worker_index to read from a pre-partitioned CSV file (mythings_0.csv, mythings_1.csv, ...)
# so that each worker uses their own file
from locust import User, events, runners, task

from locust_plugins import csvreader  # install locust-plugins first


class DemoUser(User):
    reader: csvreader.CSVDictReader

    @task
    def t(self):
        thing = next(self.reader)
        print(thing)


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if not isinstance(environment.runner, runners.MasterRunner):
        DemoUser.reader = csvreader.CSVDictReader(f"mythings_{environment.runner.worker_index}.csv")
