import time
import gevent

from urllib2 import URLError
from functools import wraps

class RequestStats(object):
    requests = {}

    def __init__(self, name):
        self.name = name
        self.num_reqs = 0
        self.num_reqs_per_sec = {}
        self.num_failures = 0
        
        self.response_times = [0]

    def log(self, response_time, failure=False):
        self.num_reqs += 1

        sec = int(time.time())
        num = self.num_reqs_per_sec.setdefault(sec, 0)
        self.num_reqs_per_sec[sec] += 1
        
        if not failure:
            self.response_times.append(response_time)
        else:
            self.num_failures += 1

    def avg_response_time(self):
        return round(avg(self.response_times), 1)

    def median_response_time(self):
        return median(self.response_times)

    def min_response_time(self):
        return min(self.response_times)

    def max_response_time(self):
        return max(self.response_times)

    def percentile_90_response_time(self):
        return 0

    def reqs_per_sec(self):
        timestamp = int(time.time())
        reqs = [self.num_reqs_per_sec.get(t, 0) for t in range(timestamp - 5, timestamp)]
        return avg(reqs)

    
    def to_dict(self):
        return {
            'num_reqs': self.num_reqs,
            'num_failures': self.num_failures,
            'avg': self.avg_response_time(),
            'min': self.min_response_time(),
            'max': self.max_response_time(),
            'req_per_sec': self.reqs_per_sec()
        }

    def __str__(self):
        return "%20s %7d %8d %7d %7d %7d %7d" % (self.name,
            self.num_reqs,
            self.num_failures,
            self.avg_response_time(),
            self.min_response_time(),
            self.max_response_time(),
            self.reqs_per_sec())

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
    def wrapper(*args, **kwargs):
        name = kwargs.get('name', args[1])
        try:
            start = time.time()
            retval = f(*args, **kwargs)
            response_time = int((time.time() - start) * 1000)
            RequestStats.get(name).log(response_time)
            return retval
        except URLError, e:
            RequestStats.get(name).log(0, True)
    return wrapper


