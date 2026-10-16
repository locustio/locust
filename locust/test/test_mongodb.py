import unittest

import pytest

pytest.importorskip("pymongo")

from locust.contrib import mongodb

from pymongo.database import Database

# nothing listens on port 1, so every operation fails fast without needing a MongoDB server
UNREACHABLE_SERVER = "mongodb://127.0.0.1:1/?serverSelectionTimeoutMS=100"


class TestMongoDBClient(unittest.TestCase):
    def setUp(self):
        self.client = mongodb.MongoDBClient(UNREACHABLE_SERVER, "my_db")
        self.addCleanup(self.client.close)

    def test_db_is_the_named_database(self):
        self.assertIsInstance(self.client.db, Database)
        self.assertEqual("my_db", self.client.db.name)

    def test_execute_query_reports_failed_request(self):
        requests = []

        def on_request(**kwargs):
            requests.append(kwargs)

        mongodb.events.request.add_listener(on_request)
        self.addCleanup(mongodb.events.request.remove_listener, on_request)

        self.client.execute_query("my_collection", {"field": "value"})

        self.assertEqual(1, len(requests))
        self.assertEqual("MONGODB", requests[0]["request_type"])
        self.assertIsInstance(requests[0]["exception"], mongodb.PyMongoError)
