import random
import time

import psycopg

from locust import TaskSet, User, between, events, task


def create_conn(conn_string):
    print("Connect and Query PostgreSQL")
    conn = psycopg2.connect(conn_string)
    return conn


def execute_query(conn_string, query):
    db_conn = create_conn(conn_string)
    db_query = db_conn.cursor().execute(query)
    return db_query


class PostgresClient:
    def __getattr__(self, name):
        def request_handler(*args, **kwargs):
            start_time = time.time()
            try:
                _ = execute_query(*args, **kwargs)
                response_time = int((time.time() - start_time) * 1000)
                events.request.fire(
                    request_type="postgres_success",
                    name=name,
                    response_time=response_time,
                    response_length=0,
                )
            except Exception as e:
                response_time = int((time.time() - start_time) * 1000)
                events.request.fire(
                    request_type="postgres_failure",
                    name=name,
                    response_time=response_time,
                    response_length=0,
                    exception=e,
                )

                print("error {}".format(e))

        return request_handler


class UserTasks(TaskSet):
    conn_string = "postgresql://postgres:postgres@localhost:5432/loadtesting_db"

    @task 
    def run_select_query(self):
        self.client.execute_query(
            self.conn_string,
            f"SELECT * FROM loadtesting.invoice WHERE amount > 500",
        )

    @task(3)
    def run_update_query(self):
        random_amount = random.randint(1, 12)
        self.client.execute_query(
            self.conn_string,
            f"UPDATE loadtesting.invoice SET amount={random_amount} WHERE amount < 10",
        )



class PostgresLocust(User):
    tasks = [UserTasks]
    min_wait = 0
    max_wait = 3
    wait_time = between(min_wait, max_wait)

    def __init__(self, *args):
        self.client = PostgresClient()
