from locust.contrib.socketio import SocketIOUser

import time
from unittest.mock import patch

import socketio

from .testcases import LocustTestCase


class TestSocketIOUser(LocustTestCase):
    def test_everything(self):
        def connect(self, *args, **kwargs): ...
        def emit(self, *args, **kwargs): ...
        def call(self, event, data, *args, **kwargs):
            if event == "error":
                raise Exception("Simulated error")
            time.sleep(0.001)
            return {"mock": "response"}

        with patch.multiple(socketio.Client, connect=connect, emit=emit, call=call) as _mocks:
            user = SocketIOUser(self.environment)
            user.connect("http://fake-url.com")
            user.emit("test_event", {"data": "test_data"})
            resp = user.call("test_2", {"data": "test_data"})
            user.call("error", {})
            self.assertEqual(1, self.environment.stats.entries[("connect", "WS")].num_requests)
            self.assertEqual(1, self.environment.stats.entries[("test_event", "WSE")].num_requests)
            self.assertEqual(1, self.environment.stats.entries[("test_2", "WSC")].num_requests)
            assert isinstance(resp, dict)
            self.assertDictEqual({"mock": "response"}, resp)
            self.assertLess(0.001, self.environment.stats.entries[("test_2", "WSC")].avg_response_time)
            self.assertEqual(1, self.environment.stats.entries[("error", "WSC")].num_requests)
            self.assertEqual(1, len(self.environment.stats.errors))
