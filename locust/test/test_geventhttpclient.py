import six

from locust.contrib.geventhttpclient import GeventHttpSession, GeventHttpLocust
from locust.stats import global_stats

from .testcases import WebserverTestCase


class TestGeventHttpSession(WebserverTestCase):
    def test_get(self):
        s = GeventHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.get("/ultra_fast")
        self.assertEqual(200, r.status_code)
    
    def test_connection_error(self):
        global_stats.clear_all()
        s = GeventHttpSession("http://localhost:1")
        r = s.get("/", timeout=0.1)
        self.assertEqual(r.status_code, 0)
        self.assertEqual(None, r.content)
        self.assertTrue(isinstance(r.error, ConnectionRefusedError))
        self.assertEqual(1, len(global_stats.errors))
        self.assertTrue(isinstance(six.next(six.itervalues(global_stats.errors)).error, ConnectionRefusedError))
    
    def test_404(self):
        global_stats.clear_all()
        s = GeventHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.get("/does_not_exist")
        self.assertEqual(404, r.status_code)
        self.assertEqual(1, global_stats.get("/does_not_exist", "GET").num_failures)
    
    def test_streaming_response(self):
        """
        Test a request to an endpoint that returns a streaming response
        """
        s = GeventHttpSession("http://127.0.0.1:%i" % self.port)
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
        s = GeventHttpSession("http://127.0.0.1:%i" % self.port)
        url = "/redirect?url=/redirect?delay=0.5"
        r = s.get(url)
        stats = global_stats.get(url, method="GET")
        self.assertEqual(1, stats.num_requests)
        self.assertGreater(stats.avg_response_time, 500)
    
    def test_post_redirect(self):
        s = GeventHttpSession("http://127.0.0.1:%i" % self.port)
        url = "/redirect"
        r = s.post(url)
        self.assertEqual(200, r.status_code)
        post_stats = global_stats.get(url, method="POST")
        get_stats = global_stats.get(url, method="GET")
        self.assertEqual(1, post_stats.num_requests)
        self.assertEqual(0, get_stats.num_requests)
    
    def test_cookie(self):
        s = GeventHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.post("/set_cookie?name=testcookie&value=1337")
        self.assertEqual(200, r.status_code)
        r = s.get("/get_cookie?name=testcookie")
        self.assertEqual('1337', r.content.decode())
    
    def test_head(self):
        s = GeventHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.head("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("", r.content.decode())
    
    def test_delete(self):
        s = GeventHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.delete("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("DELETE", r.content.decode())
    
    def test_options(self):
        s = GeventHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.options("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("", r.content.decode())
        self.assertEqual(
            set(["OPTIONS", "DELETE", "PUT", "GET", "POST", "HEAD"]),
            set(r.headers["allow"].split(", ")),
        )


class TestRequestStatsWithWebserver(WebserverTestCase):
    def test_request_stats_content_length(self):
        class MyLocust(GeventHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast")
        self.assertEqual(global_stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response"))
        locust.client.get("/ultra_fast")
        self.assertEqual(global_stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response"))
    
    def test_request_stats_no_content_length(self):
        class MyLocust(GeventHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
        l = MyLocust()
        path = "/no_content_length"
        r = l.client.get(path)
        self.assertEqual(global_stats.get(path, "GET").avg_content_length, len("This response does not have content-length in the header"))
    
    def test_request_stats_no_content_length_streaming(self):
        class MyLocust(GeventHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
        l = MyLocust()
        path = "/no_content_length"
        r = l.client.get(path, stream=True)
        self.assertEqual(0, global_stats.get(path, "GET").avg_content_length)
    
    def test_request_stats_named_endpoint(self):
        class MyLocust(GeventHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast", name="my_custom_name")
        self.assertEqual(1, global_stats.get("my_custom_name", "GET").num_requests)
    
    def test_request_stats_query_variables(self):
        class MyLocust(GeventHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast?query=1")
        self.assertEqual(1, global_stats.get("/ultra_fast?query=1", "GET").num_requests)
    
    def test_request_stats_put(self):
        class MyLocust(GeventHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.put("/put")
        self.assertEqual(1, global_stats.get("/put", "PUT").num_requests)
    
    def test_request_connection_error(self):
        class MyLocust(GeventHttpLocust):
            host = "http://localhost:1"
        
        locust = MyLocust()
        response = locust.client.get("/", timeout=0.1)
        self.assertEqual(response.status_code, 0)
        self.assertEqual(1, global_stats.get("/", "GET").num_failures)
        self.assertEqual(0, global_stats.get("/", "GET").num_requests)
