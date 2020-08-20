import datetime
import hashlib
import time
from collections import namedtuple, OrderedDict
from copy import copy
from itertools import chain
import csv

import gevent

from .exception import StopUser

import logging
console_logger = logging.getLogger("locust.stats_logger")

STATS_NAME_WIDTH = 60
STATS_TYPE_WIDTH = 8

"""Default interval for how frequently results are written to console."""
CONSOLE_STATS_INTERVAL_SEC = 2

"""Default interval for how frequently results are written to history."""
HISTORY_STATS_INTERVAL_SEC = 5

"""Default interval for how frequently CSV files are written if this option is configured."""
CSV_STATS_INTERVAL_SEC = 1
CSV_STATS_FLUSH_INTERVAL_SEC = 10


"""
Default window size/resolution - in seconds - when calculating the current 
response time percentile
"""
CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW = 10


CachedResponseTimes = namedtuple("CachedResponseTimes", ["response_times", "num_requests"])

PERCENTILES_TO_REPORT = [
    0.50,
    0.66,
    0.75,
    0.80,
    0.90,
    0.95,
    0.98,
    0.99,
    0.999,
    0.9999,
    1.0
]


class RequestStatsAdditionError(Exception):
    pass


def get_readable_percentiles(percentile_list):
    """
    Converts a list of percentiles from 0-1 fraction to 0%-100% view for using in console & csv reporting
    :param percentile_list: The list of percentiles in range 0-1
    :return: The list of string representation for each percentile in 0%-100% view
    """
    return [f"{int(percentile * 100) if (percentile * 100).is_integer() else round(100 * percentile, 6)}%"
            for percentile in percentile_list]


def calculate_response_time_percentile(response_times, num_requests, percent):
    """
    Get the response time that a certain number of percent of the requests
    finished within. Arguments:
    
    response_times: A StatsEntry.response_times dict
    num_requests: Number of request made (could be derived from response_times, 
                  but we save some CPU cycles by using the value which we already store)
    percent: The percentile we want to calculate. Specified in range: 0.0 - 1.0
    """
    num_of_request = int((num_requests * percent))

    processed_count = 0
    for response_time in sorted(response_times.keys(), reverse=True):
        processed_count += response_times[response_time]
        if(num_requests - processed_count <= num_of_request):
            return response_time
    # if all response times were None
    return 0


def diff_response_time_dicts(latest, old):
    """
    Returns the delta between two {response_times:request_count} dicts.
    
    Used together with the response_times cache to get the response times for the 
    last X seconds, which in turn is used to calculate the current response time 
    percentiles.
    """
    new = {}
    for time in latest:
        diff = latest[time] - old.get(time, 0)
        if diff:
            new[time] = diff
    return new


class RequestStats(object):
    """
    Class that holds the request statistics.
    """
    def __init__(self, use_response_times_cache=True):
        """
        :param use_response_times_cache: The value of use_response_times_cache will be set for each StatsEntry()
                                         when they are created. Settings it to False saves some memory and CPU 
                                         cycles which we can do on Worker nodes where the response_times_cache 
                                         is not needed.
        """
        self.use_response_times_cache = use_response_times_cache
        self.entries = {}
        self.errors = {}
        self.total = StatsEntry(self, "Aggregated", None, use_response_times_cache=self.use_response_times_cache)
        self.history = []
    
    @property
    def num_requests(self):
        return self.total.num_requests
    
    @property
    def num_none_requests(self):
        return self.total.num_none_requests

    @property
    def num_failures(self):
        return self.total.num_failures
    
    @property
    def last_request_timestamp(self):
        return self.total.last_request_timestamp
    
    @property
    def start_time(self):
        return self.total.start_time
    
    def log_request(self, method, name, response_time, content_length):
        self.total.log(response_time, content_length)
        self.get(name, method).log(response_time, content_length)
    
    def log_error(self, method, name, error):
        self.total.log_error(error)
        self.get(name, method).log_error(error)
        
        # store error in errors dict
        key = StatsError.create_key(method, name, error)
        entry = self.errors.get(key)
        if not entry:
            entry = StatsError(method, name, error)
            self.errors[key] = entry
        entry.occurred()
    
    def get(self, name, method):
        """
        Retrieve a StatsEntry instance by name and method
        """
        entry = self.entries.get((name, method))
        if not entry:
            entry = StatsEntry(self, name, method, use_response_times_cache=self.use_response_times_cache)
            self.entries[(name, method)] = entry
        return entry
    
    def reset_all(self):
        """
        Go through all stats entries and reset them to zero
        """
        self.total.reset()
        self.errors = {}
        for r in self.entries.values():
            r.reset()
        self.history = []
    
    def clear_all(self):
        """
        Remove all stats entries and errors
        """
        self.total = StatsEntry(self, "Aggregated", None, use_response_times_cache=self.use_response_times_cache)
        self.entries = {}
        self.errors = {}
        self.history = []
    
    def serialize_stats(self):
        return [self.entries[key].get_stripped_report() for key in self.entries.keys() if not (self.entries[key].num_requests == 0 and self.entries[key].num_failures == 0)]
    
    def serialize_errors(self):
        return dict([(k, e.to_dict()) for k, e in self.errors.items()])
        

class StatsEntry(object):
    """
    Represents a single stats entry (name and method)
    """
    
    name = None
    """ Name (URL) of this stats entry """
    
    method = None
    """ Method (GET, POST, PUT, etc.) """
    
    num_requests = None
    """ The number of requests made """
    
    num_none_requests = None
    """ The number of requests made with a None response time (typically async requests) """

    num_failures = None
    """ Number of failed request """
    
    total_response_time = None
    """ Total sum of the response times """
    
    min_response_time = None
    """ Minimum response time """
    
    max_response_time = None
    """ Maximum response time """
    
    num_reqs_per_sec = None
    """ A {second => request_count} dict that holds the number of requests made per second """

    num_fail_per_sec = None
    """ A (second => failure_count) dict that hold the number of failures per second """    
    
    response_times = None
    """
    A {response_time => count} dict that holds the response time distribution of all
    the requests.
    
    The keys (the response time in ms) are rounded to store 1, 2, ... 9, 10, 20. .. 90, 
    100, 200 .. 900, 1000, 2000 ... 9000, in order to save memory.
    
    This dict is used to calculate the median and percentile response times.
    """
    
    use_response_times_cache = False
    """
    If set to True, the copy of the response_time dict will be stored in response_times_cache 
    every second, and kept for 20 seconds (by default, will be CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW + 10). 
    We can use this dict to calculate the *current*  median response time, as well as other response 
    time percentiles.
    """
    
    response_times_cache = None
    """
    If use_response_times_cache is set to True, this will be a {timestamp => CachedResponseTimes()} 
    OrderedDict that holds a copy of the response_times dict for each of the last 20 seconds.
    """
    
    total_content_length = None
    """ The sum of the content length of all the requests for this entry """
    
    start_time = None
    """ Time of the first request for this entry """
    
    last_request_timestamp = None
    """ Time of the last request for this entry """
    
    def __init__(self, stats, name, method, use_response_times_cache=False):
        self.stats = stats
        self.name = name
        self.method = method
        self.use_response_times_cache = use_response_times_cache
        self.reset()
    
    def reset(self):
        self.start_time = time.time()
        self.num_requests = 0
        self.num_none_requests = 0
        self.num_failures = 0
        self.total_response_time = 0
        self.response_times = {}
        self.min_response_time = None
        self.max_response_time = 0
        self.last_request_timestamp = None
        self.num_reqs_per_sec = {}
        self.num_fail_per_sec = {}
        self.total_content_length = 0
        if self.use_response_times_cache:
            self.response_times_cache = OrderedDict()
            self._cache_response_times(int(time.time()))
    
    def log(self, response_time, content_length):
        # get the time
        current_time = time.time()
        t = int(current_time)
        
        if self.use_response_times_cache and self.last_request_timestamp and t > int(self.last_request_timestamp):
            # see if we shall make a copy of the response_times dict and store in the cache
            self._cache_response_times(t-1)
        
        self.num_requests += 1
        self._log_time_of_request(current_time)
        self._log_response_time(response_time)

        # increase total content-length
        self.total_content_length += content_length

    def _log_time_of_request(self, current_time):
        t = int(current_time)
        self.num_reqs_per_sec[t] = self.num_reqs_per_sec.setdefault(t, 0) + 1
        self.last_request_timestamp = current_time

    def _log_response_time(self, response_time):
        if response_time is None:
            self.num_none_requests += 1
            return

        self.total_response_time += response_time

        if self.min_response_time is None:
            self.min_response_time = response_time

        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)

        # to avoid to much data that has to be transferred to the master node when
        # running in distributed mode, we save the response time rounded in a dict
        # so that 147 becomes 150, 3432 becomes 3400 and 58760 becomes 59000
        if response_time < 100:
            rounded_response_time = round(response_time)
        elif response_time < 1000:
            rounded_response_time = round(response_time, -1)
        elif response_time < 10000:
            rounded_response_time = round(response_time, -2)
        else:
            rounded_response_time = round(response_time, -3)

        # increase request count for the rounded key in response time dict
        self.response_times.setdefault(rounded_response_time, 0)
        self.response_times[rounded_response_time] += 1

    def log_error(self, error):
        self.num_failures += 1
        t = int(time.time())
        self.num_fail_per_sec[t] = self.num_fail_per_sec.setdefault(t, 0) + 1

    @property
    def fail_ratio(self):
        try:
            return float(self.num_failures) / self.num_requests
        except ZeroDivisionError:
            if self.num_failures > 0:
                return 1.0
            else:
                return 0.0

    @property
    def avg_response_time(self):
        try:
            return float(self.total_response_time) / (self.num_requests - self.num_none_requests)
        except ZeroDivisionError:
            return 0

    @property
    def median_response_time(self):
        if not self.response_times:
            return 0
        median = median_from_dict(self.num_requests - self.num_none_requests, self.response_times) or 0

        # Since we only use two digits of precision when calculating the median response time 
        # while still using the exact values for min and max response times, the following checks 
        # makes sure that we don't report a median > max or median < min when a StatsEntry only 
        # have one (or very few) really slow requests
        if median > self.max_response_time:
            median = self.max_response_time
        elif median < self.min_response_time:
            median = self.min_response_time

        return median

    @property
    def current_rps(self):
        if self.stats.last_request_timestamp is None:
            return 0
        slice_start_time = max(int(self.stats.last_request_timestamp) - 12, int(self.stats.start_time or 0))

        reqs = [self.num_reqs_per_sec.get(t, 0) for t in range(slice_start_time, int(self.stats.last_request_timestamp)-2)]
        return avg(reqs)

    @property
    def current_fail_per_sec(self):
        if self.stats.last_request_timestamp is None:
            return 0
        slice_start_time = max(int(self.stats.last_request_timestamp) - 12, int(self.stats.start_time or 0))

        reqs = [self.num_fail_per_sec.get(t, 0) for t in range(slice_start_time, int(self.stats.last_request_timestamp)-2)]
        return avg(reqs)

    @property
    def total_rps(self):
        if not self.stats.last_request_timestamp or not self.stats.start_time:
            return 0.0
        try:
            return self.num_requests / (self.stats.last_request_timestamp - self.stats.start_time)
        except ZeroDivisionError:
            return 0.0
    
    @property
    def total_fail_per_sec(self):
        if not self.stats.last_request_timestamp or not self.stats.start_time:
            return 0.0
        try:
            return self.num_failures / (self.stats.last_request_timestamp - self.stats.start_time)
        except ZeroDivisionError:
            return 0.0

    @property
    def avg_content_length(self):
        try:
            return self.total_content_length / self.num_requests
        except ZeroDivisionError:
            return 0
    
    def extend(self, other):
        """
        Extend the data from the current StatsEntry with the stats from another
        StatsEntry instance. 
        """
        # save the old last_request_timestamp, to see if we should store a new copy
        # of the response times in the response times cache
        old_last_request_timestamp = self.last_request_timestamp
        
        if self.last_request_timestamp is not None and other.last_request_timestamp is not None:
            self.last_request_timestamp = max(self.last_request_timestamp, other.last_request_timestamp)
        elif other.last_request_timestamp is not None:
            self.last_request_timestamp = other.last_request_timestamp
        self.start_time = min(self.start_time, other.start_time)

        self.num_requests = self.num_requests + other.num_requests
        self.num_none_requests = self.num_none_requests + other.num_none_requests
        self.num_failures = self.num_failures + other.num_failures
        self.total_response_time = self.total_response_time + other.total_response_time
        self.max_response_time = max(self.max_response_time, other.max_response_time)
        if self.min_response_time is not None and other.min_response_time is not None:
            self.min_response_time = min(self.min_response_time, other.min_response_time)
        elif other.min_response_time is not None:
            # this means self.min_response_time is None, so we can safely replace it
            self.min_response_time = other.min_response_time
        self.total_content_length = self.total_content_length + other.total_content_length

        for key in other.response_times:
            self.response_times[key] = self.response_times.get(key, 0) + other.response_times[key]
        for key in other.num_reqs_per_sec:
            self.num_reqs_per_sec[key] = self.num_reqs_per_sec.get(key, 0) + other.num_reqs_per_sec[key]
        for key in other.num_fail_per_sec:
            self.num_fail_per_sec[key] = self.num_fail_per_sec.get(key, 0) + other.num_fail_per_sec[key]
        
        if self.use_response_times_cache:
            # If we've entered a new second, we'll cache the response times. Note that there 
            # might still be reports from other worker nodes - that contains requests for the same
            # time periods - that hasn't been received/accounted for yet. This will cause the cache to 
            # lag behind a second or two, but since StatsEntry.current_response_time_percentile() 
            # (which is what the response times cache is used for) uses an approximation of the 
            # last 10 seconds anyway, it should be fine to ignore this. 
            last_time = self.last_request_timestamp and int(self.last_request_timestamp) or None
            if last_time and last_time > (old_last_request_timestamp and int(old_last_request_timestamp) or 0):
                self._cache_response_times(last_time)
    
    def serialize(self):
        return {
            "name": self.name,
            "method": self.method,
            "last_request_timestamp": self.last_request_timestamp,
            "start_time": self.start_time,
            "num_requests": self.num_requests,
            "num_none_requests": self.num_none_requests,
            "num_failures": self.num_failures,
            "total_response_time": self.total_response_time,
            "max_response_time": self.max_response_time,
            "min_response_time": self.min_response_time,
            "total_content_length": self.total_content_length,
            "response_times": self.response_times,
            "num_reqs_per_sec": self.num_reqs_per_sec,
            "num_fail_per_sec": self.num_fail_per_sec,
        }
    
    @classmethod
    def unserialize(cls, data):
        obj = cls(None, data["name"], data["method"])
        for key in [
            "last_request_timestamp",
            "start_time",
            "num_requests",
            "num_none_requests",
            "num_failures",
            "total_response_time",
            "max_response_time",
            "min_response_time",
            "total_content_length",
            "response_times",
            "num_reqs_per_sec",
            "num_fail_per_sec",
        ]:
            setattr(obj, key, data[key])
        return obj
    
    def get_stripped_report(self):
        """
        Return the serialized version of this StatsEntry, and then clear the current stats.
        """
        report = self.serialize()
        self.reset()
        return report
    
    def to_string(self, current=True):
        """
        Return the stats as a string suitable for console output. If current is True, it'll show 
        the RPS and failure rate for the last 10 seconds. If it's false, it'll show the total stats
        for the whole run.
        """
        if current:
            rps = self.current_rps
            fail_per_sec = self.current_fail_per_sec
        else:
            rps = self.total_rps
            fail_per_sec = self.total_fail_per_sec
        return (" %-" + str(STATS_NAME_WIDTH) + "s %7d %12s  | %7d %7d %7d %7d  | %7.2f %7.2f") % (
            (self.method and self.method + " " or "") + self.name,
            self.num_requests,
            "%d(%.2f%%)" % (self.num_failures, self.fail_ratio * 100),
            self.avg_response_time,
            self.min_response_time or 0,
            self.max_response_time,
            self.median_response_time or 0,
            rps or 0,
            fail_per_sec or 0,
        )
    
    def __str__(self):
        return self.to_string(current=True)
    
    def get_response_time_percentile(self, percent):
        """
        Get the response time that a certain number of percent of the requests
        finished within.
        
        Percent specified in range: 0.0 - 1.0
        """
        return calculate_response_time_percentile(self.response_times, self.num_requests, percent)
    
    def get_current_response_time_percentile(self, percent):
        """
        Calculate the *current* response time for a certain percentile. We use a sliding 
        window of (approximately) the last 10 seconds (specified by CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW) 
        when calculating this.
        """
        if not self.use_response_times_cache:
            raise ValueError("StatsEntry.use_response_times_cache must be set to True if we should be able to calculate the _current_ response time percentile")
        # First, we want to determine which of the cached response_times dicts we should 
        # use to get response_times for approximately 10 seconds ago. 
        t = int(time.time())
        # Since we can't be sure that the cache contains an entry for every second. 
        # We'll construct a list of timestamps which we consider acceptable keys to be used 
        # when trying to fetch the cached response_times. We construct this list in such a way 
        # that it's ordered by preference by starting to add t-10, then t-11, t-9, t-12, t-8, 
        # and so on
        acceptable_timestamps = []
        acceptable_timestamps.append(t-CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW)
        for i in range(1, 9):
            acceptable_timestamps.append(t-CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW-i)
            acceptable_timestamps.append(t-CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW+i)
        
        cached = None
        for ts in acceptable_timestamps:
            if ts in self.response_times_cache:
                cached = self.response_times_cache[ts]
                break
        
        if cached:
            # If we fond an acceptable cached response times, we'll calculate a new response 
            # times dict of the last 10 seconds (approximately) by diffing it with the current 
            # total response times. Then we'll use that to calculate a response time percentile 
            # for that timeframe
            return calculate_response_time_percentile(
                diff_response_time_dicts(self.response_times, cached.response_times), 
                self.num_requests - cached.num_requests, 
                percent,
            )
    
    def percentile(self):
        if not self.num_requests:
            raise ValueError("Can't calculate percentile on url with no successful requests")

        tpl = f" %-{str(STATS_TYPE_WIDTH)}s %-{str(STATS_NAME_WIDTH)}s %8d {' '.join(['%6d'] * len(PERCENTILES_TO_REPORT))}"

        return tpl % ((self.method, self.name)
                      + tuple([self.get_response_time_percentile(p) for p in PERCENTILES_TO_REPORT]) 
                      + (self.num_requests,))

    def _cache_response_times(self, t):
        self.response_times_cache[t] = CachedResponseTimes(
            response_times=copy(self.response_times),
            num_requests=self.num_requests,
        )
        
        
        # We'll use a cache size of CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW + 10 since - in the extreme case -
        # we might still use response times (from the cache) for t-CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW-10 
        # to calculate the current response time percentile, if we're missing cached values for the subsequent 
        # 20 seconds
        cache_size = CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW + 10
        
        if len(self.response_times_cache) > cache_size:
            # only keep the latest 20 response_times dicts
            for i in range(len(self.response_times_cache) - cache_size):
                self.response_times_cache.popitem(last=False)


class StatsError(object):
    def __init__(self, method, name, error, occurrences=0):
        self.method = method
        self.name = name
        self.error = error
        self.occurrences = occurrences

    @classmethod
    def parse_error(cls, error):
        string_error = repr(error)
        target = "object at 0x"
        target_index = string_error.find(target)
        if target_index < 0:
            return string_error
        start = target_index + len(target) - 2
        end = string_error.find(">", start)
        if end < 0:
            return string_error
        hex_address = string_error[start:end]
        return string_error.replace(hex_address, "0x....")

    @classmethod
    def create_key(cls, method, name, error):
        key = "%s.%s.%r" % (method, name, StatsError.parse_error(error))
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    def occurred(self):
        self.occurrences += 1

    def to_name(self):
        return "%s %s: %r" % (self.method, 
            self.name, repr(self.error))

    def to_dict(self):
        return {
            "method": self.method,
            "name": self.name,
            "error": StatsError.parse_error(self.error),
            "occurrences": self.occurrences
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["method"], 
            data["name"], 
            data["error"], 
            data["occurrences"]
        )


def avg(values):
    return sum(values, 0.0) / max(len(values), 1)

def median_from_dict(total, count):
    """
    total is the number of requests made
    count is a dict {response_time: count}
    """
    pos = (total - 1) / 2
    for k in sorted(count.keys()):
        if pos < count[k]:
            return k
        pos -= count[k]


def setup_distributed_stats_event_listeners(events, stats):
    def on_report_to_master(client_id, data):
        data["stats"] = stats.serialize_stats()
        data["stats_total"] = stats.total.get_stripped_report()
        data["errors"] =  stats.serialize_errors()
        stats.errors = {}
    
    def on_worker_report(client_id, data):
        for stats_data in data["stats"]:
            entry = StatsEntry.unserialize(stats_data)
            request_key = (entry.name, entry.method)
            if not request_key in stats.entries:
                stats.entries[request_key] = StatsEntry(stats, entry.name, entry.method, use_response_times_cache=True)
            stats.entries[request_key].extend(entry)
    
        for error_key, error in data["errors"].items():
            if error_key not in stats.errors:
                stats.errors[error_key] = StatsError.from_dict(error)
            else:
                stats.errors[error_key].occurrences += error["occurrences"]
        
        stats.total.extend(StatsEntry.unserialize(data["stats_total"]))
        
    events.report_to_master.add_listener(on_report_to_master)
    events.worker_report.add_listener(on_worker_report)


def print_stats(stats, current=True):
    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %7s %12s  | %7s %7s %7s %7s  | %7s %7s") % ('Name', '# reqs', '# fails', 'Avg', 'Min', 'Max', 'Median', 'req/s', 'failures/s'))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    for key in sorted(stats.entries.keys()):
        r = stats.entries[key]
        console_logger.info(r.to_string(current=current))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    console_logger.info(stats.total.to_string(current=current))
    console_logger.info("")


def print_percentile_stats(stats):
    console_logger.info("Response time percentiles (approximated)")
    headers = ('Type', 'Name') + tuple(get_readable_percentiles(PERCENTILES_TO_REPORT)) + ('# reqs',)
    console_logger.info((f" %-{str(STATS_TYPE_WIDTH)}s %-{str(STATS_NAME_WIDTH)}s %8s "
                    f"{' '.join(['%6s'] * len(PERCENTILES_TO_REPORT))}") % headers)
    separator = f'{"-" * STATS_TYPE_WIDTH}|{"-" * STATS_NAME_WIDTH}|{"-" * 9}|{("-" * 6 + "|") * len(PERCENTILES_TO_REPORT)}'
    console_logger.info(separator)
    for key in sorted(stats.entries.keys()):
        r = stats.entries[key]
        if r.response_times:
            console_logger.info(r.percentile())
    console_logger.info(separator)

    if stats.total.response_times:
        console_logger.info(stats.total.percentile())
    console_logger.info("")


def print_error_report(stats):
    if not len(stats.errors):
        return
    console_logger.info("Error report")
    console_logger.info(" %-18s %-100s" % ("# occurrences", "Error"))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    for error in stats.errors.values():
        console_logger.info(" %-18i %-100s" % (error.occurrences, error.to_name()))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    console_logger.info("")


def stats_printer(stats):
    def stats_printer_func():
        while True:
            print_stats(stats)
            gevent.sleep(CONSOLE_STATS_INTERVAL_SEC)
    return stats_printer_func

def sort_stats(stats):
    return [stats[key] for key in sorted(stats.keys())]

def stats_history(runner):
    """Save current stats info to history for charts of report."""
    while True:
        stats = runner.stats
        if not stats.total.use_response_times_cache:
            break
        r = {
            'time': datetime.datetime.now().strftime("%H:%M:%S"),
            'current_rps': stats.total.current_rps or 0,
            'current_fail_per_sec': stats.total.current_fail_per_sec or 0,
            'response_time_percentile_95': stats.total.get_current_response_time_percentile(0.95) or 0,
            'response_time_percentile_50': stats.total.get_current_response_time_percentile(0.5) or 0,
            'user_count': runner.user_count or 0,
        }
        stats.history.append(r)
        gevent.sleep(HISTORY_STATS_INTERVAL_SEC)

class StatsCSV():
    """Write statistics to csv_writer stream."""

    def __init__(self, environment, percentiles_to_report):
        super().__init__()
        self.environment = environment
        self.percentiles_to_report = percentiles_to_report

        self.percentiles_na = ["N/A"] * len(self.percentiles_to_report)

        self.requests_csv_columns = [
            "Type",
            "Name",
            "Request Count",
            "Failure Count",
            "Median Response Time",
            "Average Response Time",
            "Min Response Time",
            "Max Response Time",
            "Average Content Size",
            "Requests/s",
            "Failures/s",
        ] + get_readable_percentiles(self.percentiles_to_report)


        self.failures_columns = [
            "Method",
            "Name",
            "Error",
            "Occurrences",
        ]

    def _percentile_fields(self, stats_entry):
        return [int(stats_entry.get_response_time_percentile(x) or 0) for x in self.percentiles_to_report] if stats_entry.num_requests else self.percentiles_na

    def requests_csv(self, csv_writer):
        """Write requests csv with header and data rows."""
        csv_writer.writerow(self.requests_csv_columns)
        self._requests_data_rows(csv_writer)

    def _requests_data_rows(self, csv_writer):
        """Write requests csv data row, excluding header."""
        stats = self.environment.stats
        for stats_entry in chain(sort_stats(stats.entries), [stats.total]):
            csv_writer.writerow(
                chain([
                    stats_entry.method,
                    stats_entry.name,
                    stats_entry.num_requests,
                    stats_entry.num_failures,
                    stats_entry.median_response_time,
                    stats_entry.avg_response_time,
                    stats_entry.min_response_time or 0,
                    stats_entry.max_response_time,
                    stats_entry.avg_content_length,
                    stats_entry.total_rps,
                    stats_entry.total_fail_per_sec,
                ], self._percentile_fields(stats_entry))
            )

    def failures_csv(self, csv_writer):
        csv_writer.writerow(self.failures_columns)
        self._failures_data_rows(csv_writer)

    def _failures_data_rows(self, csv_writer):
        for stats_error in sort_stats(self.environment.stats.errors):
            csv_writer.writerow([
                stats_error.method,
                stats_error.name,
                stats_error.error,
                stats_error.occurrences,
            ])


class StatsCSVFileWriter(StatsCSV):
    """Write statistics to to CSV files"""

    def __init__(self, environment, percentiles_to_report, base_filepath, full_history=False):
        super().__init__(environment, percentiles_to_report)
        self.base_filepath = base_filepath
        self.full_history = full_history

        self.requests_csv_filehandle = open(self.base_filepath + '_stats.csv', 'w')
        self.requests_csv_writer = csv.writer(self.requests_csv_filehandle)

        self.stats_history_csv_filehandle = open(self.stats_history_file_name(), 'w')
        self.stats_history_csv_writer = csv.writer(self.stats_history_csv_filehandle)

        self.failures_csv_filehandle = open(self.base_filepath + '_failures.csv', 'w')
        self.failures_csv_writer = csv.writer(self.failures_csv_filehandle)
        self.failures_csv_data_start = 0

        self.stats_history_csv_columns = [
            "Timestamp",
            "User Count",
            "Type",
            "Name",
            "Requests/s",
            "Failures/s",
            *get_readable_percentiles(self.percentiles_to_report),
            "Total Request Count",
            "Total Failure Count",
            "Total Median Response Time",
            "Total Average Response Time",
            "Total Min Response Time",
            "Total Max Response Time",
            "Total Average Content Size",
        ]

    def __call__(self):
        self.stats_writer()

    def stats_writer(self):
        """Writes all the csv files for the locust run."""

        # Write header row for all files and save posistion for non-append files
        self.requests_csv_writer.writerow(self.requests_csv_columns)
        requests_csv_data_start = self.requests_csv_filehandle.tell()

        self.stats_history_csv_writer.writerow(self.stats_history_csv_columns)

        self.failures_csv_writer.writerow(self.failures_columns)
        self.failures_csv_data_start = self.failures_csv_filehandle.tell()

        # Continuously write date rows for all files
        last_flush_time = 0
        while True:
            now = time.time()

            self.requests_csv_filehandle.seek(requests_csv_data_start)
            self._requests_data_rows(self.requests_csv_writer)
            self.requests_csv_filehandle.truncate()

            self._stats_history_data_rows(self.stats_history_csv_writer, now)

            self.failures_csv_filehandle.seek(self.failures_csv_data_start)
            self._failures_data_rows(self.failures_csv_writer)
            self.failures_csv_filehandle.truncate()

            if now - last_flush_time > CSV_STATS_FLUSH_INTERVAL_SEC:
                self.requests_flush()
                self.stats_history_flush()
                self.failures_flush()
                last_flush_time = now

            gevent.sleep(CSV_STATS_INTERVAL_SEC)


    def _stats_history_data_rows(self, csv_writer, now):
        """
        Write CSV rows with the *current* stats. By default only includes the
        Aggregated stats entry, but if self.full_history is set to True, a row for each entry will
        will be included.

        Note that this method differs from the other methods as it appends time-stamped data to the file, whereas the other methods overwrites the data.
        """

        stats = self.environment.stats
        timestamp = int(now)
        stats_entries = []
        if self.full_history:
            stats_entries = sort_stats(stats.entries)

        for stats_entry in chain(stats_entries, [stats.total]):
            csv_writer.writerow(
                chain((
                    timestamp,
                    self.environment.runner.user_count,
                    stats_entry.method or "",
                    stats_entry.name,
                    f"{stats_entry.current_rps:2f}",
                    f"{stats_entry.current_fail_per_sec:2f}",
                ), self._percentile_fields(stats_entry), (
                    stats_entry.num_requests,
                    stats_entry.num_failures,
                    stats_entry.median_response_time,
                    stats_entry.avg_response_time,
                    stats_entry.min_response_time or 0,
                    stats_entry.max_response_time,
                    stats_entry.avg_content_length,
                ))
            )

    def requests_flush(self):
        self.requests_csv_filehandle.flush()

    def stats_history_flush(self):
        self.stats_history_csv_filehandle.flush()

    def failures_flush(self):
        self.failures_csv_filehandle.flush()

    def close_files(self):
        self.requests_csv_filehandle.close()
        self.stats_history_csv_filehandle.close()
        self.failures_csv_filehandle.close()

    def stats_history_file_name(self):
        return self.base_filepath + '_stats_history.csv'
