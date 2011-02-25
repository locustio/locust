import time
import gevent
from copy import copy
import math
import functools

from urllib2 import URLError
from httplib import BadStatusLine

from exception import InterruptLocust
from collections import deque

class RequestStatsAdditionError(Exception):
    pass

class RequestStats(object):
    requests = {}
    request_observers = []
    total_num_requests = 0
    global_max_requests = None

    def __init__(self, name):
        self.name = name
        self.num_reqs_per_sec = {}
        self.reset()
    
    @classmethod
    def reset_all(cls):
        for name, stats in cls.requests.iteritems():
            stats.reset()
    
    def reset(self):
        self.start_time = time.time()
        self.num_reqs = 0
        self.num_failures = 0
        self.total_response_time = 0
        self.response_times = {}
        self.min_response_time = None
        self.max_response_time = 0
        self._requests = deque(maxlen=1000)

    def log(self, response_time, failure=False):
        RequestStats.total_num_requests += 1
        
        self.num_reqs += 1
        self.total_response_time += response_time
        
        t = int(time.time())
        self.num_reqs_per_sec[t] = self.num_reqs_per_sec.setdefault(t, 0) + 1

        if not failure:
            if self.min_response_time is None:
                self.min_response_time = response_time
                
            self.min_response_time = min(self.min_response_time, response_time)
            self.max_response_time = max(self.max_response_time, response_time)

            self.response_times.setdefault(response_time, 0)
            self.response_times[response_time] += 1
            
            self._requests.appendleft(response_time)
        else:
            self.num_failures += 1

    @property
    def avg_response_time(self):
        return self.total_response_time / self.num_reqs
    
    @property
    def median_response_time(self):
        return median(sorted(self._requests))
    
    @property
    def reqs_per_sec(self):
        timestamp = int(time.time())
        slice_start_time = max(timestamp - 10, int(self.start_time))
        
        reqs = [self.num_reqs_per_sec.get(t, 0) for t in range(slice_start_time, timestamp)]
        return avg(reqs)

    @property
    def total_reqs_per_sec(self):
        return self.num_reqs / (time.time() - self.start_time)

    def create_response_times_list(self):
        inflated_list = []
        for response_time, count in self.response_times.iteritems():
            inflated_list.extend([response_time for x in xrange(0, count)])
        inflated_list.sort()

        return inflated_list

    def __add__(self, other):
        if self.name != other.name:
            raise RequestStatsAdditionError("Trying to add two RequestStats objects of different names (%s and %s)" % (self.name, other.name))
        
        new = RequestStats(other.name)
        new.num_reqs = self.num_reqs + other.num_reqs
        new.num_failures = self.num_failures + other.num_failures
        new.total_response_time = self.total_response_time + other.total_response_time
        new.min_response_time = min(self.min_response_time, other.min_response_time) or other.min_response_time
        new.max_response_time = max(self.max_response_time, other.max_response_time)
        
        new.num_reqs_per_sec = copy(self.num_reqs_per_sec)
        for key in other.num_reqs_per_sec:
            new.num_reqs_per_sec[key] = new.num_reqs_per_sec.setdefault(key, 0) + other.num_reqs_per_sec[key]
        return new
    
    def to_dict(self):
        return {
            'num_reqs': self.num_reqs,
            'num_failures': self.num_failures,
            'avg': self.avg_response_time,
            'min': self.min_response_time,
            'max': self.max_response_time,
            'req_per_sec': self.reqs_per_sec
        }

    def __str__(self):
        return " %-40s %7d %12s %7d %7d %7d  | %7d %7.2f" % (
            self.name,
            self.num_reqs,
            "%d(%.2f%%)" % (self.num_failures, (self.num_failures/float(self.num_reqs))*100),
            self.avg_response_time,
            self.min_response_time or 0,
            self.max_response_time,
            self.median_response_time or 0,
            self.reqs_per_sec or 0
        )

    def percentile(self):
        inflated_list = self.create_response_times_list()

        return " %-40s %8d %6d %6d %6d %6d %6d %6d %6d %6d %6d" % (
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
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

# median is 50th percentile.
median = functools.partial(percentile, percent=0.5)

def log_request(f):
    def _wrapper(*args, **kwargs):
        name = kwargs.get('name', args[1])
        try:
            if RequestStats.global_max_requests is not None and RequestStats.total_num_requests >= RequestStats.global_max_requests:
                raise InterruptLocust("Maximum number of requests reached")
            start = time.time()
            retval = f(*args, **kwargs)
            response_time = int((time.time() - start) * 1000)
            RequestStats.get(name).log(response_time)
            return retval
        except (URLError, BadStatusLine), e:
            RequestStats.get(name).log(0, True)
    return _wrapper

def print_stats(stats):
    print " %-40s %7s %12s %7s %7s %7s  | %7s %7s" % ('Name', '# reqs', '# fails', 'Avg', 'Min', 'Max', 'Median', 'req/s')
    print "-" * 120
    for r in stats.itervalues():
        print r
    print "-" * 120
    print ""

def print_percentile_stats(stats):
    print "Percentage of the requests completed within given times" 
    print " %-40s %8s %6s %6s %6s %6s %6s %6s %6s %6s %6s" % ('Name', '# reqs', '50%', '66%', '75%', '80%', '90%', '95%', '98%', '99%', '100%')
    print "-" * 120
    complete_list = []
    for r in stats.itervalues():
        print r.percentile()
        complete_list.extend(r.create_response_times_list())
    print "-" * 120
    complete_list.sort()
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

def stats_printer():
    from core import locust_runner
    while True:
        print_stats(locust_runner.request_stats)
        gevent.sleep(2)
