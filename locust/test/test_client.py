import unittest
from requests.exceptions import RequestException

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
    
    def test_connection_error(self):
        s = HttpSession("http://localhost:1")
        r = s.get("/", timeout=0.1)
        self.assertFalse(r)
        self.assertEqual(None, r.content)
        self.assertRaises(RequestException, r.raise_for_status)
