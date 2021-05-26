import socket
import gevent
from tempfile import NamedTemporaryFile

from locust.user import task, TaskSet
from locust.contrib.fasthttp import FastHttpSession, FastHttpUser
from locust.exception import CatchResponseError, InterruptTaskSet, ResponseError
from locust.main import is_user_class
from .testcases import WebserverTestCase, LocustTestCase
from .util import create_tls_cert


class TestFastHttpSession(WebserverTestCase):
    def get_client(self):
        return FastHttpSession(self.environment, base_url="http://127.0.0.1:%i" % self.port, user=None)

    def test_get(self):
        s = self.get_client()
        r = s.get("/ultra_fast")
        self.assertEqual(200, r.status_code)

    def test_connection_error(self):
        s = FastHttpSession(self.environment, "http://localhost:1", user=None)
        r = s.get("/", timeout=0.1)
        self.assertEqual(r.status_code, 0)
        self.assertEqual(None, r.content)
        self.assertEqual(1, len(self.runner.stats.errors))
        self.assertTrue(isinstance(r.error, ConnectionRefusedError))
        self.assertTrue(isinstance(next(iter(self.runner.stats.errors.values())).error, ConnectionRefusedError))

    def test_404(self):
        s = self.get_client()
        r = s.get("/does_not_exist")
        self.assertEqual(404, r.status_code)
        self.assertEqual(1, self.runner.stats.get("/does_not_exist", "GET").num_failures)

    def test_204(self):
        s = self.get_client()
        r = s.get("/status/204")
        self.assertEqual(204, r.status_code)
        self.assertEqual(1, self.runner.stats.get("/status/204", "GET").num_requests)
        self.assertEqual(0, self.runner.stats.get("/status/204", "GET").num_failures)

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
        self.assertGreaterEqual(self.runner.stats.get("/streaming/30", method="GET").avg_response_time, 0)
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

    def test_patch(self):
        s = self.get_client()
        r = s.patch("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("PATCH", r.content.decode())

    def test_options(self):
        s = self.get_client()
        r = s.options("/request_method")
        self.assertEqual(200, r.status_code)
        self.assertEqual("", r.content.decode())
        self.assertEqual(
            set(["OPTIONS", "DELETE", "PUT", "GET", "POST", "HEAD", "PATCH"]),
            set(r.headers["allow"].split(", ")),
        )

    def test_json_payload(self):
        s = self.get_client()
        r = s.post("/request_method", json={"foo": "bar"})
        self.assertEqual(200, r.status_code)

    def test_catch_response_fail_successful_request(self):
        s = self.get_client()
        with s.get("/ultra_fast", catch_response=True) as r:
            r.failure("nope")
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


class TestRequestStatsWithWebserver(WebserverTestCase):
    def test_request_stats_content_length(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        locust.client.get("/ultra_fast")
        self.assertEqual(
            self.runner.stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response")
        )
        locust.client.get("/ultra_fast")
        self.assertEqual(
            self.runner.stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response")
        )

    def test_request_stats_no_content_length(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        l = MyUser(self.environment)
        path = "/no_content_length"
        r = l.client.get(path)
        self.assertEqual(
            self.runner.stats.get(path, "GET").avg_content_length,
            len("This response does not have content-length in the header"),
        )

    def test_request_stats_no_content_length_streaming(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        l = MyUser(self.environment)
        path = "/no_content_length"
        r = l.client.get(path, stream=True)
        self.assertEqual(0, self.runner.stats.get(path, "GET").avg_content_length)

    def test_request_stats_named_endpoint(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        locust.client.get("/ultra_fast", name="my_custom_name")
        self.assertEqual(1, self.runner.stats.get("my_custom_name", "GET").num_requests)

    def test_request_stats_query_variables(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        locust.client.get("/ultra_fast?query=1")
        self.assertEqual(1, self.runner.stats.get("/ultra_fast?query=1", "GET").num_requests)

    def test_request_stats_put(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        locust.client.put("/put")
        self.assertEqual(1, self.runner.stats.get("/put", "PUT").num_requests)

    def test_request_connection_error(self):
        class MyUser(FastHttpUser):
            host = "http://localhost:1"

        locust = MyUser(self.environment)
        response = locust.client.get("/", timeout=0.1)
        self.assertEqual(response.status_code, 0)
        self.assertEqual(1, self.runner.stats.get("/", "GET").num_failures)
        self.assertEqual(1, self.runner.stats.get("/", "GET").num_requests)


class TestFastHttpUserClass(WebserverTestCase):
    def test_is_abstract(self):
        self.assertTrue(FastHttpUser.abstract)
        self.assertFalse(is_user_class(FastHttpUser))

    def test_class_context(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

            def context(self):
                return {"user": self.username}

        kwargs = {}

        def on_request(**kw):
            kwargs.update(kw)

        self.environment.events.request.add_listener(on_request)
        user = MyUser(self.environment)
        user.username = "foo"
        user.client.request("get", "/request_method")
        self.assertDictEqual({"user": "foo"}, kwargs["context"])
        self.assertEqual("GET", kwargs["response"].text)
        user.client.request("get", "/request_method", context={"user": "bar"})
        self.assertDictEqual({"user": "bar"}, kwargs["context"])

    def test_get_request(self):
        self.response = ""

        def t1(l):
            self.response = l.client.get("/ultra_fast")

        class MyUser(FastHttpUser):
            tasks = [t1]
            host = "http://127.0.0.1:%i" % self.port

        my_locust = MyUser(self.environment)
        t1(my_locust)
        self.assertEqual(self.response.text, "This is an ultra fast response")

    def test_client_request_headers(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        self.assertEqual("hello", locust.client.get("/request_header_test", headers={"X-Header-Test": "hello"}).text)

    def test_client_get(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        self.assertEqual("GET", locust.client.get("/request_method").text)

    def test_client_get_absolute_url(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        self.assertEqual("GET", locust.client.get("http://127.0.0.1:%i/request_method" % self.port).text)

    def test_client_post(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        self.assertEqual("POST", locust.client.post("/request_method", {"arg": "hello world"}).text)
        self.assertEqual("hello world", locust.client.post("/post", {"arg": "hello world"}).text)

    def test_client_put(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        self.assertEqual("PUT", locust.client.put("/request_method", {"arg": "hello world"}).text)
        self.assertEqual("hello world", locust.client.put("/put", {"arg": "hello world"}).text)

    def test_client_delete(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        self.assertEqual("DELETE", locust.client.delete("/request_method").text)
        self.assertEqual(200, locust.client.delete("/request_method").status_code)

    def test_client_head(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        self.assertEqual(200, locust.client.head("/request_method").status_code)

    def test_log_request_name_argument(self):
        self.response = ""

        class MyUser(FastHttpUser):
            tasks = []
            host = "http://127.0.0.1:%i" % self.port

            @task()
            def t1(l):
                self.response = l.client.get("/ultra_fast", name="new name!")

        my_locust = MyUser(self.environment)
        my_locust.t1()

        self.assertEqual(1, self.runner.stats.get("new name!", "GET").num_requests)
        self.assertEqual(0, self.runner.stats.get("/ultra_fast", "GET").num_requests)

    def test_redirect_url_original_path_as_name(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        l = MyUser(self.environment)
        l.client.get("/redirect")

        self.assertEqual(1, len(self.runner.stats.entries))
        self.assertEqual(1, self.runner.stats.get("/redirect", "GET").num_requests)
        self.assertEqual(0, self.runner.stats.get("/ultra_fast", "GET").num_requests)

    def test_network_timeout_setting(self):
        class MyUser(FastHttpUser):
            network_timeout = 0.5
            host = "http://127.0.0.1:%i" % self.port

        l = MyUser(self.environment)

        timeout = gevent.Timeout(
            seconds=0.6,
            exception=AssertionError(
                "Request took longer than 0.6 even though FastHttpUser.network_timeout was set to 0.5"
            ),
        )
        timeout.start()
        r = l.client.get("/redirect?url=/redirect&delay=5.0")
        timeout.cancel()

        self.assertTrue(isinstance(r.error.original, socket.timeout))
        self.assertEqual(1, self.runner.stats.get("/redirect?url=/redirect&delay=5.0", "GET").num_failures)

    def test_max_redirect_setting(self):
        class MyUser(FastHttpUser):
            max_redirects = 1  # max_redirects and max_retries are funny names, because they are actually max attempts
            host = "http://127.0.0.1:%i" % self.port

        l = MyUser(self.environment)
        l.client.get("/redirect")
        self.assertEqual(1, self.runner.stats.get("/redirect", "GET").num_failures)

    def test_allow_redirects_override(self):
        class MyLocust(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        l = MyLocust(self.environment)
        resp = l.client.get("/redirect", allow_redirects=False)
        self.assertEqual("http://127.0.0.1:%i/ultra_fast" % self.port, resp.headers["location"])
        resp = l.client.get("/redirect")  # ensure redirect still works
        self.assertFalse("location" in resp.headers)

    def test_slow_redirect(self):
        s = FastHttpSession(self.environment, "http://127.0.0.1:%i" % self.port, user=None)
        url = "/redirect?url=/redirect&delay=0.5"
        r = s.get(url)
        stats = self.runner.stats.get(url, method="GET")
        self.assertEqual(1, stats.num_requests)
        self.assertGreater(stats.avg_response_time, 500)

    def test_client_basic_auth(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        class MyAuthorizedUser(FastHttpUser):
            host = "http://locust:menace@127.0.0.1:%i" % self.port

        class MyUnauthorizedUser(FastHttpUser):
            host = "http://locust:wrong@127.0.0.1:%i" % self.port

        locust = MyUser(self.environment)
        unauthorized = MyUnauthorizedUser(self.environment)
        authorized = MyAuthorizedUser(self.environment)
        response = authorized.client.get("/basic_auth")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Authorized", response.text)
        self.assertEqual(401, locust.client.get("/basic_auth").status_code)
        self.assertEqual(401, unauthorized.client.get("/basic_auth").status_code)


class TestFastHttpCatchResponse(WebserverTestCase):
    def setUp(self):
        super().setUp()

        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port

        self.locust = MyUser(self.environment)

        self.num_failures = 0
        self.num_success = 0

        def on_request(exception, **kwargs):
            if exception:
                self.num_failures += 1
                self.last_failure_exception = exception
            else:
                self.num_success += 1

        self.environment.events.request.add_listener(on_request)

    def test_catch_response(self):
        self.assertEqual(500, self.locust.client.get("/fail").status_code)
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)

        with self.locust.client.get("/ultra_fast", catch_response=True) as response:
            pass
        self.assertEqual(1, self.num_failures)
        self.assertEqual(1, self.num_success)
        self.assertIn("ultra fast", str(response.content))

        with self.locust.client.get("/ultra_fast", catch_response=True) as response:
            raise ResponseError("Not working")

        self.assertEqual(2, self.num_failures)
        self.assertEqual(1, self.num_success)

    def test_catch_response_http_fail(self):
        with self.locust.client.get("/fail", catch_response=True) as response:
            pass
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)

    def test_catch_response_http_manual_fail(self):
        with self.locust.client.get("/ultra_fast", catch_response=True) as response:
            response.failure("Haha!")
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)
        self.assertTrue(
            isinstance(self.last_failure_exception, CatchResponseError),
            "Failure event handler should have been passed a CatchResponseError instance",
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

        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:%i" % self.port
            tasks = [MyTaskSet]

        l = MyUser(self.environment)
        ts = MyTaskSet(l)
        self.assertRaises(InterruptTaskSet, lambda: ts.interrupted_task())
        self.assertEqual(0, self.num_failures)
        self.assertEqual(0, self.num_success)

    def test_catch_response_connection_error_success(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:1"

        l = MyUser(self.environment)
        with l.client.get("/", catch_response=True) as r:
            self.assertEqual(r.status_code, 0)
            self.assertEqual(None, r.content)
            r.success()
        self.assertEqual(1, self.num_success)
        self.assertEqual(0, self.num_failures)

    def test_catch_response_connection_error_fail(self):
        class MyUser(FastHttpUser):
            host = "http://127.0.0.1:1"

        l = MyUser(self.environment)
        with l.client.get("/", catch_response=True) as r:
            self.assertEqual(r.status_code, 0)
            self.assertEqual(None, r.content)
            r.failure("Manual fail")
        self.assertEqual(0, self.num_success)
        self.assertEqual(1, self.num_failures)

    def test_deprecated_request_events(self):
        status = {"success_amount": 0, "failure_amount": 0}

        def on_success(**kw):
            status["success_amount"] += 1

        def on_failure(**kw):
            status["failure_amount"] += 1

        self.environment.events.request_success.add_listener(on_success)
        self.environment.events.request_failure.add_listener(on_failure)
        with self.locust.client.get("/ultra_fast", catch_response=True) as response:
            pass
        with self.locust.client.get("/wrong_url", catch_response=True) as response:
            pass

        self.assertEqual(1, status["success_amount"])
        self.assertEqual(1, status["failure_amount"])


class TestFastHttpSsl(LocustTestCase):
    def setUp(self):
        super().setUp()
        tls_cert, tls_key = create_tls_cert("127.0.0.1")
        self.tls_cert_file = NamedTemporaryFile()
        self.tls_key_file = NamedTemporaryFile()
        with open(self.tls_cert_file.name, "w") as f:
            f.write(tls_cert.decode())
        with open(self.tls_key_file.name, "w") as f:
            f.write(tls_key.decode())

        self.web_ui = self.environment.create_web_ui(
            "127.0.0.1",
            0,
            tls_cert=self.tls_cert_file.name,
            tls_key=self.tls_key_file.name,
        )
        gevent.sleep(0.01)
        self.web_port = self.web_ui.server.server_port

    def tearDown(self):
        super().tearDown()
        self.web_ui.stop()

    def test_ssl_request_insecure(self):
        s = FastHttpSession(self.environment, "https://127.0.0.1:%i" % self.web_port, insecure=True, user=None)
        r = s.get("/")
        self.assertEqual(200, r.status_code)
        self.assertIn("<title>Locust</title>", r.content.decode("utf-8"))
