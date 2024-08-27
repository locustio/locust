from gevent import monkey

_ = monkey.patch_all()

from locust import User, events

import time

from pymongo import MongoClient
from pymongo.errors import PyMongoError


class MongoDBClient:
    def __init__(self, conn_string, db_name):
        self.client = MongoClient(conn_string)
        self.db = self.client[db_name]

    def execute_query(self, collection_name, query):
        start_time = time.time()
        try:
            response_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="mongodb_success", name="execute_query", response_time=response_time, response_length=0
            )
        except PyMongoError as e:
            response_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="mongodb_failure",
                name="execute_query",
                response_time=response_time,
                response_length=0,
                exception=e,
            )

    def close(self):
        self.client.close()


class MongoDBUser(User):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = MongoDBClient(conn_string=self.conn_string, db_name=self.db_name)

    def on_stop(self):
        self.client.close()
