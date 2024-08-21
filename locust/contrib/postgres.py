from locust import TaskSet, User, events

import time

import psycopg


def create_conn(conn_string):
    return psycopg.connect(conn_string)


class PostgresClient:
    def __init__(self, conn_string):
        self.conn_string = conn_string
        self.connection = create_conn(conn_string)

    def execute_query(self, query):
        start_time = time.time()
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            response_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="postgres_success",
                name="execute_query",
                response_time=response_time,
                response_length=0,
            )
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="postgres_failure",
                name="execute_query",
                response_time=response_time,
                response_length=0,
                exception=e,
            )
            print(f"error: {e}")

    def close(self):
        self.connection.close()


class PostgresUser(User):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = PostgresClient(conn_string=self.conn_string)

    def on_stop(self):
        self.client.close()
