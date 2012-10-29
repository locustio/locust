import unittest
import time

from testcases import WebserverTestCase
from locust.stats import RequestStats
from locust.core import Locust, SubLocust, task
from locust.inspectlocust import get_task_ratio_dict

class TestRequestStats(unittest.TestCase):
    def setUp(self):
        RequestStats.global_start_time = time.time()
        self.s = RequestStats("GET", "test_entry")
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
        s = RequestStats("GET", "percentile_test")
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
        self.s.global_last_request_timestamp = int(time.time()) + 4
        self.assertEqual(self.s.current_rps, 3.5)

        self.s.global_last_request_timestamp = int(time.time()) + 25
        self.assertEqual(self.s.current_rps, 0)

    def test_num_reqs_fails(self):
        self.assertEqual(self.s.num_reqs, 7)
        self.assertEqual(self.s.num_failures, 3)

    def test_avg(self):
        self.assertEqual(self.s.avg_response_time, 187.71428571428571428571428571429)

    def test_reset(self):
        self.s.reset()
        self.s.log(756, 0)
        self.s.log_error(Exception("dummy fail after reset"))
        self.s.log(85, 0)

        self.assertEqual(self.s.total_rps, 2)
        self.assertEqual(self.s.num_reqs, 2)
        self.assertEqual(self.s.num_failures, 1)
        self.assertEqual(self.s.avg_response_time, 420.5)
        self.assertEqual(self.s.median_response_time, 85)

    def test_aggregation(self):
        s1 = RequestStats("GET", "aggregate me!")
        s1.log(12, 0)
        s1.log(12, 0)
        s1.log(38, 0)
        s1.log_error("Dummy exzeption")

        s2 = RequestStats("GET", "aggregate me!")
        s2.log_error("Dummy exzeption")
        s2.log_error("Dummy exzeption")
        s2.log(12, 0)
        s2.log(99, 0)
        s2.log(14, 0)
        s2.log(55, 0)
        s2.log(38, 0)
        s2.log(55, 0)
        s2.log(97, 0)

        s = RequestStats("GET", "")
        s.iadd_stats(s1, full_request_history=True)
        s.iadd_stats(s2, full_request_history=True)

        self.assertEqual(s.num_reqs, 10)
        self.assertEqual(s.num_failures, 3)
        self.assertEqual(s.median_response_time, 38)
        self.assertEqual(s.avg_response_time, 43.2)

class TestRequestStatsWithWebserver(WebserverTestCase):
    def test_request_stats_content_length(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast")
        self.assertEqual(RequestStats.get("GET", "/ultra_fast").avg_content_length, len("This is an ultra fast response"))
        locust.client.get("/ultra_fast")
        self.assertEqual(RequestStats.get("GET", "/ultra_fast").avg_content_length, len("This is an ultra fast response"))
    
    def test_request_stats_named_endpoint(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast", name="my_custom_name")
        self.assertEqual(1, RequestStats.get("GET", "my_custom_name").num_reqs)
    
    def test_request_stats_query_variables(self):
        class MyLocust(Locust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast?query=1")
        self.assertEqual(1, RequestStats.get("GET", "/ultra_fast?query=1").num_reqs)


class MyLocust(Locust):
    @task(75)
    def root_task(self):
        pass
    
    @task(25)
    class MySubLocust(SubLocust):
        @task
        def task1(self):
            pass
        @task
        def task2(self):
            pass
    
class TestInspectLocust(unittest.TestCase):
    def test_get_task_ratio_dict_relative(self):
        ratio = get_task_ratio_dict([MyLocust])
        self.assertEqual(1.0, ratio["MyLocust"]["ratio"])
        self.assertEqual(0.75, ratio["MyLocust"]["tasks"]["root_task"]["ratio"])
        self.assertEqual(0.25, ratio["MyLocust"]["tasks"]["MySubLocust"]["ratio"])
        self.assertEqual(0.5, ratio["MyLocust"]["tasks"]["MySubLocust"]["tasks"]["task1"]["ratio"])
        self.assertEqual(0.5, ratio["MyLocust"]["tasks"]["MySubLocust"]["tasks"]["task2"]["ratio"])
    
    def test_get_task_ratio_dict_total(self):
        ratio = get_task_ratio_dict([MyLocust], total=True)
        self.assertEqual(1.0, ratio["MyLocust"]["ratio"])
        self.assertEqual(0.75, ratio["MyLocust"]["tasks"]["root_task"]["ratio"])
        self.assertEqual(0.25, ratio["MyLocust"]["tasks"]["MySubLocust"]["ratio"])
        self.assertEqual(0.125, ratio["MyLocust"]["tasks"]["MySubLocust"]["tasks"]["task1"]["ratio"])
        self.assertEqual(0.125, ratio["MyLocust"]["tasks"]["MySubLocust"]["tasks"]["task2"]["ratio"])
        