import unittest
import time

from six.moves import xrange

from .testcases import WebserverTestCase
from locust.stats import RequestStats, StatsEntry, global_stats
from locust.core import HttpLocust, TaskSet, task
from locust.inspectlocust import get_task_ratio_dict
from locust.rpc.protocol import Message

class TestRequestStats(unittest.TestCase):
    def setUp(self):
        self.stats = RequestStats()
        self.stats.start_time = time.time()
        self.s = StatsEntry(self.stats, "test_entry", "GET")
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
        s = StatsEntry(self.stats, "percentile_test", "GET")
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
        self.assertEqual(self.s.avg_response_time, 189.0)

    def test_reset(self):
        self.s.reset()
        self.s.log(756, 0)
        self.s.log_error(Exception("dummy fail after reset"))
        self.s.log(85, 0)

        self.assertEqual(self.s.total_rps, 2)
        self.assertEqual(self.s.num_requests, 2)
        self.assertEqual(self.s.num_failures, 1)
        self.assertEqual(self.s.avg_response_time, 422.5)
        self.assertEqual(self.s.median_response_time, 85)
    
    def test_reset_min_response_time(self):
        self.s.reset()
        self.s.log(756, 0)
        self.assertEqual(760, self.s.min_response_time)

    def test_aggregation(self):
        s1 = StatsEntry(self.stats, "aggregate me!", "GET")
        s1.log(12, 0)
        s1.log(12, 0)
        s1.log(38, 0)
        s1.log_error("Dummy exzeption")

        s2 = StatsEntry(self.stats, "aggregate me!", "GET")
        s2.log_error("Dummy exzeption")
        s2.log_error("Dummy exzeption")
        s2.log(12, 0)
        s2.log(99, 0)
        s2.log(14, 0)
        s2.log(55, 0)
        s2.log(38, 0)
        s2.log(55, 0)
        s2.log(97, 0)

        s = StatsEntry(self.stats, "GET", "")
        s.extend(s1, full_request_history=True)
        s.extend(s2, full_request_history=True)

        self.assertEqual(s.num_requests, 10)
        self.assertEqual(s.num_failures, 3)
        self.assertEqual(s.median_response_time, 38)
        self.assertEqual(s.avg_response_time, 43.2)

    def test_aggregation_with_rounding(self):
        s1 = StatsEntry(self.stats, "round me!", "GET")
        s1.log(122, 0)    # (rounded 120) min
        s1.log(992, 0)    # (rounded 990) max
        s1.log(142, 0)    # (rounded 140)
        s1.log(552, 0)    # (rounded 550)
        s1.log(557, 0)    # (rounded 560)
        s1.log(387, 0)    # (rounded 390)
        s1.log(557, 0)    # (rounded 560)
        s1.log(977, 0)    # (rounded 980)

        self.assertEqual(s1.num_requests, 8)
        self.assertEqual(s1.median_response_time, 550)
        self.assertEqual(s1.avg_response_time, 536.25)
        self.assertEqual(s1.min_response_time, 120)
        self.assertEqual(s1.max_response_time, 990)

    def test_percentile_rounded(self):
        s1 = StatsEntry(self.stats, "rounding down!", "GET")
        s1.log(122, 0)    # (rounded 120) min
        actual_percentile = s1.percentile()
        self.assertEqual(actual_percentile, " GET rounding down!                                                  1    120    120    120    120    120    120    120    120    120")

        s2 = StatsEntry(self.stats, "rounding up!", "GET")
        s2.log(127, 0)    # (rounded 130) min
        actual_percentile = s2.percentile()
        self.assertEqual(actual_percentile, " GET rounding up!                                                    1    130    130    130    130    130    130    130    130    130")
    
    def test_error_grouping(self):
        # reset stats
        self.stats = RequestStats()
        
        s = StatsEntry(self.stats, "/some-path", "GET")
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
        
        s = StatsEntry(self.stats, "/", "GET")
        s.log_error(Exception("Error caused by %r" % Dummy()))
        s.log_error(Exception("Error caused by %r" % Dummy()))
        
        self.assertEqual(1, len(self.stats.errors))
    
    def test_serialize_through_message(self):
        """
        Serialize a RequestStats instance, then serialize it through a Message, 
        and unserialize the whole thing again. This is done "IRL" when stats are sent 
        from slaves to master.
        """
        s1 = StatsEntry(self.stats, "test", "GET")
        s1.log(10, 0)
        s1.log(20, 0)
        s1.log(40, 0)
        u1 = StatsEntry.unserialize(s1.serialize())
        
        data = Message.unserialize(Message("dummy", s1.serialize(), "none").serialize()).data
        u1 = StatsEntry.unserialize(data)
        
        self.assertEqual(20, u1.median_response_time)


class TestRequestStatsWithWebserver(WebserverTestCase):
    def test_request_stats_content_length(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast")
        self.assertEqual(global_stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response"))
        locust.client.get("/ultra_fast")
        self.assertEqual(global_stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response"))
    
    def test_request_stats_no_content_length(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
        l = MyLocust()
        path = "/no_content_length"
        r = l.client.get(path)
        self.assertEqual(global_stats.get(path, "GET").avg_content_length, len("This response does not have content-length in the header"))
    
    def test_request_stats_no_content_length_streaming(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
        l = MyLocust()
        path = "/no_content_length"
        r = l.client.get(path, stream=True)
        self.assertEqual(0, global_stats.get(path, "GET").avg_content_length)
    
    def test_request_stats_named_endpoint(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast", name="my_custom_name")
        self.assertEqual(1, global_stats.get("my_custom_name", "GET").num_requests)
    
    def test_request_stats_query_variables(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast?query=1")
        self.assertEqual(1, global_stats.get("/ultra_fast?query=1", "GET").num_requests)
    
    def test_request_stats_put(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.put("/put")
        self.assertEqual(1, global_stats.get("/put", "PUT").num_requests)
    
    def test_request_connection_error(self):
        class MyLocust(HttpLocust):
            host = "http://localhost:1"
        
        locust = MyLocust()
        response = locust.client.get("/", timeout=0.1)
        self.assertEqual(response.status_code, 0)
        self.assertEqual(1, global_stats.get("/", "GET").num_failures)
        self.assertEqual(0, global_stats.get("/", "GET").num_requests)
    
    def test_max_requests(self):
        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                self.client.get("/ultra_fast")
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
            task_set = MyTaskSet
            min_wait = 1
            max_wait = 1
            
        try:
            from locust.exception import StopLocust
            global_stats.clear_all()
            global_stats.max_requests = 2
            
            l = MyLocust()
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
        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                self.client.get("/ultra_fast")
                self.client.get("/fail")
                self.client.get("/fail")
            
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
            task_set = MyTaskSet
            min_wait = 1
            max_wait = 1
            
        try:
            from locust.exception import StopLocust
            global_stats.clear_all()
            global_stats.max_requests = 3
            
            l = MyLocust()
            self.assertRaises(StopLocust, lambda: l.task_set(l).run())
            self.assertEqual(1, global_stats.num_requests)
            self.assertEqual(2, global_stats.num_failures)
            
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
