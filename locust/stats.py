import time
import gevent
from copy import copy
from decorator import decorator

from urllib2 import URLError

class RequestStatsAdditionError(Exception):
    pass

class RequestStats(object):
    requests = {}

    def __init__(self, name):
        self.name = name
        self.num_reqs = 0
        self.num_reqs_per_sec = {}
        self.num_failures = 0
        
        self.total_response_time = 0
        self.min_response_time = None
        self.max_response_time = 0

    def log(self, response_time, failure=False):
        self.num_reqs += 1
        self.total_response_time += response_time

        sec = int(time.time())
        num = self.num_reqs_per_sec.setdefault(sec, 0)
        self.num_reqs_per_sec[sec] += 1
        
        if not failure:
            if self.min_response_time is None:
                self.min_response_time = response_time
                
            self.min_response_time = min(self.min_response_time, response_time)
            self.max_response_time = max(self.max_response_time, response_time)
        else:
            self.num_failures += 1
    
    @property
    def avg_response_time(self):
        return self.total_response_time / self.num_reqs
    
    @property
    def reqs_per_sec(self):
        timestamp = int(time.time())
        reqs = [self.num_reqs_per_sec.get(t, 0) for t in range(timestamp - 10, timestamp)]
        return avg(reqs)
    
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
        return "%20s %7d %8d %7d %7d %7d %7d" % (self.name,
            self.num_reqs,
            self.num_failures,
            self.avg_response_time,
            self.min_response_time or 0,
            self.max_response_time,
            self.reqs_per_sec or 0)

    @classmethod
    def get(cls, name):
        request = cls.requests.get(name, None)
        if not request:
            request = RequestStats(name)
            cls.requests[name] = request
        return request

def avg(values):
    return sum(values, 0.0) / len(values)

def median(values):
    return sorted(values)[len(values)/2] # TODO: Check for odd/even length

def log_request(f):
    def wrapper(func, *args, **kwargs):
        name = kwargs.get('name', args[1])
        try:
            start = time.time()
            retval = func(*args, **kwargs)
            response_time = int((time.time() - start) * 1000)
            RequestStats.get(name).log(response_time)
            return retval
        except URLError, e:
            RequestStats.get(name).log(0, True)
    return decorator(wrapper, f)

def print_stats():
    from core import locust_runner
    while True:
        print "%20s %7s %8s %7s %7s %7s %7s" % ('Name', '# reqs', '# fails', 'Avg', 'Min', 'Max', 'req/s')
        print "-" * 80
        for r in locust_runner.request_stats.itervalues():
            print r
        print ""
        gevent.sleep(2)
