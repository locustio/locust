from locust import TaskSet, between, task
from locust.contrib.postgres import PostgresUser

import os
import random


class UserTasks(TaskSet):
    @task
    def run_select_query(self):
        self.client.execute_query(
            self.user.conn_string,
            "SELECT * FROM loadtesting.invoice WHERE amount > 500",
        )

    @task(3)
    def run_update_query(self):
        random_amount = random.randint(1, 12)
        self.client.execute_query(
            self.user.conn_string,
            f"UPDATE loadtesting.invoice SET amount={random_amount} WHERE amount < 10",
        )


class PostgresLocust(PostgresUser):
    tasks = [UserTasks]
    min_wait = 0
    max_wait = 3
    wait_time = between(min_wait, max_wait)

    # Use environment variables or default values
    PGHOST = os.getenv("PGHOST", "localhost")
    PGPORT = os.getenv("PGPORT", "5432")
    PGDATABASE = os.getenv("PGDATABASE", "loadtesting_db")
    PGUSER = os.getenv("PGUSER", "postgres")
    PGPASSWORD = os.getenv("PGPASSWORD", "postgres")

    conn_string = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
