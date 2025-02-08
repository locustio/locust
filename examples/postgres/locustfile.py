from locust import task
from locust.contrib.postgres import PostgresUser

import os
import random


class PostgresLocust(PostgresUser):
    @task
    def run_select_query(self):
        self.client.execute_query(
            "SELECT * FROM loadtesting.invoice WHERE amount > 500",
        )

    @task
    def run_update_query(self):
        random_amount = random.randint(1, 12)
        self.client.execute_query(
            f"UPDATE loadtesting.invoice SET amount={random_amount} WHERE amount < 10",
        )

    # Use environment variables or default values
    PGHOST = os.getenv("PGHOST", "localhost")
    PGPORT = os.getenv("PGPORT", "5432")
    PGDATABASE = os.getenv("PGDATABASE", "test_db")
    PGUSER = os.getenv("PGUSER", "postgres")
    PGPASSWORD = os.getenv("PGPASSWORD", "postgres")

    conn_string = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
