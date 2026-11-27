"""
Change settings of running users without restarting the test.

Each user class below has a DynamicConfig. While the test is running you can edit the values in the
"Dynamic Config" tab of the web UI, or send them to the web server, for example:

    curl -X POST localhost:8089/dynamic-config -H "Content-Type: application/json" \
        -d '{"IndexUser": {"index_enabled": false}, "StatsUser": {"stats_report_flow": 30}}'

Only the settings you send are changed. In a distributed run the new values are also sent to all workers.

    locust -f examples/dynamic_config.py
"""

from locust import DynamicConfig, HttpUser, between, task

import random


class IndexConfig(DynamicConfig):
    # setting name -> default value. Values can be anything that is JSON serializable.
    config_bucket = {"index_enabled": True}


class StatsConfig(DynamicConfig):
    config_bucket = {"stats_report_flow": 30}


class IndexUser(HttpUser):
    """
    User class that does requests to the locust web server running on localhost
    """

    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    dynamic_config = IndexConfig()

    @task
    def index(self):
        if self.index_enabled:
            self.client.get("/")


class StatsUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    dynamic_config = StatsConfig()

    @task
    def stats(self):
        self.client.get("/stats/requests")
        stats_report_probability = random.randint(0, 100)
        if stats_report_probability < self.stats_report_flow:
            self.client.get("/stats/requests/csv")
