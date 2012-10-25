import unittest

from locust.core import Locust, SubLocust, require_once, task, events, RescheduleTaskImmediately
from locust import ResponseError, InterruptLocust
from locust.exception import CatchResponseError

from testcases import WebserverTestCase

class TestLocustClass(unittest.TestCase):
    def test_task_ratio(self):
        t1 = lambda l: None
        t2 = lambda l: None
        class MyLocust(Locust):
            tasks = {t1:5, t2:2}
            host = ""
        
        l = MyLocust()

        t1_count = len([t for t in l.tasks if t == t1])
        t2_count = len([t for t in l.tasks if t == t2])

        self.assertEqual(t1_count, 5)
        self.assertEqual(t2_count, 2)
    
    def test_task_decorator_ratio(self):
        t1 = lambda l: None
        t2 = lambda l: None
        class MyLocust(Locust):
            tasks = {t1:5, t2:2}
            host = ""
            
            @task(3)
            def t3(self):
                pass
            
            @task(13)
            def t4(self):
                pass
            

        l = MyLocust()

        t1_count = len([t for t in l.tasks if t == t1])
        t2_count = len([t for t in l.tasks if t == t2])
        t3_count = len([t for t in l.tasks if t.__name__ == MyLocust.t3.__name__])
        t4_count = len([t for t in l.tasks if t.__name__ == MyLocust.t4.__name__])

        self.assertEqual(t1_count, 5)
        self.assertEqual(t2_count, 2)
        self.assertEqual(t3_count, 3)
        self.assertEqual(t4_count, 13)

    def test_require_once(self):
        self.t1_executed = False
        self.t2_executed = False
        def t1(l):
            self.t1_executed = True

        @require_once(t1)
        def t2(l):
            self.t2_executed = True

        class MyLocust(Locust):
            tasks = [t2]
            host = ""

        l = MyLocust()
        l.schedule_task(l.get_next_task())
        l.execute_next_task()
        self.assertTrue(self.t1_executed)
        self.assertFalse(self.t2_executed)
        l.execute_next_task()
        self.assertTrue(self.t2_executed)

    def test_schedule_task(self):
        self.t1_executed = False
        self.t2_arg = None

        def t1(l):
            self.t1_executed = True

        def t2(l, arg):
            self.t2_arg = arg

        class MyLocust(Locust):
            tasks = [t1, t2]
            host = ""

        locust = MyLocust()
        locust.schedule_task(t1)
        locust.execute_next_task()
        self.assertTrue(self.t1_executed)

        locust.schedule_task(t2, args=["argument to t2"])
        locust.execute_next_task()
        self.assertEqual("argument to t2", self.t2_arg)
    
    def test_schedule_task_with_kwargs(self):
        class MyLocust(Locust):
            host = ""
            @task
            def t1(self):
                self.t1_executed = True
            @task
            def t2(self, *args, **kwargs):
                self.t2_args = args
                self.t2_kwargs = kwargs
        loc = MyLocust()
        loc.schedule_task(loc.t2, [42], {"test_kw":"hello"})
        loc.execute_next_task()
        self.assertEqual((42, ), loc.t2_args)
        self.assertEqual({"test_kw":"hello"}, loc.t2_kwargs)
        
        loc.schedule_task(loc.t2, args=[10, 4], kwargs={"arg1":1, "arg2":2})
        loc.execute_next_task()
        self.assertEqual((10, 4), loc.t2_args)
        self.assertEqual({"arg1":1, "arg2":2}, loc.t2_kwargs)
    
    def test_schedule_task_bound_method(self):
        class MyLocust(Locust):
            host = ""
            
            @task()
            def t1(self):
                self.t1_executed = True
                self.schedule_task(self.t2)
            def t2(self):
                self.t2_executed = True
        
        locust = MyLocust()
        locust.schedule_task(locust.get_next_task())
        locust.execute_next_task()
        self.assertTrue(locust.t1_executed)
        locust.execute_next_task()
        self.assertTrue(locust.t2_executed)
        
    
    def test_locust_inheritance(self):
        def t1(l):
            pass
        class MyBaseLocust(Locust):
            tasks = [t1]
            host = ""
        class MySubLocust(MyBaseLocust):
            pass
        
        l = MySubLocust()
        self.assertEqual(1, len(l.tasks))
    
    def test_task_decorator_with_or_without_argument(self):
        class MyLocust(Locust):
            host = ""
            @task
            def t1(self):
                pass
        locust = MyLocust()
        self.assertEqual(len(locust.tasks), 1)
        
        class MyLocust2(Locust):
            host = ""
            @task()
            def t1(self):
                pass
        locust = MyLocust2()
        self.assertEqual(len(locust.tasks), 1)
        
        class MyLocust3(Locust):
            host = ""
            @task(3)
            def t1(self):
                pass
        locust = MyLocust3()
        self.assertEqual(len(locust.tasks), 3)

class TestSubLocust(unittest.TestCase):
    def test_sub_locust(self):
        class MySubLocust(SubLocust):
            min_wait=1
            max_wait=1
            @task()
            def a_task(self):
                self.parent.sub_locust_task_executed = True
                self.interrupt()
        class MyLocust(Locust):
            host = ""
            sub_locust_task_executed = False
            tasks = [MySubLocust]
        
        loc = MyLocust()
        loc.schedule_task(loc.get_next_task())
        self.assertRaises(RescheduleTaskImmediately, lambda: loc.execute_next_task())
        self.assertTrue(loc.sub_locust_task_executed)
    
    def test_sub_locust_arguments(self):
        class MySubLocust(SubLocust):
            min_wait=1
            max_wait=1
            @task()
            def a_task(self):
                self.parent.sub_locust_args = self.args
                self.parent.sub_locust_kwargs = self.kwargs
                self.interrupt()
        class MyLocust(Locust):
            host = ""
            sub_locust_args = None
            sub_locust_kwargs = None
            tasks = [MySubLocust]
        
        loc = MyLocust()
        loc.schedule_task(MySubLocust, args=[1,2,3], kwargs={"hello":"world"})
        self.assertRaises(RescheduleTaskImmediately, lambda: loc.execute_next_task())
        self.assertEqual((1,2,3), loc.sub_locust_args)
        self.assertEqual({"hello":"world"}, loc.sub_locust_kwargs)
    

class TestWebLocustClass(WebserverTestCase):
    def test_get_request(self):
        self.response = ""
        def t1(l):
            self.response = l.client.get("/ultra_fast")
        class MyLocust(Locust):
            tasks = [t1]
            host = "http://127.0.0.1:%i" % self.port

        my_locust = MyLocust()
        t1(my_locust)
        self.assertEqual(self.response.content, "This is an ultra fast response")

    def test_client_request_headers(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("hello", locust.client.get("/request_header_test", headers={"X-Header-Test":"hello"}).content)

    def test_client_get(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("GET", locust.client.get("/request_method").content)
    
    def test_client_get_absolute_url(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("GET", locust.client.get("http://127.0.0.1:%i/request_method" % self.port).content)

    def test_client_post(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("POST", locust.client.post("/request_method", {"arg":"hello world"}).content)
        self.assertEqual("hello world", locust.client.post("/post", {"arg":"hello world"}).content)

    def test_client_put(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("PUT", locust.client.put("/request_method", {"arg":"hello world"}).content)
        self.assertEqual("hello world", locust.client.put("/put", {"arg":"hello world"}).content)

    def test_client_delete(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("DELETE", locust.client.delete("/request_method").content)
        self.assertEqual(200, locust.client.delete("/request_method").status_code)

    def test_client_head(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual(200, locust.client.head("/request_method").status_code)

    def test_client_basic_auth(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        class MyAuthorizedLocust(Locust):
            host = "http://locust:menace@127.0.0.1:%i" % self.port

        class MyUnauthorizedLocust(Locust):
            host = "http://locust:wrong@127.0.0.1:%i" % self.port

        locust = MyLocust()
        unauthorized = MyUnauthorizedLocust()
        authorized = MyAuthorizedLocust()
        self.assertEqual("Authorized", authorized.client.get("/basic_auth").content)
        self.assertFalse(locust.client.get("/basic_auth"))
        self.assertFalse(unauthorized.client.get("/basic_auth"))
    
    def test_log_request_name_argument(self):
        from locust.stats import RequestStats
        self.response = ""
        
        class MyLocust(Locust):
            tasks = []
            host = "http://127.0.0.1:%i" % self.port
            
            @task()
            def t1(l):
                self.response = l.client.get("/ultra_fast", name="new name!")

        my_locust = MyLocust()
        my_locust.t1()
        
        self.assertEqual(1, RequestStats.get("GET", "new name!").num_reqs)
        self.assertEqual(0, RequestStats.get("GET", "/ultra_fast").num_reqs)


class TestCatchResponse(WebserverTestCase):
    def setUp(self):
        super(TestCatchResponse, self).setUp()
        
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        self.locust = MyLocust()
        
        self.num_failures = 0
        self.num_success = 0
        def on_failure(method, path, response_time, exception, response):
            self.num_failures += 1
            self.last_failure_exception = exception
        def on_success(a, b, c, d):
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
        
        with self.locust.client.get("/ultra_fast", catch_response=True) as response:
            raise ResponseError("Not working")
        
        self.assertEqual(2, self.num_failures)
        self.assertEqual(1, self.num_success)
    
    def test_catch_response_http_fail(self):
        with self.locust.client.get("/fail", catch_response=True) as catched: pass
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)
    
    def test_catch_response_http_manual_fail(self):
        with self.locust.client.get("/ultra_fast", catch_response=True) as catched:
            catched.failure("Haha!")
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)
        self.assertIsInstance(self.last_failure_exception, CatchResponseError)
    
    def test_catch_response_http_manual_success(self):
        with self.locust.client.get("/fail", catch_response=True) as catched:
            catched.success()
        self.assertEqual(0, self.num_failures)
        self.assertEqual(1, self.num_success)
    
    def test_interrupt_locust_with_catch_response(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port
            @task
            def interrupted_task(self):
                with self.client.get("/ultra_fast", catch_response=True) as r:
                    raise InterruptLocust()
        
        l = MyLocust()
        self.assertRaises(InterruptLocust, lambda: l.interrupted_task())
        self.assertEqual(0, self.num_failures)
        self.assertEqual(0, self.num_success)
