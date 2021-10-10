import time

from locust.user.users import HttpUser
from requests.exceptions import InvalidSchema, InvalidURL, MissingSchema, RequestException

from locust.clients import HttpSession
from locust.exception import ResponseError
from .testcases import WebserverTestCase


class TestHttpSession(WebserverTestCase):
    def get_client(self, base_url=None):
        if base_url is None:
            base_url = "http://127.0.0.1:%i" % self.port
        return HttpSession(
            base_url=base_url,
            request_event=self.environment.events.request,
            user=None,
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
            ("http://\x94", InvalidURL),
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
        self.assertEqual("1337", r.content.decode())

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

    def test_error_message(self):
        s = self.get_client()
        kwargs = {}

        def on_request(**kw):
            kwargs.update(kw)

        self.environment.events.request.add_listener(on_request)
        s.request("get", "/wrong_url", context={"foo": "bar"})
        self.assertIn("/wrong_url", str(kwargs["exception"]))
        self.assertDictEqual({"foo": "bar"}, kwargs["context"])

    def test_context_in_success(self):
        s = self.get_client()
        kwargs = {}

        def on_request(exception, **kw):
            self.assertIsNone(exception)
            kwargs.update(kw)

        self.environment.events.request.add_listener(on_request)
        s.request("get", "/request_method", context={"foo": "bar"})
        self.assertDictEqual({"foo": "bar"}, kwargs["context"])

    def test_response_parameter(self):
        s = self.get_client()
        kwargs = {}

        def on_request(**kw):
            kwargs.update(kw)

        self.environment.events.request.add_listener(on_request)
        s.request("get", "/request_method")
        self.assertEqual("GET", kwargs["response"].text)
        s.request("get", "/wrong_url")
        self.assertEqual("Not Found", kwargs["response"].text)

    def test_deprecated_request_events(self):
        s = self.get_client()
        status = {"success_amount": 0, "failure_amount": 0}

        def on_success(**kw):
            status["success_amount"] += 1

        def on_failure(**kw):
            status["failure_amount"] += 1

        self.environment.events.request_success.add_listener(on_success)
        self.environment.events.request_failure.add_listener(on_failure)
        s.request("get", "/request_method")
        s.request("get", "/wrong_url")
        self.assertEqual(1, status["success_amount"])
        self.assertEqual(1, status["failure_amount"])

    def test_error_message_with_name_replacement(self):
        s = self.get_client()
        kwargs = {}

        def on_request(**kw):
            self.assertIsNotNone(kw["exception"])
            kwargs.update(kw)

        self.environment.events.request.add_listener(on_request)
        before_request = time.time()
        s.request("get", "/wrong_url/01", name="replaced_url_name", context={"foo": "bar"})
        after_request = time.time()
        self.assertIn("for url: replaced_url_name", str(kwargs["exception"]))
        self.assertAlmostEqual(before_request, kwargs["start_time"], delta=0.01)
        self.assertAlmostEqual(after_request, kwargs["start_time"] + kwargs["response_time"] / 1000, delta=0.01)
        self.assertEqual("/wrong_url/01", kwargs["url"])  # url is unaffected by name
        self.assertDictEqual({"foo": "bar"}, kwargs["context"])

    def test_get_with_params(self):
        s = self.get_client()
        r = s.get("/get_arg", params={"arg": "test_123"})
        self.assertEqual(200, r.status_code)
        self.assertEqual("test_123", r.text)

    def test_catch_response_fail_successful_request(self):
        s = self.get_client()
        with s.get("/ultra_fast", catch_response=True) as r:
            r.failure("nope")
        self.assertEqual(1, self.environment.stats.get("/ultra_fast", "GET").num_requests)
        self.assertEqual(1, self.environment.stats.get("/ultra_fast", "GET").num_failures)

    def test_catch_response_fail_successful_request_with_non_string_error_message(self):
        s = self.get_client()
        with s.get("/ultra_fast", catch_response=True) as r:
            r.failure({"other types are also wrapped as exceptions": True})
        self.assertEqual(1, self.environment.stats.get("/ultra_fast", "GET").num_requests)
        self.assertEqual(1, self.environment.stats.get("/ultra_fast", "GET").num_failures)

    def test_catch_response_pass_failed_request(self):
        s = self.get_client()
        with s.get("/fail", catch_response=True) as r:
            r.success()
        self.assertEqual(1, self.environment.stats.total.num_requests)
        self.assertEqual(0, self.environment.stats.total.num_failures)

    def test_catch_response_multiple_failure_and_success(self):
        s = self.get_client()
        with s.get("/ultra_fast", catch_response=True) as r:
            r.failure("nope")
            r.success()
            r.failure("nooo")
            r.success()
        self.assertEqual(1, self.environment.stats.total.num_requests)
        self.assertEqual(0, self.environment.stats.total.num_failures)

    def test_catch_response_pass_failed_request_with_other_exception_within_block(self):
        class OtherException(Exception):
            pass

        s = self.get_client()
        try:
            with s.get("/fail", catch_response=True) as r:
                r.success()
                raise OtherException("wtf")
        except OtherException as e:
            pass
        else:
            self.fail("OtherException should have been raised")

        self.assertEqual(1, self.environment.stats.total.num_requests)
        self.assertEqual(0, self.environment.stats.total.num_failures)

    def test_catch_response_response_error(self):
        s = self.get_client()
        try:
            with s.get("/fail", catch_response=True) as r:
                raise ResponseError("response error")
        except ResponseError as e:
            self.fail("ResponseError should not have been raised")

        self.assertEqual(1, self.environment.stats.total.num_requests)
        self.assertEqual(1, self.environment.stats.total.num_failures)

    def test_catch_response_default_success(self):
        s = self.get_client()
        with s.get("/ultra_fast", catch_response=True) as r:
            pass
        self.assertEqual(1, self.environment.stats.get("/ultra_fast", "GET").num_requests)
        self.assertEqual(0, self.environment.stats.get("/ultra_fast", "GET").num_failures)

    def test_catch_response_default_fail(self):
        s = self.get_client()
        with s.get("/fail", catch_response=True) as r:
            pass
        self.assertEqual(1, self.environment.stats.total.num_requests)
        self.assertEqual(1, self.environment.stats.total.num_failures)

    def test_user_context(self):
        class TestUser(HttpUser):
            host = f"http://127.0.0.1:{self.port}"

            def context(self):
                return {"user": self.username}

        kwargs = {}

        def on_request(**kw):
            kwargs.update(kw)

        self.environment.events.request.add_listener(on_request)

        user = TestUser(self.environment)
        user.username = "foo"
        user.client.request("get", "/request_method")
        self.assertDictEqual({"user": "foo"}, kwargs["context"])
        self.assertEqual("GET", kwargs["response"].text)
        user.client.request("get", "/request_method", context={"user": "bar"})  # override User context
        self.assertDictEqual({"user": "bar"}, kwargs["context"])
