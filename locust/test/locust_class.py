from locust.core import Locust, require_once, task, events
from locust.clients import HttpBrowser
from locust import ResponseError, InterruptLocust
import unittest
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

        locust.schedule_task(t2, "argument to t2")
        locust.execute_next_task()
        self.assertEqual("argument to t2", self.t2_arg)
    
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
        self.assertEqual(self.response.data, "This is an ultra fast response")

    def test_client_request_headers(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("hello", locust.client.get("/request_header_test", {"X-Header-Test":"hello"}).data)

    def test_client_get(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("GET", locust.client.get("/request_method").data)

    def test_client_post(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("POST", locust.client.post("/request_method", {"arg":"hello world"}).data)
        self.assertEqual("hello world", locust.client.post("/post", {"arg":"hello world"}).data)

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
        self.assertEqual("Authorized", authorized.client.get("/basic_auth").data)
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
        
        self.assertEqual(1, RequestStats.get("new name!").num_reqs)
        self.assertEqual(0, RequestStats.get("/ultra_fast").num_reqs)
    
    def test_catch_response(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()

        num = {'failures': 0, 'success': 0}
        def on_failure(path, response_time, exception, response): num['failures'] += 1
        def on_success(a, b, c): num['success'] += 1

        events.request_failure += on_failure
        events.request_success += on_success

        self.assertEqual(None, locust.client.get("/fail"))
        self.assertEqual(1, num['failures'])
        self.assertEqual(0, num['success'])

        with locust.client.get("/ultra_fast", catch_response=True) as response: pass
        self.assertEqual(1, num['failures'])
        self.assertEqual(1, num['success'])

        with locust.client.get("/ultra_fast", catch_response=True) as response:
            raise ResponseError("Not working")

        self.assertEqual(2, num['failures'])
        self.assertEqual(1, num['success'])
    
    def test_allow_http_error(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port
        l = MyLocust()
        
        num = {'failures': 0, 'success': 0}
        def on_failure(path, response_time, exception, response): num['failures'] += 1
        def on_success(a, b, c): num['success'] += 1
        events.request_failure += on_failure
        events.request_success += on_success
        
        l.client.get("/fail", allow_http_error=True)
        self.assertEqual(num["failures"], 0)
        
        with l.client.get("/fail", allow_http_error=True, catch_response=True) as r:
            raise ResponseError("Not working")
        self.assertEqual(num["failures"], 1)
    
    def test_interrupt_locust_with_catch_response(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port
            @task
            def interrupted_task(self):
                with self.client.get("/ultra_fast", catch_response=True) as r:
                    raise InterruptLocust()
        
        num = {'failures': 0, 'success': 0}
        def on_failure(path, response_time, exception, response): num['failures'] += 1
        def on_success(a, b, c): num['success'] += 1
        events.request_failure += on_failure
        events.request_success += on_success
        
        l = MyLocust()
        self.assertRaises(InterruptLocust, lambda: l.interrupted_task())
        self.assertEqual(num["failures"], 0)
