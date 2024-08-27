from locust import between, task
from locust.contrib.mongo import MongoDBUser

import os


class MongoDBUser(MongoDBUser):
    conn_string = os.getenv("MONGODB_URI")
    db_name = "test"

    @task
    def db_query(self):
        self.client.execute_query("collection", {"field": "value"})
