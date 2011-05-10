import sys
import time
import gevent
from copy import copy
import math
import functools

from exception import InterruptLocust
from collections import deque
import events

class RequestStatsAdditionError(Exception):
    pass
        

class RequestStats(object):
    requests = {}
    request_observers = []
    total_num_requests = 0
    global_max_requests = None
    global_last_request_timestamp = None
    global_start_time = None
    errors = {}

    def __init__(self, name):
        self.name = name
        self.num_reqs_per_sec = {}
        self.last_request_timestamp = 0
        self.reset()
    
    @classmethod
    def reset_all(cls):
        cls.total_num_requests = 0
        for name, stats in cls.requests.iteritems():
            stats.reset()
        cls.errors = {}
    
    def reset(self):
        self.start_time = time.time()
        self.num_reqs = 0
        self.num_failures = 0
        self.total_response_time = 0
        self.response_times = {}
        self._min_response_time = None
        self.max_response_time = 0
        self.last_request_timestamp = int(time.time())
        self.num_reqs_per_sec = {}
        self.total_content_length = 0

    def log(self, response_time, content_length):
        RequestStats.total_num_requests += 1

        self.num_reqs += 1
        self.total_response_time += response_time
        
        t = int(time.time())
        self.num_reqs_per_sec[t] = self.num_reqs_per_sec.setdefault(t, 0) + 1
        self.last_request_timestamp = t
        RequestStats.global_last_request_timestamp = t

        if self._min_response_time is None:
            self._min_response_time = response_time
            
        self._min_response_time = min(self._min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)
        
        # to avoid to much data that has to be transfered to the master node when
        # running in distributed mode, we save the response time rounded in a dict
        # so that 147 becomes 150, 3432 becomes 3400 and 58760 becomes 59000
        if response_time < 100:
            rounded_response_time = response_time
        elif response_time < 1000:
            rounded_response_time = int(round(response_time, -1))
        elif response_time < 10000:
            rounded_response_time = int(round(response_time, -2))
        else:
            rounded_response_time = int(round(response_time, -3))
        # increase request count for the rounded key in response time dict
        self.response_times.setdefault(rounded_response_time, 0)
        self.response_times[rounded_response_time] += 1
        
        # increase total content-length
        self.total_content_length += content_length
    
    def log_error(self, error):
        self.num_failures += 1
        key = "%r: %s" % (error, repr(str(error)))
        RequestStats.errors.setdefault(key, 0)
        RequestStats.errors[key] += 1
        
    @property
    def min_response_time(self):
        if self._min_response_time is None:
            return 0
        return self._min_response_time
    
    @property
    def avg_response_time(self):
        try:
            return float(self.total_response_time) / self.num_reqs
        except ZeroDivisionError:
            return 0
    
    @property
    def median_response_time(self):
        if not self.response_times:
            return 0
        
        def median(total, count):
            """
            total is the number of requests made
            count is a dict {response_time: count}
            """
            pos = (total - 1) / 2
            for k in sorted(count.iterkeys()):
                if pos < count[k]:
                    return k
                pos -= count[k]
        
        return median(self.num_reqs, self.response_times)
    
    @property
    def current_rps(self):
        if self.global_last_request_timestamp is None:
            return 0
        slice_start_time = max(self.global_last_request_timestamp - 12, int(self.global_start_time or 0))
        
        reqs = [self.num_reqs_per_sec.get(t, 0) for t in range(slice_start_time, self.global_last_request_timestamp-2)]
        return avg(reqs)

    @property
    def total_rps(self):
        if not RequestStats.global_last_request_timestamp:
            return 0.0
        
        return self.num_reqs / max(RequestStats.global_last_request_timestamp - RequestStats.global_start_time, 1)
    
    @property
    def avg_content_length(self):
        try:
            return self.total_content_length / self.num_reqs
        except ZeroDivisionError:
            return 0

    def __add__(self, other):
        #if self.name != other.name:
        #    raise RequestStatsAdditionError("Trying to add two RequestStats objects of different names (%s and %s)" % (self.name, other.name))
        
        new = RequestStats(self.name)
        new.last_request_timestamp = max(self.last_request_timestamp, other.last_request_timestamp)
        new.start_time = min(self.start_time, other.start_time)
        
        new.num_reqs = self.num_reqs + other.num_reqs
        new.num_failures = self.num_failures + other.num_failures
        new.total_response_time = self.total_response_time + other.total_response_time
        new.max_response_time = max(self.max_response_time, other.max_response_time)
        new._min_response_time = min(self._min_response_time, other._min_response_time) or other._min_response_time
        new.total_content_length = self.total_content_length + other.total_content_length        
        
        def merge_dict_add(d1, d2):
            """Merge two dicts by adding the values from each dict"""
            merged = {}
            for key in set(d1.keys() + d2.keys()):
                merged[key] = d1.get(key, 0) + d2.get(key, 0)
            return merged
        
        new.num_reqs_per_sec = merge_dict_add(self.num_reqs_per_sec, other.num_reqs_per_sec)
        new.response_times = merge_dict_add(self.response_times, other.response_times)
        return new
    
    def get_stripped_report(self):
        report = copy(self)
        self.reset()
        return report
    
    def to_dict(self):
        return {
            'num_reqs': self.num_reqs,
            'num_failures': self.num_failures,
            'avg': self.avg_response_time,
            'min': self.min_response_time,
            'max': self.max_response_time,
            'current_req_per_sec': self.current_rps
        }

    def __str__(self):
        try:
            fail_percent = (self.num_failures/float(self.num_reqs))*100
        except ZeroDivisionError:
            fail_percent = 0
        
        return " %-40s %7d %12s %7d %7d %7d  | %7d %7.2f" % (
            self.name,
            self.num_reqs,
            "%d(%.2f%%)" % (self.num_failures, fail_percent),
            self.avg_response_time,
            self.min_response_time,
            self.max_response_time,
            self.median_response_time or 0,
            self.current_rps or 0
        )
    
    def create_response_times_list(self):
        inflated_list = []
        for response_time, count in self.response_times.iteritems():
            inflated_list.extend([response_time for x in xrange(0, count)])
        inflated_list.sort()

        return inflated_list

    def percentile(self, tpl=" %-40s %8d %6d %6d %6d %6d %6d %6d %6d %6d %6d"):
        inflated_list = self.create_response_times_list()
        return tpl % (
            self.name,
            self.num_reqs,
            percentile(inflated_list, 0.5),
            percentile(inflated_list, 0.66),
            percentile(inflated_list, 0.75),
            percentile(inflated_list, 0.80),
            percentile(inflated_list, 0.90),
            percentile(inflated_list, 0.95),
            percentile(inflated_list, 0.98),
            percentile(inflated_list, 0.99),
            percentile(inflated_list, 1.0)
        )

    @classmethod
    def get(cls, name):
        request = cls.requests.get(name, None)
        if not request:
            request = RequestStats(name)
            cls.requests[name] = request
        return request
    
    @classmethod
    def sum_stats(cls, name="Total"):
        stats = RequestStats(name)
        for s in cls.requests.itervalues():
            stats += s
        return stats

def avg(values):
    return sum(values, 0.0) / max(len(values), 1)

# TODO Use interpolation or not?
def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return 0
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

def on_request_success(name, response_time, response):
    if RequestStats.global_max_requests is not None and RequestStats.total_num_requests >= RequestStats.global_max_requests:
        raise InterruptLocust("Maximum number of requests reached")
    
    content_length = int(response.info.getheader("Content-Length") or 0)
    RequestStats.get(name).log(response_time, content_length)

def on_request_failure(name, response_time, error, response=None):
    RequestStats.get(name).log_error(error)

def on_report_to_master(client_id, data):
    data["stats"] = [RequestStats.requests[name].get_stripped_report() for name in RequestStats.requests if not (RequestStats.requests[name].num_reqs == 0 and RequestStats.requests[name].num_failures == 0)]
    data["errors"] =  RequestStats.errors
    RequestStats.errors = {}

def on_slave_report(client_id, data):
    for stats in data["stats"]:
        if not stats.name in RequestStats.requests:
            RequestStats.requests[stats.name] = RequestStats(stats.name)
        RequestStats.requests[stats.name] += stats
        RequestStats.global_last_request_timestamp = max(RequestStats.global_last_request_timestamp, stats.last_request_timestamp)
    
    for err_message, err_count in data["errors"].iteritems():
        RequestStats.errors[err_message] = RequestStats.errors.setdefault(err_message, 0) + err_count

events.request_success += on_request_success
events.request_failure += on_request_failure
events.report_to_master += on_report_to_master
events.slave_report += on_slave_report


def print_stats(stats):
    print " %-40s %7s %12s %7s %7s %7s  | %7s %7s" % ('Name', '# reqs', '# fails', 'Avg', 'Min', 'Max', 'Median', 'req/s')
    print "-" * 120
    total_rps = 0
    total_reqs = 0
    total_failures = 0
    for r in stats.itervalues():
        total_rps += r.current_rps
        total_reqs += r.num_reqs
        total_failures += r.num_failures
        print r
    print "-" * 120

    try:
        fail_percent = (total_failures/float(total_reqs))*100
    except ZeroDivisionError:
        fail_percent = 0

    print " %-40s %7d %12s %42.2f" % ('Total', total_reqs, "%d(%.2f%%)" % (total_failures, fail_percent), total_rps)
    print ""

def print_percentile_stats(stats):
    print "Percentage of the requests completed within given times" 
    print " %-40s %8s %6s %6s %6s %6s %6s %6s %6s %6s %6s" % ('Name', '# reqs', '50%', '66%', '75%', '80%', '90%', '95%', '98%', '99%', '100%')
    print "-" * 120
    complete_list = []
    for r in stats.itervalues():
        if r.response_times:
            print r.percentile()
            complete_list.extend(r.create_response_times_list())
    print "-" * 120
    complete_list.sort()
    if complete_list:
        print " %-40s %8s %6d %6d %6d %6d %6d %6d %6d %6d %6d" % (
            'Total',
            str(len(complete_list)),
            percentile(complete_list, 0.5),
            percentile(complete_list, 0.66),
            percentile(complete_list, 0.75),
            percentile(complete_list, 0.8),
            percentile(complete_list, 0.9),
            percentile(complete_list, 0.95),
            percentile(complete_list, 0.98),
            percentile(complete_list, 0.99),
            complete_list[-1]
        )
    print ""

def print_error_report():
    print "Error report"
    print " %-18s %-100s" % ("# occurences", "Error")
    print "-" * 120
    for error, count in RequestStats.errors.iteritems():
        print " %-18i %-100s" % (count, error)
    print "-" * 120
    print

def stats_printer():
    from core import locust_runner
    while True:
        print_stats(locust_runner.request_stats)
        gevent.sleep(2)
