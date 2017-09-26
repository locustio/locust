import hashlib
import time
from itertools import chain

import gevent
import six

from six.moves import xrange

from . import events
from .exception import StopLocust
from .log import console_logger

STATS_NAME_WIDTH = 60

"""Default interval for how frequently the CSV file is written if this option
is configured."""
CSV_STATS_INTERVAL_SEC = 2

"""Default interval for how frequently results are written to console."""
CONSOLE_STATS_INTERVAL_SEC = 2

class RequestStatsAdditionError(Exception):
    pass


class RequestStats(object):
    
    action_agreate_label = 'Action Total'

    def __init__(self):
        self.entries = {}
        self.errors = {}
        self.tasks = {}
        self.tasks_failures = {}
        self.num_requests = 0
        self.num_failures = 0
        self.max_requests = None
        self.last_request_timestamp = None
        self.start_time = None
        self.num_success_tasks = 0
        self.num_failed_tasks = 0

    def get(self, task, name, method):
        """
        Retrieve a StatsEntry instance by name and method
        """
        entry = self.entries.get((task, name, method))
        if not entry:
            entry = StatsEntry(self, task, name, method)
            self.entries[(task, name, method)] = entry
        return entry

    def get_task(self, name):
        self.tasks[name] = self.tasks.get(name, TaskEntry(self, name))
        return self.tasks[name]

    def log(self, task, name, request_type, response_time, response_length):
        """Perform StatsEntry log for task and action in total"""
        self.num_requests += 1
        self.get(task, name, request_type).log(response_time, response_length)
        self.get(self.action_agreate_label, name, request_type).log(response_time, response_length)

    def log_error(self, task, name, request_type, exception):
        """Perform StatsEntry log error for task and action in total"""
        self.num_failures += 1
        self.get(task, name, request_type).log_error(exception)
        self.get(self.action_agreate_label, name, request_type).log_error(exception)

    def aggregated_stats(self, name="Total", full_request_history=False):
        """
        Returns a StatsEntry which is an aggregate of all stats entries
        within entries.
        """
        total = StatsEntry(self, '', name, method=None)
        for r in six.itervalues(self.entries):
            if r.task != self.action_agreate_label:
                total.extend(r, full_request_history=full_request_history)
        return total

    def aggregated_task_stats(self, name="Total"):
        """
        Returns a TaskEntry which is an aggregate of all task entries
        within tasks.
        """
        total = TaskEntry(self, name)
        for t in six.itervalues(self.tasks):
            total.extend(t)
        return total

    def reset_all(self):
        """
        Go through all stats entries and reset them to zero
        """
        self.start_time = time.time()
        self.num_requests = 0
        self.num_failures = 0
        self.num_success_tasks = 0
        self.num_failed_tasks = 0
        for r in six.itervalues(self.entries):
            r.reset()
        for t in six.itervalues(self.tasks):
            t.reset()

    def clear_all(self):
        """
        Remove all stats entries and errors
        """
        self.num_requests = 0
        self.num_failures = 0
        self.num_success_tasks = 0
        self.num_failed_tasks = 0
        self.entries = {}
        self.errors = {}
        self.tasks = {}
        self.tasks_failures = {}
        self.max_requests = None
        self.last_request_timestamp = None
        self.start_time = None


class StatsEntry(object):
    """
    Represents a single stats entry (task, name and method)
    """

    name = None
    """ Name (URL) of this stats entry """

    method = None
    """ Method (GET, POST, PUT, etc.) """

    num_requests = None
    """ The number of requests made """

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

    response_times = None
    """
    A {response_time => count} dict that holds the response time distribution of all
    the requests.

    The keys (the response time in ms) are rounded to store 1, 2, ... 9, 10, 20. .. 90, 
    100, 200 .. 900, 1000, 2000 ... 9000, in order to save memory.

    This dict is used to calculate the median and percentile response times.
    """

    total_content_length = None
    """ The sum of the content length of all the requests for this entry """

    start_time = None
    """ Time of the first request for this entry """

    last_request_timestamp = None
    """ Time of the last request for this entry """

    def __init__(self, stats, task, name, method):
        self.stats = stats
        self.name = name
        self.method = method
        self.task = task
        self.reset()

    def reset(self):
        self.start_time = time.time()
        self.num_requests = 0
        self.num_failures = 0
        self.total_response_time = 0
        self.response_times = {}
        self.min_response_time = None
        self.max_response_time = 0
        self.last_request_timestamp = int(time.time())
        self.num_reqs_per_sec = {}
        self.total_content_length = 0

    def log(self, response_time, content_length):
        self.num_requests += 1

        self._log_time_of_request()
        self._log_response_time(response_time)

        # increase total content-length
        self.total_content_length += content_length

    def _log_time_of_request(self):
        t = int(time.time())
        self.num_reqs_per_sec[t] = self.num_reqs_per_sec.setdefault(t, 0) + 1
        self.last_request_timestamp = t
        self.stats.last_request_timestamp = t

    def _log_response_time(self, response_time):
        self.total_response_time += response_time

        if self.min_response_time is None:
            self.min_response_time = response_time

        self.min_response_time = min(self.min_response_time, response_time)
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

    def log_error(self, error):
        self.num_failures += 1
        key = StatsError.create_key(self.task, self.method, self.name, error)
        entry = self.stats.errors.get(key)
        if not entry:
            entry = StatsError(self.task, self.method, self.name, error)
            self.stats.errors[key] = entry

        entry.occured()

    @property
    def fail_ratio(self):
        try:
            return float(self.num_failures) / (self.num_requests + self.num_failures)
        except ZeroDivisionError:
            if self.num_failures > 0:
                return 1.0
            else:
                return 0.0

    @property
    def avg_response_time(self):
        try:
            return float(self.total_response_time) / self.num_requests
        except ZeroDivisionError:
            return 0

    @property
    def median_response_time(self):
        if not self.response_times:
            return 0

        return median_from_dict(self.num_requests, self.response_times)

    @property
    def current_rps(self):
        if self.stats.last_request_timestamp is None:
            return 0
        slice_start_time = max(self.stats.last_request_timestamp - 12, int(self.stats.start_time or 0))

        reqs = [self.num_reqs_per_sec.get(t, 0) for t in range(slice_start_time, self.stats.last_request_timestamp-2)]
        return avg(reqs)

    @property
    def total_rps(self):
        if not self.stats.last_request_timestamp or not self.stats.start_time:
            return 0.0

        return self.num_requests / max(self.stats.last_request_timestamp - self.stats.start_time, 1)

    @property
    def avg_content_length(self):
        try:
            return self.total_content_length / self.num_requests
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
        self.last_request_timestamp = max(self.last_request_timestamp, other.last_request_timestamp)
        self.start_time = min(self.start_time, other.start_time)

        self.num_requests = self.num_requests + other.num_requests
        self.num_failures = self.num_failures + other.num_failures
        self.total_response_time = self.total_response_time + other.total_response_time
        self.max_response_time = max(self.max_response_time, other.max_response_time)
        self.min_response_time = min(self.min_response_time or 0, other.min_response_time or 0) or other.min_response_time
        self.total_content_length = self.total_content_length + other.total_content_length

        if full_request_history:
            for key in other.response_times:
                self.response_times[key] = self.response_times.get(key, 0) + other.response_times[key]
            for key in other.num_reqs_per_sec:
                self.num_reqs_per_sec[key] = self.num_reqs_per_sec.get(key, 0) +  other.num_reqs_per_sec[key]
        else:
            # still add the number of reqs per seconds the last 20 seconds
            for i in xrange(other.last_request_timestamp-20, other.last_request_timestamp+1):
                if i in other.num_reqs_per_sec:
                    self.num_reqs_per_sec[i] = self.num_reqs_per_sec.get(i, 0) + other.num_reqs_per_sec[i]

    def serialize(self):
        return {
            "task": self.task,
            "name": self.name,
            "method": self.method,
            "last_request_timestamp": self.last_request_timestamp,
            "start_time": self.start_time,
            "num_requests": self.num_requests,
            "num_failures": self.num_failures,
            "total_response_time": self.total_response_time,
            "max_response_time": self.max_response_time,
            "min_response_time": self.min_response_time,
            "total_content_length": self.total_content_length,
            "response_times": self.response_times,
            "num_reqs_per_sec": self.num_reqs_per_sec,
        }

    @classmethod
    def unserialize(cls, data):
        obj = cls(None, data["task"], data["name"], data["method"])
        for key in [
            "last_request_timestamp",
            "start_time",
            "num_requests",
            "num_failures",
            "total_response_time",
            "max_response_time",
            "min_response_time",
            "total_content_length",
            "response_times",
            "num_reqs_per_sec",
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
            fail_percent = (self.num_failures/float(self.num_requests + self.num_failures))*100
        except ZeroDivisionError:
            fail_percent = 0

        return (" %-" + str(STATS_NAME_WIDTH) + "s %7d %12s %7d %7d %7d  | %7d %7.2f") % (
            "[" + str(self.task) + "]" + " " + self.method + " " + self.name,
            self.num_requests,
            "%d(%.2f%%)" % (self.num_failures, fail_percent),
            self.avg_response_time,
            self.min_response_time or 0,
            self.max_response_time,
            self.median_response_time or 0,
            self.current_rps or 0
        )

    def get_response_time_percentile(self, percent):
        """
        Get the response time that a certain number of percent of the requests
        finished within.

        Percent specified in range: 0.0 - 1.0
        """
        num_of_request = int((self.num_requests * percent))

        processed_count = 0
        for response_time in sorted(six.iterkeys(self.response_times), reverse=True):
            processed_count += self.response_times[response_time]
            if((self.num_requests - processed_count) <= num_of_request):
                return response_time

    def percentile(self, tpl=" %-" + str(STATS_NAME_WIDTH) + "s %8d %6d %6d %6d %6d %6d %6d %6d %6d %6d"):
        if not self.num_requests:
            raise ValueError("Can't calculate percentile on url with no successful requests")

        return tpl % (
            "[" + str(self.task) + "]" + " " + str(self.method) + " " + self.name,
            self.num_requests,
            self.get_response_time_percentile(0.5),
            self.get_response_time_percentile(0.66),
            self.get_response_time_percentile(0.75),
            self.get_response_time_percentile(0.80),
            self.get_response_time_percentile(0.90),
            self.get_response_time_percentile(0.95),
            self.get_response_time_percentile(0.98),
            self.get_response_time_percentile(0.99),
            self.max_response_time
        )

class StatsError(object):
    def __init__(self, task, method, name, error, occurences=0):
        self.task = task
        self.method = method
        self.name = name
        self.error = error
        self.occurences = occurences

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
    def create_key(cls, task, method, name, error):
        key = "%s.%s.%s.%r" % (task, method, name, StatsError.parse_error(error))
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    def occured(self):
        self.occurences += 1

    def to_name(self):
        return "[%s] %s %s: %r" % (self.task, self.method, 
            self.name, repr(self.error))

    def to_dict(self):
        return {
            "task": self.task,
            "method": self.method,
            "name": self.name,
            "error": StatsError.parse_error(self.error),
            "occurences": self.occurences
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["task"],
            data["method"], 
            data["name"], 
            data["error"], 
            data["occurences"]
        )


class TaskEntry(object):
    """
    Represents a single task entry
    """

    def __init__(self, stats, task):
        self.stats = stats
        self.task = task
        self.reset()

    def reset(self):
        self.num_success = 0
        self.num_failures = 0
        self.total_execution_time = 0
        self.min_execution_time = None
        self.max_execution_time = 0

    def log(self, task_time):
        self.stats.num_success_tasks += 1
        self.num_success += 1

        self._log_execution_time(task_time)

    def _log_execution_time(self, task_time):
        self.total_execution_time += task_time

        if self.min_execution_time is None:
            self.min_execution_time = task_time

        self.min_execution_time = min(self.min_execution_time, task_time)
        self.max_execution_time = max(self.max_execution_time, task_time)

    def log_failure(self, exception, action):
        self.stats.num_failed_tasks += 1
        self.num_failures += 1
        key = TaskError.create_key(self.task, exception, action)
        entry = self.stats.tasks_failures.get(key)
        if not entry:
            entry = TaskError(self.task, exception, action)
            self.stats.tasks_failures[key] = entry

        entry.occured()

    @property
    def fail_ratio(self):
        try:
            return float(self.num_failures) / (self.num_success + self.num_failures)
        except ZeroDivisionError:
            if self.num_failures > 0:
                return 1.0
            else:
                return 0.0

    @property
    def avg_execution_time(self):
        try:
            return float(self.total_execution_time) / self.num_success
        except ZeroDivisionError:
            return 0

    def extend(self, other):
        """
        Extend the data fro the current TaskEntry with the stats from another
        TaskEntry instance.
        """
        self.num_success = self.num_success + other.num_success
        self.num_failures = self.num_failures + other.num_failures
        self.total_execution_time = self.total_execution_time + other.total_execution_time
        self.max_execution_time = max(self.max_execution_time, other.max_execution_time)
        self.min_execution_time = min(self.min_execution_time or 0, other.min_execution_time or 0) or other.min_execution_time

    def serialize(self):
        return {
            "task": self.task,
            "num_success": self.num_success,
            "num_failures": self.num_failures,
            "total_execution_time": self.total_execution_time,
            "max_execution_time": self.max_execution_time,
            "min_execution_time": self.min_execution_time
        }

    @classmethod
    def unserialize(cls, data):
        obj = cls(None, data["task"])
        for key in [
            "num_success",
            "num_failures",
            "total_execution_time",
            "max_execution_time",
            "min_execution_time"
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
            fail_percent = (self.num_failures/float(self.num_success + self.num_failures))*100
        except ZeroDivisionError:
            fail_percent = 0

        return (" %-" + str(STATS_NAME_WIDTH) + "s %9d %12s %7d %7d %7d") % (
            self.task,
            self.num_success,
            "%d(%.2f%%)" % (self.num_failures, fail_percent),
            self.avg_execution_time,
            self.min_execution_time or 0,
            self.max_execution_time
        )


class TaskError(object):
    def __init__(self, task, exception, action, occurences=0):
        self.task = task
        self.exception = exception
        self.action = action
        self.occurences = occurences

    @classmethod
    def create_key(cls, task, exception, action):
        key = "%s.%s.%r" % (task, action, StatsError.parse_error(exception))
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    def occured(self):
        self.occurences += 1

    def to_name(self):
        return "[%s] %s: %r" % (self.task, self.action, repr(self.exception))

    def to_dict(self):
        return {
            "task": self.task,
            "exception": StatsError.parse_error(self.exception),
            "action": self.action,
            "occurences": self.occurences
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["task"],
            data["exception"],
            data["action"],
            data["occurences"]
        )


def avg(values):
    return sum(values, 0.0) / max(len(values), 1)

def median_from_dict(total, count):
    """
    total is the number of requests made
    count is a dict {response_time: count}
    """
    pos = (total - 1) / 2
    for k in sorted(six.iterkeys(count)):
        if pos < count[k]:
            return k
        pos -= count[k]


global_stats = RequestStats()
"""
A global instance for holding the statistics. Should be removed eventually.
"""

def on_request_success(request_type, name, response_time, response_length, task):
    global_stats.log(task, name, request_type, response_time, response_length)
    if global_stats.max_requests is not None and (global_stats.num_requests + global_stats.num_failures) >= global_stats.max_requests:
        raise StopLocust("Maximum number of requests reached")

def on_request_failure(request_type, name, response_time, exception, task):
    global_stats.log_error(task, name, request_type, exception)
    if global_stats.max_requests is not None and (global_stats.num_requests + global_stats.num_failures) >= global_stats.max_requests:
        raise StopLocust("Maximum number of requests reached")

def on_task_success(task_name, task_time):
    global_stats.get_task(task_name).log(task_time)

def on_task_failure(task_name, task_time, exception, action):
    global_stats.get_task(task_name).log_failure(exception, action)

def on_report_to_master(node_id, data):
    data["stats"] = [global_stats.entries[key].get_stripped_report() for key in six.iterkeys(global_stats.entries) if not (global_stats.entries[key].num_requests == 0 and global_stats.entries[key].num_failures == 0)]
    data["errors"] =  dict([(k, e.to_dict()) for k, e in six.iteritems(global_stats.errors)])
    data["task_stats"] = [global_stats.tasks[key].get_stripped_report() for key in six.iterkeys(global_stats.tasks) if not (global_stats.tasks[key].num_success == 0 and global_stats.tasks[key].num_failures == 0)]
    data["tasks_failures"] =  dict([(k, e.to_dict()) for k, e in six.iteritems(global_stats.tasks_failures)])
    global_stats.errors = {}
    global_stats.tasks_failures = {}

def on_node_report(node_id, data):
    for stats_data in data["stats"]:
        entry = StatsEntry.unserialize(stats_data)
        request_key = (entry.task, entry.name, entry.method)
        if not request_key in global_stats.entries:
            global_stats.entries[request_key] = StatsEntry(global_stats, entry.task, entry.name, entry.method)
        global_stats.entries[request_key].extend(entry, full_request_history=True)
        global_stats.last_request_timestamp = max(global_stats.last_request_timestamp or 0, entry.last_request_timestamp)

    for error_key, error in six.iteritems(data["errors"]):
        if error_key not in global_stats.errors:
            global_stats.errors[error_key] = StatsError.from_dict(error)
        else:
            global_stats.errors[error_key].occurences += error["occurences"]

    for task_data in data["task_stats"]:
        entry = TaskEntry.unserialize(task_data)
        if not entry.task in global_stats.tasks:
            global_stats.tasks[entry.task] = TaskEntry(global_stats, entry.task)
        global_stats.tasks[entry.task].extend(entry)

    for error_key, error in six.iteritems(data["tasks_failures"]):
        if error_key not in global_stats.tasks_failures:
            global_stats.tasks_failures[error_key] = TaskError.from_dict(error)
        else:
            global_stats.tasks_failures[error_key].occurences += error["occurences"]

def subscribe_stats():
    events.request_success += on_request_success
    events.request_failure += on_request_failure
    events.task_success += on_task_success
    events.task_failure += on_task_failure
    events.report_to_master += on_report_to_master
    events.node_report += on_node_report

subscribe_stats()

def print_stats(stats):
    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %7s %12s %7s %7s %7s  | %7s %7s") % ('Name', '# reqs', '# fails', 'Avg', 'Min', 'Max', 'Median', 'req/s'))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    total_rps = 0
    total_reqs = 0
    total_failures = 0
    for key in sorted(six.iterkeys(stats)):
        r = stats[key]
        total_rps += r.current_rps
        total_reqs += r.num_requests
        total_failures += r.num_failures
        console_logger.info(r)
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))

    try:
        fail_percent = (total_failures/float(total_reqs))*100
    except ZeroDivisionError:
        fail_percent = 0

    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %7d %12s %42.2f") % ('Total', total_reqs, "%d(%.2f%%)" % (total_failures, fail_percent), total_rps))
    console_logger.info("")

def print_task_stats(stats):
    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %7s %12s %7s %7s %7s") % ('Name', '# success', '# fails', 'Avg', 'Min', 'Max'))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    total_tasks = 0
    total_failures = 0
    for key in sorted(six.iterkeys(stats)):
        t = stats[key]
        total_tasks += t.num_success
        total_failures += t.num_failures
        console_logger.info(t)
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))

    try:
        fail_percent = (total_failures/float(total_tasks))*100
    except ZeroDivisionError:
        fail_percent = 0

    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %9d %12s") % ('Total', total_tasks, "%d(%.2f%%)" % (total_failures, fail_percent)))
    console_logger.info("")

def print_percentile_stats(stats):
    console_logger.info("Percentage of the requests completed within given times")
    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %8s %6s %6s %6s %6s %6s %6s %6s %6s %6s") % ('Name', '# reqs', '50%', '66%', '75%', '80%', '90%', '95%', '98%', '99%', '100%'))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    for key in sorted(six.iterkeys(stats)):
        r = stats[key]
        if r.response_times:
            console_logger.info(r.percentile())
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    
    total_stats = global_stats.aggregated_stats()
    if total_stats.response_times:
        console_logger.info(total_stats.percentile())
    console_logger.info("")

def print_error_report():
    # Requests errors
    if not len(global_stats.errors):
        return
    console_logger.info("Error report")
    console_logger.info(" %-18s %-100s" % ("# occurences", "Error"))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    for error in six.itervalues(global_stats.errors):
        console_logger.info(" %-18i %-100s" % (error.occurences, error.to_name()))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    console_logger.info("")

    # Task failures
    if not len(global_stats.tasks_failures):
        return
    console_logger.info("Task failures report")
    console_logger.info(" %-18s %-100s" % ("# occurences", "Error"))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    for error in six.itervalues(global_stats.tasks_failures):
        console_logger.info(" %-18i %-100s" % (error.occurences, error.to_name()))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    console_logger.info("")

def stats_printer():
    from . import runners
    while True:
        print_stats(runners.main.request_stats)
        print_task_stats(runners.main.task_stats)
        gevent.sleep(CONSOLE_STATS_INTERVAL_SEC)

def stats_writer(base_filepath):
    """Writes the csv files for the locust run."""
    while True:
        write_stat_csvs(base_filepath)
        gevent.sleep(CSV_STATS_INTERVAL_SEC)


def write_stat_csvs(base_filepath):
    """Writes the requests and distribution csvs."""
    with open(base_filepath + '_requests.csv', "w") as f:
        f.write(requests_csv())

    with open(base_filepath + '_distribution.csv', 'w') as f:
        f.write(distribution_csv())


def sort_stats(stats):
    return [stats[key] for key in sorted(six.iterkeys(stats))]


def requests_csv():
    from . import runners

    """Returns the contents of the 'requests' tab as CSV."""
    rows = [
        ",".join([
            '"Method"',
            '"Name"',
            '"# requests"',
            '"# failures"',
            '"Median response time"',
            '"Average response time"',
            '"Min response time"',
            '"Max response time"',
            '"Average Content Size"',
            '"Requests/s"',
        ])
    ]

    for s in chain(sort_stats(runners.main.request_stats), [runners.main.stats.aggregated_stats("Total", full_request_history=True)]):
        rows.append('"%s","%s","%s",%i,%i,%i,%i,%i,%i,%i,%.2f' % (
            s.task,
            s.method,
            s.name,
            s.num_requests,
            s.num_failures,
            s.median_response_time,
            s.avg_response_time,
            s.min_response_time or 0,
            s.max_response_time,
            s.avg_content_length,
            s.total_rps,
        ))
    return "\n".join(rows)

def distribution_csv():
    """Returns the contents of the 'distribution' tab as CSV."""
    from . import runners

    rows = [",".join((
        '"Name"',
        '"# requests"',
        '"50%"',
        '"66%"',
        '"75%"',
        '"80%"',
        '"90%"',
        '"95%"',
        '"98%"',
        '"99%"',
        '"100%"',
    ))]
    for s in chain(sort_stats(runners.main.request_stats), [runners.main.stats.aggregated_stats("Total", full_request_history=True)]):
        if s.num_requests:
            rows.append(s.percentile(tpl='"%s",%i,%i,%i,%i,%i,%i,%i,%i,%i,%i'))
        else:
            rows.append('"%s",0,"N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"' % s.name)

    return "\n".join(rows)
