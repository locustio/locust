from locust import between, task
from locust.contrib.mongo import MongoDBUser

import os


class MongoDBUser(MongoDBUser):
    conn_string = os.getenv("MONGODB_URI")
    db_name = "test"  # change to your db name

    @task
    def db_query(self):
        # chanf
        self.client.execute_query("collection", {"field": "value"})  # update to match your collection, field, and value
