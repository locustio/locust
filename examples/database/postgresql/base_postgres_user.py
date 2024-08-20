from locust import TaskSet, User, events

import time

import psycopg


def create_conn(conn_string):
    return psycopg.connect(conn_string)


def execute_query(conn_string, query):
    db_conn = create_conn(conn_string)
    return db_conn.cursor().execute(query)


class PostgresClient:
    def __getattr__(self, name):
        def request_handler(*args, **kwargs):
            start_time = time.time()
            try:
                execute_query(*args, **kwargs)
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
                print(f"error: {e}")

        return request_handler


class PostgresUser(User):
    abstract = True
    client_class = PostgresClient

    def __init__(self, *args, **kwargs):
        self.client = self.client_class()
