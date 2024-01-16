from locust import debug, task
from locust.test.testcases import LocustTestCase
from locust.user.task import LOCUST_STATE_STOPPING
from locust.user.users import HttpUser

import os
from threading import Timer
from unittest import mock


class DebugTestCase(LocustTestCase):
    def setUp(self):
        super().setUp()
        debug._env = None


class TestDebugging(DebugTestCase):
    @mock.patch.dict(os.environ, {"LOCUST_HOST": "http://localhost"})
    def test_run_single_user_pass_host_to_user_classes(self):
        """
        HttpUser should receive host from environment variable
        """

        class MyUser1(HttpUser):
            @task
            def my_task(self):
                pass

        def _stop_user():
            user = getattr(debug._env, "single_user_instance", None)
            if user:
                user._state = LOCUST_STATE_STOPPING

        t = Timer(1, _stop_user)
        t.start()

        debug.run_single_user(
            MyUser1,
            loglevel=None,  # another log setup might mess with other tests...
        )
