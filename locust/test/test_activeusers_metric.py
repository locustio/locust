from unittest.mock import patch
from locust import HttpUser, LoadTestShape, between, task
from .testcases import LocustTestCase


class SimpleUser(HttpUser):
    wait_time = between(0.1, 0.3)

    @task
    def index(self):
        self.client.get("/")


class RampUserTest(LoadTestShape):
    """
    Shape used by the test to ramp active users up and back down.

    The stages are chosen so the OTel ``locust.users.count`` gauge can be
    observed increasing, decreasing, and finally reaching zero.
    """
    stages = [
        {"duration": 6, "users": 6, "spawn_rate": 6},
        {"duration": 12, "users": 3, "spawn_rate": 6},
        {"duration": 18, "users": 0, "spawn_rate": 6},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None


class UserCount(LocustTestCase):
    def test_user_count_ramps_through_expected_stages(self):
        shape = RampUserTest()

        with patch.object(RampUserTest, "get_run_time", return_value=0):
            self.assertEqual((6, 6), shape.tick())

        with patch.object(RampUserTest, "get_run_time", return_value=6):
            self.assertEqual((3, 6), shape.tick())

        with patch.object(RampUserTest, "get_run_time", return_value=12):
            self.assertEqual((0, 6), shape.tick())

        with patch.object(RampUserTest, "get_run_time", return_value=18):
            self.assertIsNone(shape.tick())