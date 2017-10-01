import six

from locust import InterruptTaskSet, ResponseError
from locust.core import HttpLocust, Locust, TaskSet, events, task
from locust.exception import (CatchResponseError, LocustError, RescheduleTask,
                              RescheduleTaskImmediately)

from .testcases import LocustTestCase, WebserverTestCase


class TestTaskSet(LocustTestCase):
    def setUp(self):
        super(TestTaskSet, self).setUp()
        
        class User(Locust):
            host = "127.0.0.1"
        self.locust = User()
    
    def test_task_ratio(self):
        t1 = lambda l: None
        t2 = lambda l: None
        class MyTasks(TaskSet):
            tasks = {t1:5, t2:2}
        
        l = MyTasks(self.locust)

        t1_count = len([t for t in l.tasks if t == t1])
        t2_count = len([t for t in l.tasks if t == t2])

        self.assertEqual(t1_count, 5)
        self.assertEqual(t2_count, 2)
    
    def test_task_decorator_ratio(self):
        t1 = lambda l: None
        t2 = lambda l: None
        class MyTasks(TaskSet):
            tasks = {t1:5, t2:2}
            host = ""
            
            @task(3)
            def t3(self):
                pass
            
            @task(13)
            def t4(self):
                pass
            

        l = MyTasks(self.locust)

        t1_count = len([t for t in l.tasks if t == t1])
        t2_count = len([t for t in l.tasks if t == t2])
        t3_count = len([t for t in l.tasks if t.__name__ == MyTasks.t3.__name__])
        t4_count = len([t for t in l.tasks if t.__name__ == MyTasks.t4.__name__])

        self.assertEqual(t1_count, 5)
        self.assertEqual(t2_count, 2)
        self.assertEqual(t3_count, 3)
        self.assertEqual(t4_count, 13)

    def test_on_start(self):
        class MyTasks(TaskSet):
            t1_executed = False
            t2_executed = False
            
            def on_start(self):
                self.t1()
            
            def t1(self):
                self.t1_executed = True
            
            @task
            def t2(self):
                self.t2_executed = True
                raise InterruptTaskSet(reschedule=False)

        l = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: l.run())
        self.assertTrue(l.t1_executed)
        self.assertTrue(l.t2_executed)

    def test_schedule_task(self):
        self.t1_executed = False
        self.t2_arg = None

        def t1(l):
            self.t1_executed = True

        def t2(l, arg):
            self.t2_arg = arg

        class MyTasks(TaskSet):
            tasks = [t1, t2]

        taskset = MyTasks(self.locust)
        taskset.schedule_task(t1)
        taskset.execute_next_task()
        self.assertTrue(self.t1_executed)

        taskset.schedule_task(t2, args=["argument to t2"])
        taskset.execute_next_task()
        self.assertEqual("argument to t2", self.t2_arg)
    
    def test_schedule_task_with_kwargs(self):
        class MyTasks(TaskSet):
            @task
            def t1(self):
                self.t1_executed = True
            @task
            def t2(self, *args, **kwargs):
                self.t2_args = args
                self.t2_kwargs = kwargs
        loc = MyTasks(self.locust)
        loc.schedule_task(loc.t2, [42], {"test_kw":"hello"})
        loc.execute_next_task()
        self.assertEqual((42, ), loc.t2_args)
        self.assertEqual({"test_kw":"hello"}, loc.t2_kwargs)
        
        loc.schedule_task(loc.t2, args=[10, 4], kwargs={"arg1":1, "arg2":2})
        loc.execute_next_task()
        self.assertEqual((10, 4), loc.t2_args)
        self.assertEqual({"arg1":1, "arg2":2}, loc.t2_kwargs)
    
    def test_schedule_task_bound_method(self):
        class MyTasks(TaskSet):
            host = ""
            
            @task()
            def t1(self):
                self.t1_executed = True
                self.schedule_task(self.t2)
            def t2(self):
                self.t2_executed = True
        
        taskset = MyTasks(self.locust)
        taskset.schedule_task(taskset.get_next_task())
        taskset.execute_next_task()
        self.assertTrue(taskset.t1_executed)
        taskset.execute_next_task()
        self.assertTrue(taskset.t2_executed)
        
    
    def test_taskset_inheritance(self):
        def t1(l):
            pass
        class MyBaseTaskSet(TaskSet):
            tasks = [t1]
            host = ""
        class MySubTaskSet(MyBaseTaskSet):
            @task
            def t2(self):
                pass
        
        l = MySubTaskSet(self.locust)
        self.assertEqual(2, len(l.tasks))
        self.assertEqual([t1, six.get_unbound_function(MySubTaskSet.t2)], l.tasks)
    
    def test_task_decorator_with_or_without_argument(self):
        class MyTaskSet(TaskSet):
            @task
            def t1(self):
                pass
        taskset = MyTaskSet(self.locust)
        self.assertEqual(len(taskset.tasks), 1)
        
        class MyTaskSet2(TaskSet):
            @task()
            def t1(self):
                pass
        taskset = MyTaskSet2(self.locust)
        self.assertEqual(len(taskset.tasks), 1)
        
        class MyTaskSet3(TaskSet):
            @task(3)
            def t1(self):
                pass
        taskset = MyTaskSet3(self.locust)
        self.assertEqual(len(taskset.tasks), 3)
    
    def test_sub_taskset(self):
        class MySubTaskSet(TaskSet):
            min_wait = 1
            max_wait = 1
            @task()
            def a_task(self):
                self.locust.sub_locust_task_executed = True
                self.interrupt()
            
        class MyTaskSet(TaskSet):
            tasks = [MySubTaskSet]
        
        self.sub_locust_task_executed = False
        loc = MyTaskSet(self.locust)
        loc.schedule_task(loc.get_next_task())
        self.assertRaises(RescheduleTaskImmediately, lambda: loc.execute_next_task())
        self.assertTrue(self.locust.sub_locust_task_executed)
    
    def test_sub_taskset_tasks_decorator(self):
        class MyTaskSet(TaskSet):
            @task
            class MySubTaskSet(TaskSet):
                min_wait = 1
                max_wait = 1
                @task()
                def a_task(self):
                    self.locust.sub_locust_task_executed = True
                    self.interrupt()
        
        self.sub_locust_task_executed = False
        loc = MyTaskSet(self.locust)
        loc.schedule_task(loc.get_next_task())
        self.assertRaises(RescheduleTaskImmediately, lambda: loc.execute_next_task())
        self.assertTrue(self.locust.sub_locust_task_executed)
    
    def test_sub_taskset_arguments(self):
        class MySubTaskSet(TaskSet):
            min_wait = 1
            max_wait = 1
            @task()
            def a_task(self):
                self.locust.sub_taskset_args = self.args
                self.locust.sub_taskset_kwargs = self.kwargs
                self.interrupt()
        class MyTaskSet(TaskSet):
            sub_locust_args = None
            sub_locust_kwargs = None
            tasks = [MySubTaskSet]
        
        self.locust.sub_taskset_args = None
        self.locust.sub_taskset_kwargs = None
        
        loc = MyTaskSet(self.locust)
        loc.schedule_task(MySubTaskSet, args=[1,2,3], kwargs={"hello":"world"})
        self.assertRaises(RescheduleTaskImmediately, lambda: loc.execute_next_task())
        self.assertEqual((1,2,3), self.locust.sub_taskset_args)
        self.assertEqual({"hello":"world"}, self.locust.sub_taskset_kwargs)
    
    def test_interrupt_taskset_in_main_taskset(self):
        class MyTaskSet(TaskSet):
            @task
            def interrupted_task(self):
                raise InterruptTaskSet(reschedule=False)
        class MyLocust(Locust):
            host = "http://127.0.0.1"
            task_set = MyTaskSet
        
        class MyTaskSet2(TaskSet):
            @task
            def interrupted_task(self):
                self.interrupt()
        class MyLocust2(Locust):
            host = "http://127.0.0.1"
            task_set = MyTaskSet2
        
        l = MyLocust()
        l2 = MyLocust2()
        self.assertRaises(LocustError, lambda: l.run())
        self.assertRaises(LocustError, lambda: l2.run())
        
        try:
            l.run()
        except LocustError as e:
            self.assertTrue("MyLocust" in e.args[0], "MyLocust should have been referred to in the exception message")
            self.assertTrue("MyTaskSet" in e.args[0], "MyTaskSet should have been referred to in the exception message")
        except:
            raise
        
        try:
            l2.run()
        except LocustError as e:
            self.assertTrue("MyLocust2" in e.args[0], "MyLocust2 should have been referred to in the exception message")
            self.assertTrue("MyTaskSet2" in e.args[0], "MyTaskSet2 should have been referred to in the exception message")
        except:
            raise
    
    def test_on_start_interrupt(self):
        class SubTaskSet(TaskSet):
            def on_start(self):
                if self.kwargs["reschedule"]:
                    self.interrupt(reschedule=True)
                else:
                    self.interrupt(reschedule=False)
        
        class MyLocust(Locust):
            host = ""
            task_set = SubTaskSet
        
        l = MyLocust()
        task_set = SubTaskSet(l)
        self.assertRaises(RescheduleTaskImmediately, lambda: task_set.run(reschedule=True))
        self.assertRaises(RescheduleTask, lambda: task_set.run(reschedule=False))

    
    def test_parent_attribute(self):
        from locust.exception import StopLocust
        parents = {}
        
        class SubTaskSet(TaskSet):
            def on_start(self):
                parents["sub"] = self.parent
            
            @task
            class SubSubTaskSet(TaskSet):
                def on_start(self):
                    parents["subsub"] = self.parent
                @task
                def stop(self):
                    raise StopLocust()
        class RootTaskSet(TaskSet):
            tasks = [SubTaskSet]
        
        class MyLocust(Locust):
            host = ""
            task_set = RootTaskSet
        
        l = MyLocust()
        l.run()
        self.assertTrue(isinstance(parents["sub"], RootTaskSet))
        self.assertTrue(isinstance(parents["subsub"], SubTaskSet))
    

class TestWebLocustClass(WebserverTestCase):
    def test_get_request(self):
        self.response = ""
        def t1(l):
            self.response = l.client.get("/ultra_fast")
        class MyLocust(HttpLocust):
            tasks = [t1]
            host = "http://127.0.0.1:%i" % self.port

        my_locust = MyLocust()
        t1(my_locust)
        self.assertEqual(self.response.text, "This is an ultra fast response")

    def test_client_request_headers(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("hello", locust.client.get("/request_header_test", headers={"X-Header-Test":"hello"}).text)

    def test_client_get(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("GET", locust.client.get("/request_method").text)
    
    def test_client_get_absolute_url(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("GET", locust.client.get("http://127.0.0.1:%i/request_method" % self.port).text)

    def test_client_post(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("POST", locust.client.post("/request_method", {"arg":"hello world"}).text)
        self.assertEqual("hello world", locust.client.post("/post", {"arg":"hello world"}).text)

    def test_client_put(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("PUT", locust.client.put("/request_method", {"arg":"hello world"}).text)
        self.assertEqual("hello world", locust.client.put("/put", {"arg":"hello world"}).text)

    def test_client_delete(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual("DELETE", locust.client.delete("/request_method").text)
        self.assertEqual(200, locust.client.delete("/request_method").status_code)

    def test_client_head(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        locust = MyLocust()
        self.assertEqual(200, locust.client.head("/request_method").status_code)

    def test_client_basic_auth(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        class MyAuthorizedLocust(HttpLocust):
            host = "http://locust:menace@127.0.0.1:%i" % self.port

        class MyUnauthorizedLocust(HttpLocust):
            host = "http://locust:wrong@127.0.0.1:%i" % self.port

        locust = MyLocust()
        unauthorized = MyUnauthorizedLocust()
        authorized = MyAuthorizedLocust()
        response = authorized.client.get("/basic_auth")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Authorized", response.text)
        self.assertEqual(401, locust.client.get("/basic_auth").status_code)
        self.assertEqual(401, unauthorized.client.get("/basic_auth").status_code)
    
    def test_log_request_name_argument(self):
        from locust.stats import global_stats
        self.response = ""
        
        class MyLocust(HttpLocust):
            tasks = []
            host = "http://127.0.0.1:%i" % self.port
            
            @task()
            def t1(l):
                self.response = l.client.get("/ultra_fast", name="new name!")

        my_locust = MyLocust()
        my_locust.t1()
        
        self.assertEqual(1, global_stats.get("new name!", "GET").num_requests)
        self.assertEqual(0, global_stats.get("/ultra_fast", "GET").num_requests)
    
    def test_locust_client_error(self):
        class MyTaskSet(TaskSet):
            @task
            def t1(self):
                self.client.get("/")
                self.interrupt()
        
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port
            task_set = MyTaskSet
        
        my_locust = MyLocust()
        self.assertRaises(LocustError, lambda: my_locust.client.get("/"))
        my_taskset = MyTaskSet(my_locust)
        self.assertRaises(LocustError, lambda: my_taskset.client.get("/"))
    
    def test_redirect_url_original_path_as_name(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        l = MyLocust()
        l.client.get("/redirect")
        
        from locust.stats import global_stats
        self.assertEqual(1, len(global_stats.entries))
        self.assertEqual(1, global_stats.get("/redirect", "GET").num_requests)
        self.assertEqual(0, global_stats.get("/ultra_fast", "GET").num_requests)


class TestCatchResponse(WebserverTestCase):
    def setUp(self):
        super(TestCatchResponse, self).setUp()
        
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port

        self.locust = MyLocust()
        
        self.num_failures = 0
        self.num_success = 0
        def on_failure(request_type, name, response_time, exception):
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
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
            task_set = MyTaskSet
        
        l = MyLocust()
        ts = MyTaskSet(l)
        self.assertRaises(InterruptTaskSet, lambda: ts.interrupted_task())
        self.assertEqual(0, self.num_failures)
        self.assertEqual(0, self.num_success)
    
    def test_catch_response_connection_error_success(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:1"
        l = MyLocust()
        with l.client.get("/", catch_response=True) as r:
            self.assertEqual(r.status_code, 0)
            self.assertEqual(None, r.content)
            r.success()
        self.assertEqual(1, self.num_success)
        self.assertEqual(0, self.num_failures)
    
    def test_catch_response_connection_error_fail(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:1"
        l = MyLocust()
        with l.client.get("/", catch_response=True) as r:
            self.assertEqual(r.status_code, 0)
            self.assertEqual(None, r.content)
            r.success()
        self.assertEqual(1, self.num_success)
        self.assertEqual(0, self.num_failures)
