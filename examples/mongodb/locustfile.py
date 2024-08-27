from locust import between, task
from locust.contrib.mongo import MongoDBUser


class MongoDBUser(MongoDBUser):
    conn_string = "mongodb://mongoadmin:secret@localhost:27017"
    db_name = "test"
    wait_time = between(1, 5)

    @task
    def db_query(self):
        self.client.execute_query("collection", {"field": "value"})
