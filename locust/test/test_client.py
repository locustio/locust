import unittest

from locust.clients import HttpSession
from testcases import WebserverTestCase

class TestHttpSession(WebserverTestCase):
    def test_get(self):
        s = HttpSession("http://127.0.0.1:%i" % self.port)
        r = s.get("/ultra_fast")
        self.assertEqual(200, r.status_code)
    
    def test_session_config(self):
        s = HttpSession("http://127.0.0.1:%i" % self.port)
        self.assertFalse(s.config.get("keep_alive"))
        self.assertEqual(0, s.config.get("max_retries"))
        