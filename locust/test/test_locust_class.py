import six

from locust import InterruptTaskSet, ResponseError
from locust.core import WebLocust, Locust, TaskSet, events, task, mod_context
from locust.exception import (CatchResponseError, LocustError, RescheduleTask,
                              RescheduleTaskImmediately)
from locust import config

from .testcases import LocustTestCase, WebserverTestCase


class TestTaskSet(LocustTestCase):
    def setUp(self):
        super(TestTaskSet, self).setUp()

        class User(WebLocust):
            pass

        self.locust = User(config.locust_config())

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
        loc.schedule_task(MySubTaskSet, args=[1, 2, 3], kwargs={"hello": "world"})
        self.assertRaises(RescheduleTaskImmediately, lambda: loc.execute_next_task())
        self.assertEqual((1, 2, 3), self.locust.sub_taskset_args)
        self.assertEqual({"hello": "world"}, self.locust.sub_taskset_kwargs)

    def test_interrupt_taskset_in_main_taskset(self):
        class MyTaskSet(TaskSet):
            @task
            def interrupted_task(self):
                raise InterruptTaskSet(reschedule=False)

        class MyLocust(Locust):
            task_set = MyTaskSet

        class MyTaskSet2(TaskSet):
            @task
            def interrupted_task(self):
                self.interrupt()

        class MyLocust2(Locust):
            task_set = MyTaskSet2

        l = MyLocust(config.locust_config())
        l2 = MyLocust2(config.locust_config())
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
            task_set = SubTaskSet

        l = MyLocust(config.locust_config())
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
            task_set = RootTaskSet

        l = MyLocust(config.locust_config())
        l.run()
        self.assertTrue(isinstance(parents["sub"], RootTaskSet))
        self.assertTrue(isinstance(parents["subsub"], SubTaskSet))

    def tast_on_task_start_hook(self):
        class MyTasks(TaskSet):
            t1_executed = False
            t2_executed = False

            def on_task_start(self):
               self.t1_executed = True

            @task
            def t2(self):
                self.t2_executed = True
                raise InterruptTaskSet(reschedule=False)

        l = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: l.run())
        self.assertTrue(l.t1_executed)
        self.assertTrue(l.t2_executed)

    def tast_on_task_end_hook(self):
        class MyTasks(TaskSet):
            t1_executed = False
            t2_executed = False

            def on_task_start(self):
                self.t1_executed = True

            @task
            def t2(self):
                self.t2_executed = True
                raise InterruptTaskSet(reschedule=False)

        l = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: l.run())
        self.assertTrue(l.t1_executed)
        self.assertTrue(l.t2_executed)


class TestWebLocustClass(WebserverTestCase):
    def setUp(self):
        super(TestWebLocustClass, self).setUp()
        class MyLocust(WebLocust):
            pass
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': self.port})
        self.locust = MyLocust(options)

    def test_get_request(self):
        self.response = ""
        def t1(l):
            self.response = l.client.http.get("/ultra_fast")
        class MyLocust(WebLocust):
            tasks = [t1]

        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': self.port})
        my_locust = MyLocust(options)
        t1(my_locust)
        self.assertEqual(self.response.text, "This is an ultra fast response")

    def test_client_request_headers(self):
        self.assertEqual(
            "hello",
            self.locust.client.http.get(
                "/request_header_test",
                headers={"X-Header-Test":"hello"}
            ).text
        )

    def test_client_get(self):
        self.assertEqual("GET", self.locust.client.http.get("/request_method").text)
    
    def test_client_get_absolute_url(self):
        self.assertEqual(
            "GET",
            self.locust.client.http.get("http://127.0.0.1:%i/request_method" % self.port).text
        )

    def test_client_post(self):
        self.assertEqual(
            "POST",
            self.locust.client.http.post("/request_method", {"arg": "hello world"}).text
        )
        self.assertEqual(
            "hello world",
            self.locust.client.http.post("/post", {"arg": "hello world"}).text
        )

    def test_client_put(self):
        self.assertEqual(
            "PUT",
            self.locust.client.http.put("/request_method", {"arg": "hello world"}).text
        )
        self.assertEqual(
            "hello world",
            self.locust.client.http.put("/put", {"arg": "hello world"}).text
        )

    def test_client_delete(self):
        self.assertEqual("DELETE", self.locust.client.http.delete("/request_method").text)
        self.assertEqual(200, self.locust.client.http.delete("/request_method").status_code)

    def test_client_head(self):
        self.assertEqual(200, self.locust.client.http.head("/request_method").status_code)

    def test_client_basic_auth(self):
        auth_options = config.LocustConfig()
        auth_options.update_config({'host': 'locust:menace@127.0.0.1', 'port': self.port})
        class MyAuthorizedLocust(WebLocust):
            pass

        unauth_options = config.LocustConfig()
        unauth_options.update_config({'host': 'locust:wrong@127.0.0.1', 'port': self.port})
        class MyUnauthorizedLocust(WebLocust):
            pass
        
        unauthorized = MyUnauthorizedLocust(unauth_options)
        authorized = MyAuthorizedLocust(auth_options)
        response = authorized.client.http.get("/basic_auth")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Authorized", response.text)
        with self.locust.client.http.get("/basic_auth", catch_response=True) as response:
            response.success()
            self.assertEqual(401, response.status_code)
        with unauthorized.client.http.get("/basic_auth", catch_response=True) as response:
            response.success()
            self.assertEqual(401, response.status_code)       
    
    def test_log_request_name_argument(self):
        from locust.stats import global_stats
        self.response = ""
        
        class MyLocust(WebLocust):
            tasks = []
            pass
            
            @task()
            def t1(l):
                self.response = l.client.http.get("/ultra_fast", name="new name!")

        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': self.port})
        my_locust = MyLocust(options)
        my_locust.t1()
        
        self.assertEqual(1, global_stats.get(None, "new name!", "GET").num_requests)
        self.assertEqual(0, global_stats.get(None, "/ultra_fast", "GET").num_requests)
    
    def test_locust_client_error(self):
        class MyTaskSet(TaskSet):
            @task
            def t1(self):
                self.client.http.get("/")
                self.interrupt()

        class MyLocust(WebLocust):
            task_set = MyTaskSet

        my_locust = MyLocust(config.locust_config())
        self.assertRaises(RescheduleTask, lambda: my_locust.client.http.get("/"))
        my_taskset = MyTaskSet(my_locust)
        self.assertRaises(RescheduleTask, lambda: my_taskset.client.http.get("/"))

    def test_redirect_url_original_path_as_name(self):
        self.locust.client.http.get("/redirect")

        from locust.stats import global_stats
        self.assertEqual(2, len(global_stats.entries))
        self.assertEqual(1, global_stats.get(None, "/redirect", "GET").num_requests)
        self.assertEqual(0, global_stats.get(None, "/ultra_fast", "GET").num_requests)


class TestCatchResponse(WebserverTestCase):
    def setUp(self):
        super(TestCatchResponse, self).setUp()
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': self.port})

        class MyLocust(WebLocust):
            pass

        self.locust = MyLocust(options)
        
        self.num_failures = 0
        self.num_success = 0
        def on_failure(request_type, name, response_time, exception, task):
            self.num_failures += 1
            self.last_failure_exception = exception
        def on_success(**kwargs):
            self.num_success += 1
        events.request_failure += on_failure
        events.request_success += on_success
        
    def test_catch_response(self):
        try:
            self.assertEqual(500, self.locust.client.http.get("/fail").status_code)
        except RescheduleTask:
            pass
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)
        
        with self.locust.client.http.get("/ultra_fast", catch_response=True) as response: pass
        self.assertEqual(1, self.num_failures)
        self.assertEqual(1, self.num_success)
        try:
            with self.locust.client.http.get("/ultra_fast", catch_response=True) as response:
                raise ResponseError("Not working")
        except RescheduleTask:
            pass
        self.assertEqual(2, self.num_failures)
        self.assertEqual(1, self.num_success)
    
    def test_catch_response_http_fail(self):
        try:
            with self.locust.client.http.get("/fail", catch_response=True) as response: pass
        except RescheduleTask:
            pass
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)
    
    def test_catch_response_http_manual_fail(self):
        try:
            with self.locust.client.http.get("/ultra_fast", catch_response=True) as response:
                response.failure("Haha!")
        except RescheduleTask:
            pass
        self.assertEqual(1, self.num_failures)
        self.assertEqual(0, self.num_success)
        self.assertTrue(
            isinstance(self.last_failure_exception, CatchResponseError),
            "Failure event handler should have been passed a CatchResponseError instance"
        )
    
    def test_catch_response_http_manual_success(self):
        with self.locust.client.http.get("/fail", catch_response=True) as response:
            response.success()
        self.assertEqual(0, self.num_failures)
        self.assertEqual(1, self.num_success)
    
    def test_catch_response_allow_404(self):
        with self.locust.client.http.get("/does/not/exist", catch_response=True) as response:
            self.assertEqual(404, response.status_code)
            if response.status_code == 404:
                response.success()
        self.assertEqual(0, self.num_failures)
        self.assertEqual(1, self.num_success)
    
    def test_interrupt_taskset_with_catch_response(self):
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': '1'})
        class MyTaskSet(TaskSet):
            @task
            def interrupted_task(self):
                with self.client.http.get("/ultra_fast", catch_response=True) as r:
                    raise InterruptTaskSet()
        class MyLocust(WebLocust):
            task_set = MyTaskSet
        
        l = MyLocust(options)
        ts = MyTaskSet(l)
        self.assertRaises(InterruptTaskSet, lambda: ts.interrupted_task())
        self.assertEqual(0, self.num_failures)
        self.assertEqual(0, self.num_success)
    
    def test_catch_response_connection_error_success(self):
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': '1'})
        class MyLocust(WebLocust):
            pass
        l = MyLocust(options)
        with l.client.http.get("/", catch_response=True) as r:
            self.assertEqual(r.status_code, 0)
            self.assertEqual(None, r.content)
            r.success()
        self.assertEqual(1, self.num_success)
        self.assertEqual(0, self.num_failures)

    def test_catch_response_connection_error_fail(self):
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': '1'})

        class MyLocust(WebLocust):
            pass

        l = MyLocust(options)
        with l.client.http.get("/", catch_response=True) as r:
            self.assertEqual(r.status_code, 0)
            self.assertEqual(None, r.content)
            r.success()
        self.assertEqual(1, self.num_success)
        self.assertEqual(0, self.num_failures)


class TestContext(LocustTestCase):

    def setUp(self):
        super(TestContext, self).setUp()
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': '1'})

        class User(WebLocust):
            pass
        self.locust = User(options)
    
    def test_access(self):
        test = self
        class MyTasks(TaskSet):
            
            def on_start(self):
                test.assertTrue(self.context['any_1'] == None)

            def on_task_start(self):
                test.assertTrue(self.context['any_2'] == None)

            def on_task_end(self):
                test.assertTrue(self.context['any_3'] == None)

            @task
            def t1(self):
                test.assertTrue(self.context['any_4'] == None)
                raise InterruptTaskSet(reschedule=False)

        l = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: l.run())

    def test_context_modification(self):
        test = self
        class MyTasks(TaskSet):
            
            def on_start(self):
                self.context['any'] = 1

            def on_task_start(self):
                test.assertTrue(self.context['any'] == 1)
                self.context['any'] += 1

            def on_task_end(self):
                test.assertTrue(self.context['any'] == 3)

            @task
            def t1(self):
                test.assertTrue(self.context['any'] == 2)
                self.context['any'] += 1
                raise InterruptTaskSet(reschedule=False)

        l = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: l.run())

    def test_context_revert(self):
        test = self
        class MyTasks(TaskSet):
            completed = 0
            def on_start(self):
                self.context['default'] = 1

            def on_task_start(self):
                test.assertTrue(self.context['default'] == 1)
                self.context['default'] += 1

            def on_task_end(self):
                test.assertTrue(self.context['default'] == 3)

            @task
            def t1(self):
                test.assertTrue(self.context['default'] == 2)
                self.context['default'] += 1
                self.completed += 1
                if self.completed >= 2:
                    raise InterruptTaskSet(reschedule=False)

        loc = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: loc.run())

    def test_context_mod_decorator(self):
        test = self
        class MyTasks(TaskSet):
            completed = 0
            def on_start(self):
                self.context['default'] = 1

            @task
            @mod_context('default', 10)
            def t1(self):
                test.assertTrue(self.context['default'] == 10)
                raise InterruptTaskSet(reschedule=False)

        loc = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: loc.run())
