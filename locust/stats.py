import time
import gevent
import hashlib

import events
from exception import StopLocust
from log import console_logger

STATS_NAME_WIDTH = 60

class RequestStatsAdditionError(Exception):
    pass

class StatsError(object):
    def __init__(self, key, error, occurences=0):
        self.key = key
        self.error = error
        self.occurences = occurences

    @classmethod
    def create_key(cls, key, error):
        key = "%s.%r" % (key, error)
        return hashlib.md5(key).hexdigest()

    def key_string(self):
        return str(self.key)

    def occured(self):
        self.occurences += 1

    def to_name(self):
        return "%s: %r" % (self.key, repr(self.error))

    def to_dict(self):
        return {
            "key": self.key,
            "error": repr(self.error),
            "occurences": self.occurences
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["key"],
            data["error"],
            data["occurences"]
        )

class RequestStatsError(StatsError):
    def __init__(self, key, error, occurences=0):
        self.method, self.name = key
        super(RequestStatsError, self).__init__(key, error, occurences)

    def key_string(self):
        return "%s %s" % self.key

    def to_dict(self):
        return {
            "method": self.method,
            "name": self.name,
            "error": repr(self.error),
            "occurences": self.occurences
        }

    def to_name(self):
        return "%s: %r" % (self.key_string, repr(self.error))

    @classmethod
    def from_dict(cls, data):
        return cls(
            ( data["method"], data["name"] ),
            data["error"],
            data["occurences"]
        )

class TaskStatsError(StatsError):
    pass

class StatsEntry(object):
    key = None
    """ The key for this item """
    
    num_items = None
    """ The number of entries made """
    
    num_failures = None
    """ Number of failed entries """
    
    total_response_time = None
    """ Total sum of the response times """
    
    min_response_time = None
    """ Minimum response time """
    
    max_response_time = None
    """ Maximum response time """
    
    num_item_per_sec = None
    """ A {second => count} dict that holds the number of itemitems per second """
    
    times = None
    """
    A {time => count} dict that holds the the time distribution of all 
    the entries.
    
    The keys (the time in ms) are rounded to store 1, 2, ... 9, 10, 20. .. 90, 
    100, 200 .. 900, 1000, 2000 ... 9000, in order to save memory.
    
    This dict is used to calculate the median and percentile times.
    """
    
    start_time = None
    """ Time of the first request for this entry """
    
    last_timestamp = None
    """ Time of the last request for this entry """

    error_class = StatsError
    """ Class to use for logging errors. """

    def __init__(self, stats, key):
        self.key = key
        self.stats = stats
        self.reset()
    
    def reset(self):
        self.start_time = time.time()
        self.num_items = 0
        self.num_failures = 0
        self.total_time = 0
        self.times = {}
        self.min_time = 0
        self.max_time = 0
        self.last_timestamp = int(time.time())
        self.num_items_per_sec = {}
        self.total_content_length = 0
    
    def log(self, duration):
        self.stats.num_items += 1
        self.num_items += 1

        self._log_time_of_action()
        self._log_duration(duration)

    def _log_time_of_action(self):
        t = int(time.time())
        self.num_items_per_sec[t] = self.num_items_per_sec.setdefault(t, 0) + 1
        self.last_timestamp = t
        self.stats.last_timestamp = t

    def _log_duration(self, duration):
        self.total_time += duration

        if self.min_time is None:
            self.min_time = duration

        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)

        # to avoid to much data that has to be transfered to the master node when
        # running in distributed mode, we save the response time rounded in a dict
        # so that 147 becomes 150, 3432 becomes 3400 and 58760 becomes 59000
        if duration < 100:
            rounded_duration = duration
        elif duration < 1000:
            rounded_duration = int(round(duration, -1))
        elif duration < 10000:
            rounded_duration = int(round(duration, -2))
        else:
            rounded_duration = int(round(duration, -3))

        # increase count for the rounded key in response duration dict
        self.times.setdefault(rounded_duration, 0)
        self.times[rounded_duration] += 1


    def log_error(self, error):
        self.num_failures += 1
        key = self.error_class.create_key(self.key, error)
        entry = self.stats.errors.get(key)
        if not entry:
            entry = self.error_class(self.key, error)
            self.stats.errors[key] = entry

        entry.occured()

    @property
    def fail_ratio(self):
        try:
            return float(self.num_failures) / (self.num_items + self.num_failures)
        except ZeroDivisionError:
            if self.num_failures > 0:
                return 1.0
            else:
                return 0.0

    @property
    def avg_time(self):
        try:
            return float(self.total_time) / self.num_items
        except ZeroDivisionError:
            return 0

    @property
    def median_time(self):
        if not self.times:
            return 0

        return median_from_dict(self.num_items, self.times)

    @property
    def current_per_sec(self):
        if self.stats.last_timestamp is None:
            return 0
        slice_start_time = max(self.stats.last_timestamp - 12, int(self.stats.start_time or 0))

        items = [self.num_items_per_sec.get(t, 0) for t in range(slice_start_time, self.stats.last_timestamp-2)]
        return avg(items)

    @property
    def total_per_sec(self):
        if not self.stats.last_timestamp or not self.stats.start_time:
            return 0

        return self.num_items / max(self.stats.last_timestamp - self.stats.start_time, 1)

    @property
    def avg_content_length(self):
        try:
            return self.total_content_length / self.num_items
        except ZeroDivisionError:
            return 0
    
    def extend(self, other, full_request_history=False):
        """
        Extend the data fro the current StatsEntry with the stats from another
        StatsEntry instance. 
        
        If full_request_history is False, we'll only care to add the data from 
        the last 20 seconds of other's stats. The reason for this argument is that 
        extend can be used to generate an aggregate of multiple different StatsEntry 
        instances on the fly, in order to get the *total* current RPS, average 
        response time, etc.
        """
        self.last_timestamp = max(self.last_timestamp, other.last_timestamp)
        self.start_time = min(self.start_time, other.start_time)

        self.num_items = self.num_items + other.num_items
        self.num_failures = self.num_failures + other.num_failures
        self.total_time = self.total_time + other.total_time
        self.max_time = max(self.max_time, other.max_time)
        self.min_time = min(self.min_time, other.min_time) or other.min_time
        self.total_content_length = self.total_content_length + other.total_content_length

        if full_request_history:
            for key in other.times:
                self.times[key] = self.times.get(key, 0) + other.times[key]
            for key in other.num_items_per_sec:
                self.num_items_per_sec[key] = self.num_items_per_sec.get(key, 0) +  other.num_items_per_sec[key]
        else:
            # still add the number of reqs per seconds the last 20 seconds
            for i in xrange(other.last_timestamp-20, other.last_timestamp+1):
                if i in other.num_items_per_sec:
                    self.num_items_per_sec[i] = self.num_items_per_sec.get(i, 0) + other.num_items_per_sec[i]
    
    def serialize(self):
        return {
            "name": self.name,
            "method": self.method,
            "last_timestamp": self.last_timestamp,
            "start_time": self.start_time,
            "num_items": self.num_items,
            "num_failures": self.num_failures,
            "total_time": self.total_time,
            "max_time": self.max_time,
            "min_time": self.min_time,
            "total_content_length": self.total_content_length,
            "times": self.times,
            "num_items_per_sec": self.num_items_per_sec,
        }
    
    @classmethod
    def unserialize(cls, data):
        obj = cls(None, (data["method"], data["name"]))
        for key in [
            "last_timestamp",
            "start_time",
            "num_items",
            "num_failures",
            "total_time",
            "max_time",
            "min_time",
            "total_content_length",
            "times",
            "num_items_per_sec",
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

    def __str__(self):
        try:
            fail_percent = (self.num_failures/float(self.num_items + self.num_failures))*100
        except ZeroDivisionError:
            fail_percent = 0
        
        return (" %-" + str(STATS_NAME_WIDTH) + "s %7d %12s %7d %7d %7d  | %7d %7.2f") % (
            self.key_string(),
            self.num_items,
            "%d(%.2f%%)" % (self.num_failures, fail_percent),
            self.avg_time,
            self.min_time,
            self.max_time,
            self.median_time or 0,
            self.current_per_sec or 0
        )


    def key_string(self):
        """Return a string representation of this key"""
        return str(self.key)

    
    def get_time_percentile(self, percent):
        """
        Get the response time that a certain number of percent of the requests
        finished within.
        
        Percent specified in range: 0.0 - 1.0
        """
        num_of_request = int((self.num_items * percent))

        processed_count = 0
        for time in sorted(self.times.iterkeys(), reverse=True):
            processed_count += self.times[time]
            if((self.num_items - processed_count) <= num_of_request):
                return time

    def percentile(self, tpl=" %-" + str(STATS_NAME_WIDTH) + "s %8d %6d %6d %6d %6d %6d %6d %6d %6d %6d"):
        if not self.num_items:
            raise ValueError("Can't calculate percentile on item with no entries")
        
        return tpl % (
            self.key_string(),
            self.num_items,
            self.get_time_percentile(0.5),
            self.get_time_percentile(0.66),
            self.get_time_percentile(0.75),
            self.get_time_percentile(0.80),
            self.get_time_percentile(0.90),
            self.get_time_percentile(0.95),
            self.get_time_percentile(0.98),
            self.get_time_percentile(0.99),
            self.max_time
        )

    def key_string(self):
        """Return a string representation of this key"""
        return str(self.key)

class Stats(object):
    stats_entry_class = StatsEntry
    """Override in subclasses"""

    def __init__(self):
        self.entries = {}
        self.errors = {}
        self.num_items = 0
        self.max_items = None
        self.last_timestamp = None
        self.start_time = None
    
    def get(self, key):
        """
        Retrieve a StatsEntry instance by name and method
        """
        entry = self.entries.get(key)
        if not entry:
            entry = self.stats_entry_class(self, key)
            self.entries[key] = entry
        return entry
    
    def aggregated_stats(self, name="Total", full_request_history=False):
        """
        Returns a StatsEntry which is an aggregate of all stats entries 
        within entries.
        """
        total = StatsEntry(self, name)
        for r in self.entries.itervalues():
            total.extend(r, full_request_history=full_request_history)
        return total
    
    def reset_all(self):
        """
        Go through all stats entries and reset them to zero
        """
        self.start_time = time.time()
        self.num_items = 0
        for r in self.entries.itervalues():
            r.reset()
    
    def clear_all(self):
        """
        Remove all stats entries and errors
        """
        self.num_items = 0
        self.entries = {}
        self.errors = {}
        self.max_items = None
        self.last_timestamp = None
        self.start_time = None
        
class RequestStatsEntry(StatsEntry):
    """
    Represents a single stats entry (name and method)
    """
    
    name = None
    """ Name (URL) of this stats entry """
    
    method = None
    """ Method (GET, POST, PUT, etc.) """

    total_content_length = None
    """ The sum of the content length of all the requests for this entry """

    error_class = RequestStatsError

    # key is (method, name)

    def __init__(self, stats, key):
        # Support calling with RequestStatsEntry("Total") and RequestStatsEntry(("GET", "/"))
        if isinstance(key, basestring):
            method = None
            name = key
        else:
            method, name = key

        self.method = method
        self.name = name

        self.key = key

        super(RequestStatsEntry, self).__init__(stats, key)

    def key_string(self):
        return "%s %s" % (self.method, self.name)
    
    def log(self, response_time, content_length):
        super(RequestStatsEntry, self).log(response_time)

        # increase total content-length
        self.total_content_length += content_length

class RequestStats(Stats):
    stats_entry_class = RequestStatsEntry

class TaskStatsEntry(StatsEntry):
    error_class = TaskStatsError

class TaskStats(Stats):
    stats_entry_class = TaskStatsEntry




def avg(values):
    return sum(values, 0.0) / max(len(values), 1)

def median_from_dict(total, count):
    """
    total is the number of requests made
    count is a dict {response_time: count}
    """
    pos = (total - 1) / 2
    for k in sorted(count.iterkeys()):
        if pos < count[k]:
            return k
        pos -= count[k]


global_stats = RequestStats()
"""
A global instance for holding the statistics. Should be removed eventually.
"""

global_task_stats = TaskStats()
"""
A global instance for holding the task statistics. Should be removed eventually.
"""

def on_request_success(method, name, response_time, response_length):
    if global_stats.max_items is not None and global_stats.num_items >= global_stats.max_items:
        raise StopLocust("Maximum number of requests reached")
    
    global_stats.get((method, name)).log(response_time, response_length)

def on_request_failure(method, name, response_time, error, response=None):
    global_stats.get((method, name)).log_error(error)

events.request_success += on_request_success
events.request_failure += on_request_failure

def on_task_success(name, response_time, response=None):
    if global_task_stats.max_items is not None and global_task_stats.num_items >= global_task_stats.max_items:
        raise StopLocust("Maximum number of tasks reached")
    
    global_task_stats.get(name).log(response_time)

def on_task_failure(name, response_time, error, response=None):
    global_task_stats.get(name).log_error(error)

events.task_success += on_task_success
events.task_failure += on_task_failure

def on_report_to_master(client_id, data):
    data["stats"] = [global_stats.entries[key].get_stripped_report() for key in global_stats.entries.iterkeys() if not (global_stats.entries[key].num_items == 0 and global_stats.entries[key].num_failures == 0)]
    data["errors"] =  dict([(k, e.to_dict()) for k, e in global_stats.errors.iteritems()])
    global_stats.errors = {}

def on_slave_report(client_id, data):
    for stats_data in data["stats"]:
        entry = RequestStatsEntry.unserialize(stats_data)
        request_key = (entry.method, entry.name)
        if not request_key in global_stats.entries:
            global_stats.entries[request_key] = RequestStatsEntry(global_stats, (entry.method, entry.name))
        global_stats.entries[request_key].extend(entry, full_request_history=True)
        global_stats.last_timestamp = max(global_stats.last_timestamp, entry.last_timestamp)

    for error_key, error in data["errors"].iteritems():
        if error_key not in global_stats.errors:
            global_stats.errors[error_key] = StatsError.from_dict(error)
        else:
            global_stats.errors[error_key].occurences += error["occurences"]

events.report_to_master += on_report_to_master
events.slave_report += on_slave_report


def print_stats(stats, name):
    console_logger.info("%s:" % name)
    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %7s %12s %7s %7s %7s  | %7s %7s") % ('Name', '#', '# fails', 'Avg', 'Min', 'Max', 'Median', '#/s'))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    total_per_sec = 0
    total_items = 0
    total_failures = 0
    for key in sorted(stats.iterkeys()):
        r = stats[key]
        total_per_sec += r.current_per_sec
        total_items += r.num_items
        total_failures += r.num_failures
        console_logger.info(r)
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))

    try:
        fail_percent = (total_failures/float(total_items))*100
    except ZeroDivisionError:
        fail_percent = 0

    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %7d %12s %42.2f") % ('Total', total_items, "%d(%.2f%%)" % (total_failures, fail_percent), total_per_sec))
    console_logger.info("")

def print_percentile_stats(stats, name):
    console_logger.info("Percentage of the %s completed within given times" % name)
    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %8s %6s %6s %6s %6s %6s %6s %6s %6s %6s") % ('Name', '#', '50%', '66%', '75%', '80%', '90%', '95%', '98%', '99%', '100%'))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    for key in sorted(stats.iterkeys()):
        r = stats[key]
        if r.times:
            console_logger.info(r.percentile())
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    
    total_stats = global_stats.aggregated_stats()
    if total_stats.times:
        console_logger.info(total_stats.percentile())
    console_logger.info("")

def print_error_report():
    console_logger.info("Error report")
    console_logger.info(" %-18s %-100s" % ("# occurences", "Error"))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    for error in global_stats.errors.itervalues():
        console_logger.info(" %-18i %-100s" % (error.occurences, error.to_name()))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    console_logger.info("")

def stats_printer():
    from runners import locust_runner
    while True:
        print_stats(locust_runner.request_stats, "Requests")
        print_stats(locust_runner.task_stats.entries, "Tasks")
        gevent.sleep(2)
