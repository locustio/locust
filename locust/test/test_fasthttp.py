import socket

from locust import TaskSet, task, events
from locust.core import LocustError
from locust.contrib.fasthttp import FastHttpSession, FastHttpLocust
from locust.exception import CatchResponseError, InterruptTaskSet, ResponseError
from locust.stats import global_stats

from .testcases import WebserverTestCase


class TestFastHttpSession(WebserverTestCase):
    def test_get(self):
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.get("/ultra_fast")
        self.assertEqual(200, r.status_code)
    
    def test_connection_error(self):
        global_stats.clear_all()
        s = FastHttpSession("http://localhost:1")
        r = s.get("/", timeout=0.1)
        self.assertEqual(r.status_code, 0)
        self.assertEqual(None, r.content)
        self.assertEqual(1, len(global_stats.errors))
        self.assertTrue(isinstance(r.error, ConnectionRefusedError))
        self.assertTrue(isinstance(next(iter(global_stats.errors.values())).error, ConnectionRefusedError))
    
    def test_404(self):
        global_stats.clear_all()
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.get("/does_not_exist")
        self.assertEqual(404, r.status_code)
        self.assertEqual(1, global_stats.get("/does_not_exist", "GET").num_failures)
    
    def test_204(self):
        global_stats.clear_all()
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.get("/status/204")
        self.assertEqual(204, r.status_code)
        self.assertEqual(1, global_stats.get("/status/204", "GET").num_requests)
        self.assertEqual(0, global_stats.get("/status/204", "GET").num_failures)
    
    def test_streaming_response(self):
        """
        Test a request to an endpoint that returns a streaming response
        """
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.get("/streaming/30")
        
        # verify that the time reported includes the download time of the whole streamed response
        self.assertGreater(global_stats.get("/streaming/30", method="GET").avg_response_time, 250)
        global_stats.clear_all()
        
        # verify that response time does NOT include whole download time, when using stream=True
        r = s.get("/streaming/30", stream=True)
        self.assertGreaterEqual(global_stats.get("/streaming/30", method="GET").avg_response_time, 0)
        self.assertLess(global_stats.get("/streaming/30", method="GET").avg_response_time, 250)
        
        # download the content of the streaming response (so we don't get an ugly exception in the log)
        _ = r.content
    
    def test_slow_redirect(self):
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        url = "/redirect?url=/redirect?delay=0.5"
        r = s.get(url)
        stats = global_stats.get(url, method="GET")
        self.assertEqual(1, stats.num_requests)
        self.assertGreater(stats.avg_response_time, 500)
    
    def test_post_redirect(self):
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        url = "/redirect"
        r = s.post(url)
        self.assertEqual(200, r.status_code)
        post_stats = global_stats.get(url, method="POST")
        get_stats = global_stats.get(url, method="GET")
        self.assertEqual(1, post_stats.num_requests)
        self.assertEqual(0, get_stats.num_requests)
    
    def test_cookie(self):
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.post("/set_cookie?name=testcookie&value=1337")
        self.assertEqual(200, r.status_code)
        r = s.get("/get_cookie?name=testcookie")
        self.assertEqual('1337', r.content.decode())
    
    def test_head(self):
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.head("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("", r.content.decode())
    
    def test_delete(self):
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.delete("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("DELETE", r.content.decode())
    
    def test_patch(self):
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.patch("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("PATCH", r.content.decode())
    
    def test_options(self):
        s = FastHttpSession("http://127.0.0.1:%i" % self.port)
        r = s.options("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("", r.content.decode())
        self.assertEqual(
            set(["OPTIONS", "DELETE", "PUT", "GET", "POST", "HEAD", "PATCH"]),
            set(r.headers["allow"].split(", ")),
        )


class TestRequestStatsWithWebserver(WebserverTestCase):
    def test_request_stats_content_length(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast")
        self.assertEqual(global_stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response"))
        locust.client.get("/ultra_fast")
        self.assertEqual(global_stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response"))
    
    def test_request_stats_no_content_length(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
        l = MyLocust()
        path = "/no_content_length"
        r = l.client.get(path)
        self.assertEqual(global_stats.get(path, "GET").avg_content_length, len("This response does not have content-length in the header"))
    
    def test_request_stats_no_content_length_streaming(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
        l = MyLocust()
        path = "/no_content_length"
        r = l.client.get(path, stream=True)
        self.assertEqual(0, global_stats.get(path, "GET").avg_content_length)
    
    def test_request_stats_named_endpoint(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast", name="my_custom_name")
        self.assertEqual(1, global_stats.get("my_custom_name", "GET").num_requests)
    
    def test_request_stats_query_variables(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast?query=1")
        self.assertEqual(1, global_stats.get("/ultra_fast?query=1", "GET").num_requests)
    
    def test_request_stats_put(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.put("/put")
        self.assertEqual(1, global_stats.get("/put", "PUT").num_requests)
    
    def test_request_connection_error(self):
        class MyLocust(FastHttpLocust):
            host = "http://localhost:1"
        
        locust = MyLocust()
        response = locust.client.get("/", timeout=0.1)
        self.assertEqual(response.status_code, 0)
        self.assertEqual(1, global_stats.get("/", "GET").num_failures)
        self.assertEqual(1, global_stats.get("/", "GET").num_requests)


class TestFastHttpLocustClass(WebserverTestCase):
    def test_get_request(self):
        self.response = ""
        def t1(l):
            self.response = l.client.get("/ultra_fast")
        class MyLocust(FastHttpLocust):
            tasks = [t1]
            host = "http://127.0.0.1:%i" % self.port

        my_locust = MyLocust()
        t1(my_locust)
        self.assertEqual(self.response.text, "This is an ultra fast response")

    def test_client_request_headers(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("hello", locust.client.get("/request_header_test", headers={"X-Header-Test":"hello"}).text)

    def test_client_get(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("GET", locust.client.get("/request_method").text)
    
    def test_client_get_absolute_url(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("GET", locust.client.get("http://127.0.0.1:%i/request_method" % self.port).text)

    def test_client_post(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("POST", locust.client.post("/request_method", {"arg":"hello world"}).text)
        self.assertEqual("hello world", locust.client.post("/post", {"arg":"hello world"}).text)

    def test_client_put(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("PUT", locust.client.put("/request_method", {"arg":"hello world"}).text)
        self.assertEqual("hello world", locust.client.put("/put", {"arg":"hello world"}).text)

    def test_client_delete(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("DELETE", locust.client.delete("/request_method").text)
        self.assertEqual(200, locust.client.delete("/request_method").status_code)

    def test_client_head(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual(200, locust.client.head("/request_method").status_code)
    
    def test_log_request_name_argument(self):
        from locust.stats import global_stats
        self.response = ""
        
        class MyLocust(FastHttpLocust):
            tasks = []
            host = "http://127.0.0.1:%i" % self.port
            
            @task()
            def t1(l):
                self.response = l.client.get("/ultra_fast", name="new name!")

        my_locust = MyLocust()
        my_locust.t1()
        
        self.assertEqual(1, global_stats.get("new name!", "GET").num_requests)
        self.assertEqual(0, global_stats.get("/ultra_fast", "GET").num_requests)
    
    def test_redirect_url_original_path_as_name(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        l = MyLocust()
        l.client.get("/redirect")
        
        from locust.stats import global_stats
        self.assertEqual(1, len(global_stats.entries))
        self.assertEqual(1, global_stats.get("/redirect", "GET").num_requests)
        self.assertEqual(0, global_stats.get("/ultra_fast", "GET").num_requests)
    
    def test_client_basic_auth(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        class MyAuthorizedLocust(FastHttpLocust):
            host = "http://locust:menace@127.0.0.1:%i" % self.port

        class MyUnauthorizedLocust(FastHttpLocust):
            host = "http://locust:wrong@127.0.0.1:%i" % self.port

        locust = MyLocust()
        unauthorized = MyUnauthorizedLocust()
        authorized = MyAuthorizedLocust()
        response = authorized.client.get("/basic_auth")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Authorized", response.text)
        self.assertEqual(401, locust.client.get("/basic_auth").status_code)
        self.assertEqual(401, unauthorized.client.get("/basic_auth").status_code)


class TestFastHttpCatchResponse(WebserverTestCase):
    def setUp(self):
        super(TestFastHttpCatchResponse, self).setUp()
        
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        self.locust = MyLocust()
        
        self.num_failures = 0
        self.num_success = 0
        def on_failure(request_type, name, response_time, response_length, exception):
            self.num_failures += 1
            self.last_failure_exception = exception
        def on_success(**kwargs):
            self.num_success += 1
        events.request_failure += on_failure
        events.request_success += on_success
        
    def test_catch_response(self):
        self.assertEqual(500, self.locust.client.get("/fail").status_code)
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)
        
        with self.locust.client.get("/ultra_fast", catch_response=True) as response: pass
        self.assertEqual(1, self.num_failures)
        self.assertEqual(1, self.num_success)
        self.assertIn("ultra fast", str(response.content))
        
        with self.locust.client.get("/ultra_fast", catch_response=True) as response:
            raise ResponseError("Not working")
        
        self.assertEqual(2, self.num_failures)
        self.assertEqual(1, self.num_success)
    
    def test_catch_response_http_fail(self):
        with self.locust.client.get("/fail", catch_response=True) as response: pass
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)
    
    def test_catch_response_http_manual_fail(self):
        with self.locust.client.get("/ultra_fast", catch_response=True) as response:
            response.failure("Haha!")
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)
        self.assertTrue(
            isinstance(self.last_failure_exception, CatchResponseError),
            "Failure event handler should have been passed a CatchResponseError instance"
        )
    
    def test_catch_response_http_manual_success(self):
        with self.locust.client.get("/fail", catch_response=True) as response:
            response.success()
        self.assertEqual(0, self.num_failures)
        self.assertEqual(1, self.num_success)
    
    def test_catch_response_allow_404(self):
        with self.locust.client.get("/does/not/exist", catch_response=True) as response:
            self.assertEqual(404, response.status_code)
            if response.status_code == 404:
                response.success()
        self.assertEqual(0, self.num_failures)
        self.assertEqual(1, self.num_success)
    
    def test_interrupt_taskset_with_catch_response(self):
        class MyTaskSet(TaskSet):
            @task
            def interrupted_task(self):
                with self.client.get("/ultra_fast", catch_response=True) as r:
                    raise InterruptTaskSet()
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:%i" % self.port
            task_set = MyTaskSet
        
        l = MyLocust()
        ts = MyTaskSet(l)
        self.assertRaises(InterruptTaskSet, lambda: ts.interrupted_task())
        self.assertEqual(0, self.num_failures)
        self.assertEqual(0, self.num_success)
    
    def test_catch_response_connection_error_success(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:1"
        l = MyLocust()
        with l.client.get("/", catch_response=True) as r:
            self.assertEqual(r.status_code, 0)
            self.assertEqual(None, r.content)
            r.success()
        self.assertEqual(1, self.num_success)
        self.assertEqual(0, self.num_failures)
    
    def test_catch_response_connection_error_fail(self):
        class MyLocust(FastHttpLocust):
            host = "http://127.0.0.1:1"
        l = MyLocust()
        with l.client.get("/", catch_response=True) as r:
            self.assertEqual(r.status_code, 0)
            self.assertEqual(None, r.content)
            r.failure("Manual fail")
        self.assertEqual(0, self.num_success)
        self.assertEqual(1, self.num_failures)
