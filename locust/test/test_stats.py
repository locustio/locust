import time
import unittest
from six.moves import xrange

from locust.core import WebLocust, TaskSet, task
from locust.inspectlocust import get_task_ratio_dict
from locust.rpc.protocol import Message
from locust.stats import RequestStats, StatsEntry, global_stats
from locust.exception import RescheduleTask, InterruptTaskSet
from locust import config
from .testcases import WebserverTestCase


class TestRequestStats(unittest.TestCase):
    def setUp(self):
        self.stats = RequestStats()
        self.stats.start_time = time.time()
        self.s = StatsEntry(self.stats, "task", "test_entry", "GET")
        self.s.log(45, 0)
        self.s.log(135, 0)
        self.s.log(44, 0)
        self.s.log_error(Exception("dummy fail"))
        self.s.log_error(Exception("dummy fail"))
        self.s.log(375, 0)
        self.s.log(601, 0)
        self.s.log(35, 0)
        self.s.log(79, 0)
        self.s.log_error(Exception("dummy fail"))

    def test_percentile(self):
        s = StatsEntry(self.stats, "task", "percentile_test", "GET")
        for x in xrange(100):
            s.log(x, 0)

        self.assertEqual(s.get_response_time_percentile(0.5), 50)
        self.assertEqual(s.get_response_time_percentile(0.6), 60)
        self.assertEqual(s.get_response_time_percentile(0.95), 95)

    def test_median(self):
        self.assertEqual(self.s.median_response_time, 79)

    def test_total_rps(self):
        self.assertEqual(self.s.total_rps, 7)

    def test_current_rps(self):
        self.stats.last_request_timestamp = int(time.time()) + 4
        self.assertEqual(self.s.current_rps, 3.5)

        self.stats.last_request_timestamp = int(time.time()) + 25
        self.assertEqual(self.s.current_rps, 0)

    def test_num_reqs_fails(self):
        self.assertEqual(self.s.num_requests, 7)
        self.assertEqual(self.s.num_failures, 3)

    def test_avg(self):
        self.assertEqual(self.s.avg_response_time, 187.71428571428571428571428571429)

    def test_reset(self):
        self.s.reset()
        self.s.log(756, 0)
        self.s.log_error(Exception("dummy fail after reset"))
        self.s.log(85, 0)

        self.assertEqual(self.s.total_rps, 2)
        self.assertEqual(self.s.num_requests, 2)
        self.assertEqual(self.s.num_failures, 1)
        self.assertEqual(self.s.avg_response_time, 420.5)
        self.assertEqual(self.s.median_response_time, 85)
    
    def test_reset_min_response_time(self):
        self.s.reset()
        self.s.log(756, 0)
        self.assertEqual(756, self.s.min_response_time)

    def test_aggregation(self):
        s1 = StatsEntry(self.stats, "test", "aggregate me!", "GET")
        s1.log(12, 0)
        s1.log(12, 0)
        s1.log(38, 0)
        s1.log_error("Dummy exzeption")

        s2 = StatsEntry(self.stats, "test", "aggregate me!", "GET")
        s2.log_error("Dummy exzeption")
        s2.log_error("Dummy exzeption")
        s2.log(12, 0)
        s2.log(99, 0)
        s2.log(14, 0)
        s2.log(55, 0)
        s2.log(38, 0)
        s2.log(55, 0)
        s2.log(97, 0)

        s = StatsEntry(self.stats, "test", "GET", "")
        s.extend(s1, full_request_history=True)
        s.extend(s2, full_request_history=True)

        self.assertEqual(s.num_requests, 10)
        self.assertEqual(s.num_failures, 3)
        self.assertEqual(s.median_response_time, 38)
        self.assertEqual(s.avg_response_time, 43.2)
    
    def test_error_grouping(self):
        # reset stats
        self.stats = RequestStats()
        
        s = StatsEntry(self.stats, "test", "/some-path", "GET")
        s.log_error(Exception("Exception!"))
        s.log_error(Exception("Exception!"))
            
        self.assertEqual(1, len(self.stats.errors))
        self.assertEqual(2, list(self.stats.errors.values())[0].occurences)
        
        s.log_error(Exception("Another exception!"))
        s.log_error(Exception("Another exception!"))
        s.log_error(Exception("Third exception!"))
        self.assertEqual(3, len(self.stats.errors))
    
    def test_error_grouping_errors_with_memory_addresses(self):
        # reset stats
        self.stats = RequestStats()
        class Dummy(object):
            pass
        
        s = StatsEntry(self.stats, "test", "/", "GET")
        s.log_error(Exception("Error caused by %r" % Dummy()))
        s.log_error(Exception("Error caused by %r" % Dummy()))
        
        self.assertEqual(1, len(self.stats.errors))
    
    def test_serialize_through_message(self):
        """
        Serialize a RequestStats instance, then serialize it through a Message, 
        and unserialize the whole thing again. This is done "IRL" when stats are sent 
        from slaves to master.
        """
        s1 = StatsEntry(self.stats, "test", "test", "GET")
        s1.log(10, 0)
        s1.log(20, 0)
        s1.log(40, 0)
        u1 = StatsEntry.unserialize(s1.serialize())
        
        data = Message.unserialize(Message("dummy", s1.serialize(), "none").serialize()).data
        u1 = StatsEntry.unserialize(data)
        
        self.assertEqual(20, u1.median_response_time)


class TestRequestStatsWithWebserver(WebserverTestCase):
    def setUp(self):
        super(TestRequestStatsWithWebserver, self).setUp()
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': self.port})

        class MyLocust(WebLocust):
            pass
        self.locust = MyLocust(options)
    
    def test_request_stats_content_length(self):

    
        self.locust.client.http.get("/ultra_fast")
        self.assertEqual(global_stats.get(None, "/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response"))
        self.locust.client.http.get("/ultra_fast")
        self.assertEqual(global_stats.get(None, "/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response"))
    
    def test_request_stats_no_content_length(self):
        path = "/no_content_length"
        r = self.locust.client.http.get(path)
        self.assertEqual(global_stats.get(None, path, "GET").avg_content_length, len("This response does not have content-length in the header"))
    
    def test_request_stats_no_content_length_streaming(self):
        path = "/no_content_length"
        r = self.locust.client.http.get(path, stream=True)
        self.assertEqual(0, global_stats.get(None, path, "GET").avg_content_length)
    
    def test_request_stats_named_endpoint(self):
        self.locust.client.http.get("/ultra_fast", name="my_custom_name")
        self.assertEqual(1, global_stats.get(None, "my_custom_name", "GET").num_requests)
    
    def test_request_stats_query_variables(self):
        self.locust.client.http.get("/ultra_fast?query=1")
        self.assertEqual(1, global_stats.get(None, "/ultra_fast?query=1", "GET").num_requests)
    
    def test_request_stats_put(self):
        self.locust.client.http.put("/put")
        self.assertEqual(1, global_stats.get(None, "/put", "PUT").num_requests)
    
    def test_request_connection_error(self):
        try:
            response = self.locust.client.http.get("/", timeout=0.1)
        except RescheduleTask:
            pass
        self.assertEqual(1, global_stats.get(None, "/", "GET").num_failures)
        self.assertEqual(0, global_stats.get(None, "/", "GET").num_requests)
    
    def test_max_requests(self):
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': self.port})
        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                self.client.http.get("/ultra_fast")
        class MyLocust(WebLocust):
            task_set = MyTaskSet
            min_wait = 1
            max_wait = 1
            
        try:
            from locust.exception import StopLocust
            global_stats.clear_all()
            global_stats.max_requests = 2
            
            l = MyLocust(options)
            self.assertRaises(StopLocust, lambda: l.task_set(l).run())
            self.assertEqual(2, global_stats.num_requests)
            
            global_stats.clear_all()
            global_stats.max_requests = 2
            self.assertEqual(0, global_stats.num_requests)
            
            l.run()
            self.assertEqual(2, global_stats.num_requests)
        finally:
            global_stats.clear_all()
            global_stats.max_requests = None
    
    def test_max_requests_failed_requests(self):
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1', 'port': self.port})
        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                self.client.http.get("/ultra_fast")
                self.client.http.get("/fail")
                self.client.http.get("/fail")
            
        class MyLocust(WebLocust):
            task_set = MyTaskSet
            min_wait = 1
            max_wait = 1
            
        try:
            from locust.exception import StopLocust
            global_stats.clear_all()
            global_stats.max_requests = 3
            
            l = MyLocust(options)
            self.assertRaises(StopLocust, lambda: l.task_set(l).run())
            self.assertEqual(2, global_stats.num_requests)
            self.assertEqual(1, global_stats.num_failures)

            global_stats.clear_all()
            global_stats.max_requests = 2
            self.assertEqual(0, global_stats.num_requests)
            self.assertEqual(0, global_stats.num_failures)
            l.run()
            self.assertEqual(1, global_stats.num_requests)
            self.assertEqual(1, global_stats.num_failures)
        finally:
            global_stats.clear_all()
            global_stats.max_requests = None


class MyTaskSet(TaskSet):
    @task(75)
    def root_task(self):
        pass
    
    @task(25)
    class MySubTaskSet(TaskSet):
        @task
        def task1(self):
            pass
        @task
        def task2(self):
            pass
    
class TestInspectLocust(unittest.TestCase):
    def test_get_task_ratio_dict_relative(self):
        ratio = get_task_ratio_dict([MyTaskSet])
        self.assertEqual(1.0, ratio["MyTaskSet"]["ratio"])
        self.assertEqual(0.75, ratio["MyTaskSet"]["tasks"]["root_task"]["ratio"])
        self.assertEqual(0.25, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["ratio"])
        self.assertEqual(0.5, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task1"]["ratio"])
        self.assertEqual(0.5, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task2"]["ratio"])
    
    def test_get_task_ratio_dict_total(self):
        ratio = get_task_ratio_dict([MyTaskSet], total=True)
        self.assertEqual(1.0, ratio["MyTaskSet"]["ratio"])
        self.assertEqual(0.75, ratio["MyTaskSet"]["tasks"]["root_task"]["ratio"])
        self.assertEqual(0.25, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["ratio"])
        self.assertEqual(0.125, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task1"]["ratio"])
        self.assertEqual(0.125, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task2"]["ratio"])

class TestLocustTaskStatistics(unittest.TestCase):

    def setUp(self):
        super(TestLocustTaskStatistics, self).setUp()
        options = config.LocustConfig()
        options.update_config({'host': '127.0.0.1'})
        class User(WebLocust):
            pass
        self.locust = User(options)
        global_stats.clear_all()

    def tearDown(self):
        global_stats.clear_all()

    def test_task_success(self):
        class MyTasks(TaskSet):
            def on_task_end(self):
                raise InterruptTaskSet(reschedule=False)

            @task
            def t1(self):
                pass
        loc = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: loc.run())
        self.assertEqual(len(global_stats.tasks), 1)
        self.assertEqual(global_stats.num_success_tasks, 1)

    def test_task_failure(self):
        class MyTasks(TaskSet):
            completed = False
            @task
            def t1(self):
                if not self.completed:
                    self.completed = True
                    raise RescheduleTask
                else:
                    raise InterruptTaskSet(reschedule=False)

        loc = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: loc.run())
        self.assertEqual(len(global_stats.tasks), 1)
        self.assertEqual(global_stats.num_success_tasks, 0)
        self.assertEqual(len(global_stats.tasks_failures), 1)
        self.assertEqual(global_stats.num_failed_tasks, 1)

    def test_task_requests_tracking_on_success(self):
        class MyTasks(TaskSet):
            def on_task_end(self):
                raise InterruptTaskSet(reschedule=False)

            @task
            def t1(self):
                self.client.http.get("/ultra_fast")
        loc = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: loc.run())

        self.assertIn(('Action Total', '/ultra_fast', 'GET'), global_stats.entries.keys())
        self.assertIn(('User::t1', '/ultra_fast', 'GET'), global_stats.entries.keys())

    def test_task_requests_tracking_on_failure(self):
        class MyTasks(TaskSet):
            def on_task_end(self):
                raise InterruptTaskSet(reschedule=False)

            @task
            def t1(self):
                self.client.http.post("/ultra_fast")
        loc = MyTasks(self.locust)
        self.assertRaises(RescheduleTask, lambda: loc.run())

        self.assertIn(('Action Total', '/ultra_fast', 'POST'), global_stats.entries.keys())
        self.assertIn(('User::t1', '/ultra_fast', 'POST'), global_stats.entries.keys())
        error_names = [f.task for f in global_stats.errors.values()]
        self.assertIn('Action Total', error_names)
        self.assertIn('User::t1', error_names)
