from locust import constant, task
from locust.contrib.postgres import PostgresUser

import os
from logging import getLogger

logger = getLogger("locust")


class MyUser(PostgresUser):
    wait_time = constant(1)

    @task
    def run_select_query(self):
        # example from https://rnacentral.org/help/public-database
        row = self.client.execute_query("SELECT * FROM rnc_database")
        if row:
            logger.debug(row.fetchall())
        else:
            logger.info("no rows returned")

    # @task
    # def run_update_query(self):
    #     random_amount = random.randint(1, 12)
    #     self.client.execute_query(
    #         f"UPDATE loadtesting.invoice SET amount={random_amount} WHERE amount < 10",
    #     )

    # Use environment variables or default values
    PGHOST = os.getenv("PGHOST", "localhost")
    PGPORT = os.getenv("PGPORT", "5432")
    PGDATABASE = os.getenv("PGDATABASE", "postgres")
    PGUSER = os.getenv("PGUSER", "postgres")
    PGPASSWORD = os.getenv("PGPASSWORD", "")

    conn_string = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
