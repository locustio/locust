import time
import unittest

from locust.core import HttpLocust, TaskSet, task
from locust.inspectlocust import get_task_ratio_dict
from locust.rpc.protocol import Message
from locust.stats import CachedResponseTimes, RequestStats, StatsEntry, diff_response_time_dicts, global_stats
from six.moves import xrange

from .testcases import WebserverTestCase


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

        assert s.get_response_time_percentile(0.5) == 50
        assert s.get_response_time_percentile(0.6) == 60
        assert s.get_response_time_percentile(0.95) == 95

    def test_median(self):
        assert self.s.median_response_time == 79

    def test_total_rps(self):
        assert self.s.total_rps == 7

    def test_current_rps(self):
        self.stats.total.last_request_timestamp = int(time.time()) + 4
        assert self.s.current_rps == 3.5

        self.stats.total.last_request_timestamp = int(time.time()) + 25
        assert self.s.current_rps == 0

    def test_num_reqs_fails(self):
        assert self.s.num_requests == 7
        assert self.s.num_failures == 3

    def test_avg(self):
        assert self.s.avg_response_time == 187.71428571428572

    def test_reset(self):
        self.s.reset()
        self.s.log(756, 0)
        self.s.log_error(Exception("dummy fail after reset"))
        self.s.log(85, 0)

        assert self.s.total_rps == 2
        assert self.s.num_requests == 2
        assert self.s.num_failures == 1
        assert self.s.avg_response_time == 420.5
        assert self.s.median_response_time == 85
    
    def test_reset_min_response_time(self):
        self.s.reset()
        self.s.log(756, 0)
        assert 756 == self.s.min_response_time

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
        s.extend(s1)
        s.extend(s2)

        assert s.num_requests == 10
        assert s.num_failures == 3
        assert s.median_response_time == 38
        assert s.avg_response_time == 43.2

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

        assert s1.num_requests == 8
        assert s1.median_response_time == 550
        assert s1.avg_response_time == 535.75
        assert s1.min_response_time == 122
        assert s1.max_response_time == 992

    def test_percentile_rounded_down(self):
        s1 = StatsEntry(self.stats, "rounding down!", "GET")
        s1.log(122, 0)    # (rounded 120) min
        actual_percentile = s1.percentile()
        assert actual_percentile == " GET rounding down!                                                  1    120    120    120    120    120    120    120    120    120"

    def test_percentile_rounded_up(self):
        s2 = StatsEntry(self.stats, "rounding up!", "GET")
        s2.log(127, 0)    # (rounded 130) min
        actual_percentile = s2.percentile()
        assert actual_percentile == " GET rounding up!                                                    1    130    130    130    130    130    130    130    130    130"
    
    def test_error_grouping(self):
        # reset stats
        self.stats = RequestStats()
        
        self.stats.log_error("GET", "/some-path", Exception("Exception!"))
        self.stats.log_error("GET", "/some-path", Exception("Exception!"))
            
        assert 1 == len(self.stats.errors)
        assert 2 == list(self.stats.errors.values())[0].occurences
        
        self.stats.log_error("GET", "/some-path", Exception("Another exception!"))
        self.stats.log_error("GET", "/some-path", Exception("Another exception!"))
        self.stats.log_error("GET", "/some-path", Exception("Third exception!"))
        assert 3 == len(self.stats.errors)
    
    def test_error_grouping_errors_with_memory_addresses(self):
        # reset stats
        self.stats = RequestStats()
        class Dummy(object):
            pass
        
        self.stats.log_error("GET", "/", Exception("Error caused by %r" % Dummy()))
        assert 1 == len(self.stats.errors)
    
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
        
        assert 20 == u1.median_response_time
    
    
class TestStatsEntryResponseTimesCache(unittest.TestCase):
    def setUp(self, *args, **kwargs):
        super(TestStatsEntryResponseTimesCache, self).setUp(*args, **kwargs)
        self.stats = RequestStats()
    
    def test_response_times_cached(self):
        s = StatsEntry(self.stats, "/", "GET", use_response_times_cache=True)
        assert 1 == len(s.response_times_cache)
        s.log(11, 1337)
        assert 1 == len(s.response_times_cache)
        s.last_request_timestamp -= 1
        s.log(666, 1337)
        assert 2 == len(s.response_times_cache)
        assert CachedResponseTimes(
            response_times={11:1}, 
            num_requests=1,
        ) == s.response_times_cache[s.last_request_timestamp-1]
    
    def test_response_times_not_cached_if_not_enabled(self):
        s = StatsEntry(self.stats, "/", "GET")
        s.log(11, 1337)
        assert None == s.response_times_cache
        s.last_request_timestamp -= 1
        s.log(666, 1337)
        assert None == s.response_times_cache
    
    def test_latest_total_response_times_pruned(self):
        """
        Check that RequestStats.latest_total_response_times are pruned when execeeding 20 entries
        """
        s = StatsEntry(self.stats, "/", "GET", use_response_times_cache=True)
        t = int(time.time())
        for i in reversed(range(2, 30)):
            s.response_times_cache[t-i] = CachedResponseTimes(response_times={}, num_requests=0)
        assert 29 == len(s.response_times_cache)
        s.log(17, 1337)
        s.last_request_timestamp -= 1
        s.log(1, 1)
        assert 20 == len(s.response_times_cache)
        assert (
            CachedResponseTimes(response_times={17:1}, num_requests=1)) == (
            s.response_times_cache.popitem(last=True)[1]), (
        )
    
    def test_get_current_response_time_percentile(self):
        s = StatsEntry(self.stats, "/", "GET", use_response_times_cache=True)
        t = int(time.time())
        s.response_times_cache[t-10] = CachedResponseTimes(
            response_times={i:1 for i in xrange(100)},
            num_requests=200
        )
        s.response_times_cache[t-10].response_times[1] = 201
        
        s.response_times = {i:2 for i in xrange(100)}
        s.response_times[1] = 202
        s.num_requests = 300
        
        assert 95 == s.get_current_response_time_percentile(0.95)
    
    def test_diff_response_times_dicts(self):
        assert {1:5, 6:8} == diff_response_time_dicts(
            {1:6, 6:16, 2:2}, 
            {1:1, 6:8, 2:2},
        )
        assert {} == diff_response_time_dicts(
            {}, 
            {},
        )
        assert {10:15} == diff_response_time_dicts(
            {10:15}, 
            {},
        )
        assert {10:10} == diff_response_time_dicts(
            {10:10}, 
            {},
        )
        assert {} == diff_response_time_dicts(
            {1:1}, 
            {1:1},
        )


class TestRequestStatsWithWebserver(WebserverTestCase):
    def test_request_stats_content_length(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast")
        assert global_stats.get("/ultra_fast", "GET").avg_content_length == len("This is an ultra fast response")
        locust.client.get("/ultra_fast")
        assert global_stats.get("/ultra_fast", "GET").avg_content_length == len("This is an ultra fast response")
    
    def test_request_stats_no_content_length(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
        l = MyLocust()
        path = "/no_content_length"
        r = l.client.get(path)
        assert global_stats.get(path, "GET").avg_content_length == len("This response does not have content-length in the header")
    
    def test_request_stats_no_content_length_streaming(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
        l = MyLocust()
        path = "/no_content_length"
        r = l.client.get(path, stream=True)
        assert 0 == global_stats.get(path, "GET").avg_content_length
    
    def test_request_stats_named_endpoint(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast", name="my_custom_name")
        assert 1 == global_stats.get("my_custom_name", "GET").num_requests
    
    def test_request_stats_query_variables(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.get("/ultra_fast?query=1")
        assert 1 == global_stats.get("/ultra_fast?query=1", "GET").num_requests
    
    def test_request_stats_put(self):
        class MyLocust(HttpLocust):
            host = "http://127.0.0.1:%i" % self.port
    
        locust = MyLocust()
        locust.client.put("/put")
        assert 1 == global_stats.get("/put", "PUT").num_requests
    
    def test_request_connection_error(self):
        class MyLocust(HttpLocust):
            host = "http://localhost:1"
        
        locust = MyLocust()
        response = locust.client.get("/", timeout=0.1)
        assert response.status_code == 0
        assert 1 == global_stats.get("/", "GET").num_failures
        assert 0 == global_stats.get("/", "GET").num_requests


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
        assert 1.0 == ratio["MyTaskSet"]["ratio"]
        assert 0.75 == ratio["MyTaskSet"]["tasks"]["root_task"]["ratio"]
        assert 0.25 == ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["ratio"]
        assert 0.5 == ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task1"]["ratio"]
        assert 0.5 == ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task2"]["ratio"]
    
    def test_get_task_ratio_dict_total(self):
        ratio = get_task_ratio_dict([MyTaskSet], total=True)
        assert 1.0 == ratio["MyTaskSet"]["ratio"]
        assert 0.75 == ratio["MyTaskSet"]["tasks"]["root_task"]["ratio"]
        assert 0.25 == ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["ratio"]
        assert 0.125 == ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task1"]["ratio"]
        assert 0.125 == ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task2"]["ratio"]
