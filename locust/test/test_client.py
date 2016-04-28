from requests.exceptions import (RequestException, MissingSchema,
        InvalidSchema, InvalidURL)

import gevent
from locust.clients import HttpSession
from locust.stats import global_stats
from .testcases import WebserverTestCase

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
    
    def test_streaming_response(self):
        """
        Test a request to an endpoint that returns a streaming response
        """
        s = HttpSession("http://127.0.0.1:%i" % self.port)
        r = s.get("/streaming/30")
        
        # verify that the time reported includes the download time of the whole streamed response
        self.assertGreater(global_stats.get("/streaming/30", method="GET").avg_response_time, 250)
        global_stats.clear_all()
        
        # verify that response time does NOT include whole download time, when using stream=True
        r = s.get("/streaming/30", stream=True)
        self.assertGreater(global_stats.get("/streaming/30", method="GET").avg_response_time, 0)
        self.assertLess(global_stats.get("/streaming/30", method="GET").avg_response_time, 250)
        
        # download the content of the streaming response (so we don't get an ugly exception in the log)
        _ = r.content
    
    def test_slow_redirect(self):
        s = HttpSession("http://127.0.0.1:%i" % self.port)
        url = "/redirect?url=/redirect?delay=0.5"
        r = s.get(url)
        stats = global_stats.get(url, method="GET")
        self.assertEqual(1, stats.num_requests)
        self.assertGreater(stats.avg_response_time, 500)
    
    def test_post_redirect(self):
        s = HttpSession("http://127.0.0.1:%i" % self.port)
        url = "/redirect"
        r = s.post(url)
        self.assertEqual(200, r.status_code)
        post_stats = global_stats.get(url, method="POST")
        get_stats = global_stats.get(url, method="GET")
        self.assertEqual(1, post_stats.num_requests)
        self.assertEqual(0, get_stats.num_requests)
    
