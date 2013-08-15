from requests.exceptions import (RequestException, MissingSchema,
        InvalidSchema, InvalidURL)

from locust.clients import HttpSession
from testcases import WebserverTestCase

class TestHttpSession(WebserverTestCase):
    def test_get(self):
        s = HttpSession("http://127.0.0.1:%i" % self.port)
        r = s.get("/ultra_fast")
        self.assertEqual(200, r.status_code)
    
    def test_connection_error(self):
        s = HttpSession("http://localhost:1")
        r = s.get("/", timeout=0.1)
        self.assertEqual(r.status_code, 0)
        self.assertEqual(None, r.content)
        self.assertRaises(RequestException, r.raise_for_status)

    def test_wrong_url(self):
        for url, exception in (
                (u"http://\x94", InvalidURL),
                ("telnet://127.0.0.1", InvalidSchema),
                ("127.0.0.1", MissingSchema), 
            ):
            s = HttpSession(url)
            try:
                self.assertRaises(exception, s.get, "/")
            except KeyError:
                self.fail("Invalid URL %s was not propagated" % url)
