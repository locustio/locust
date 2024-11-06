from locust import between, task
from locust.contrib.mongodb import MongoDBUser

import os


class MongoUser(MongoDBUser):
    conn_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/defaultdb")
    db_name = "test"  # change to your db name

    @task
    def db_query(self):
        self.client.execute_query("collection", {"field": "value"})  # update to match your collection, field, and value
