from requests.exceptions import (InvalidSchema, InvalidURL, MissingSchema,
                                 RequestException)

from locust.clients import HttpSession
from locust.env import Environment
from .testcases import WebserverTestCase


class TestHttpSession(WebserverTestCase):
    def get_client(self, base_url=None):
        if base_url is None:
            base_url = "http://127.0.0.1:%i" % self.port
        return HttpSession(
            base_url=base_url,
            request_success=self.environment.events.request_success,
            request_failure=self.environment.events.request_failure,
        )
    
    def test_get(self):
        s = self.get_client()
        r = s.get("/ultra_fast")
        self.assertEqual(200, r.status_code)
    
    def test_connection_error(self):
        s = self.get_client(base_url="http://localhost:1")
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
            s = self.get_client(base_url=url)
            try:
                self.assertRaises(exception, s.get, "/")
            except KeyError:
                self.fail("Invalid URL %s was not propagated" % url)
    
    def test_streaming_response(self):
        """
        Test a request to an endpoint that returns a streaming response
        """
        s = self.get_client()
        r = s.get("/streaming/30")
        
        # verify that the time reported includes the download time of the whole streamed response
        self.assertGreater(self.runner.stats.get("/streaming/30", method="GET").avg_response_time, 250)
        self.runner.stats.clear_all()
        
        # verify that response time does NOT include whole download time, when using stream=True
        r = s.get("/streaming/30", stream=True)
        self.assertGreater(self.runner.stats.get("/streaming/30", method="GET").avg_response_time, 0)
        self.assertLess(self.runner.stats.get("/streaming/30", method="GET").avg_response_time, 250)
        
        # download the content of the streaming response (so we don't get an ugly exception in the log)
        _ = r.content
    
    def test_slow_redirect(self):
        s = self.get_client()
        url = "/redirect?url=/redirect&delay=0.5"
        r = s.get(url)
        stats = self.runner.stats.get(url, method="GET")
        self.assertEqual(1, stats.num_requests)
        self.assertGreater(stats.avg_response_time, 500)
    
    def test_post_redirect(self):
        s = self.get_client()
        url = "/redirect"
        r = s.post(url)
        self.assertEqual(200, r.status_code)
        post_stats = self.runner.stats.get(url, method="POST")
        get_stats = self.runner.stats.get(url, method="GET")
        self.assertEqual(1, post_stats.num_requests)
        self.assertEqual(0, get_stats.num_requests)
    
    def test_cookie(self):
        s = self.get_client()
        r = s.post("/set_cookie?name=testcookie&value=1337")
        self.assertEqual(200, r.status_code)
        r = s.get("/get_cookie?name=testcookie")
        self.assertEqual('1337', r.content.decode())
    
    def test_head(self):
        s = self.get_client()
        r = s.head("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("", r.content.decode())
    
    def test_delete(self):
        s = self.get_client()
        r = s.delete("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("DELETE", r.content.decode())
    
    def test_options(self):
        s = self.get_client()
        r = s.options("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("", r.content.decode())
        self.assertEqual(
            set(["OPTIONS", "DELETE", "PUT", "GET", "POST", "HEAD", "PATCH"]),
            set(r.headers["allow"].split(", ")),
        )

    def test_error_message_with_name_replacment(self):
        s = self.get_client()
        kwargs = {}
        def on_error(**kw):
            kwargs.update(kw)

        self.environment.events.request_failure.add_listener(on_error)
        s.request('get', '/wrong_url/01', name='replaced_url_name')
        self.assertIn('for url: replaced_url_name', str(kwargs['exception']))
