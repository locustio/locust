import time
import gevent
import hashlib
import six
from six.moves import xrange
import tablib
from tabulate import tabulate
from collections import namedtuple
from functools import partial

try:
    import numpy
except ImportError:
    numpy = None

try:
    from scikits.bootstrap import bootstrap
except ImportError:
    bootstrap = None

CONFIDENCE_INTERVALS = numpy is not None and bootstrap is not None


from . import events
from .exception import StopLocust
from .log import console_logger

STATS_NAME_WIDTH = 60
PERCENTILES = (0.5, 0.66, 0.75, 0.80, 0.9, 0.95, 0.98, 0.99)

class RequestStatsAdditionError(Exception):
    pass


ErrorBar = namedtuple('ErrorBar', ['lower', 'upper'])


class RequestStats(object):
    def __init__(self):
        self.entries = {}
        self.errors = {}
        self.num_requests = 0
        self.num_failures = 0
        self.max_requests = None
        self.last_request_timestamp = None
        self.start_time = None
    
    def get(self, name, method):
        """
        Retrieve a StatsEntry instance by name and method
        """
        entry = self.entries.get((name, method))
        if not entry:
            entry = StatsEntry(self, name, method)
            self.entries[(name, method)] = entry
        return entry
    
    def aggregated_stats(self, name="Total", full_request_history=False):
        """
        Returns a StatsEntry which is an aggregate of all stats entries 
        within entries.
        """
        total = StatsEntry(self, name, method=None)
        for r in six.itervalues(self.entries):
            total.extend(r, full_request_history=full_request_history)
        return total
    
    def reset_all(self):
        """
        Go through all stats entries and reset them to zero
        """
        self.start_time = time.time()
        self.num_requests = 0
        self.num_failures = 0
        for r in six.itervalues(self.entries):
            r.reset()
    
    def clear_all(self):
        """
        Remove all stats entries and errors
        """
        self.num_requests = 0
        self.num_failures = 0
        self.entries = {}
        self.errors = {}
        self.max_requests = None
        self.last_request_timestamp = None
        self.start_time = None

    def percentile_column_name(self, percentile):
        """
        Return the name of the column for the `percentile` value.
        """
        return "{0:.0%}".format(percentile)

    def confidence_interval_column_name(self, percentile):
        """
        Return a ErrorBar of column names for the (lower, upper) error bar
        values for the `percentile` value.
        """
        return ErrorBar(
            "{0:.0%} low error bound".format(percentile),
            "{0:.0%} high error bound".format(percentile),
        )

    def get_percentile_dataset(self, include_empty=False):
        data = tablib.Dataset()
        data.headers = ['Method', 'Name', '# reqs']

        for percentile in PERCENTILES:
            data.headers.append(self.percentile_column_name(percentile))

            if CONFIDENCE_INTERVALS:
                data.headers.extend(self.confidence_interval_column_name(percentile))

        data.headers.append("100%")

        # Using iteritems() allows us to sort by the key while only using
        # the value.
        for _, stats in sorted(six.iteritems(self.entries)):
            data.append(stats.percentile(include_empty))

        total_stats = self.aggregated_stats(full_request_history=True)
        if total_stats.response_times:
            data.append(total_stats.percentile(include_empty))

        return data

    def get_request_stats_dataset(self):
        data = tablib.Dataset()
        data.headers = [
            "Method",
            "Name",
            "# requests",
            "# failures",
            "Median response time",
            "Average response time",
            "Min response time",
            "Max response time",
            "Average Content Size",
            "Requests/s",
        ]

        # Using iteritems() allows us to sort by the key while only using
        # the value.
        for _, stats in sorted(six.iteritems(self.entries)):
            data.append((
                stats.method,
                stats.name,
                stats.num_requests,
                stats.num_failures,
                stats.median_response_time,
                stats.avg_response_time,
                stats.min_response_time or 0,
                stats.max_response_time,
                stats.avg_content_length,
                stats.total_rps,
            ))

        total = self.aggregated_stats(full_request_history=True)
        data.append((
            total.method,
            total.name,
            total.num_requests,
            total.num_failures,
            total.median_response_time,
            total.avg_response_time,
            total.min_response_time or 0,
            total.max_response_time,
            total.avg_content_length,
            total.total_rps,
        ))

        return data


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
    
    def __init__(self, stats, name, method):
        self.stats = stats
        self.name = name
        self.method = method
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
        self.stats.num_requests += 1
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
        self.stats.num_failures += 1
        key = StatsError.create_key(self.method, self.name, error)
        entry = self.stats.errors.get(key)
        if not entry:
            entry = StatsError(self.method, self.name, error)
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
        obj = cls(None, data["name"], data["method"])
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
            self.method + " " + self.name,
            self.num_requests,
            "%d(%.2f%%)" % (self.num_failures, fail_percent),
            self.avg_response_time,
            self.min_response_time or 0,
            self.max_response_time,
            self.median_response_time or 0,
            self.current_rps or 0
        )

    def expand_response_times(self):
        """
        Return an list containing all of the response_times, unbucketed.

        N.B. the response times will still be rounded to the same values as the buckets.
        """
        return sum(([time]*count for time, count in self.response_times.iteritems()), [])

    def get_response_time_percentiles(self, percentiles=PERCENTILES):
        """
        Get the response time that a certain number of percent of the requests
        finished within, for each percent in percentiles.

        Returns a dictionary that maps the percentile inputs to their corresponding
        response times.

        Percent specified in range: 0.0 - 1.0
        """
        if numpy is not None:
            times = numpy.percentile(
                self.expand_response_times(),
                q=[percent*100 for percent in percentiles],
                interpolation='higher',  # This mimics the behavior of the non-numpy version
            )
            return dict(zip(
                percentiles,
                [int(time) for time in times],
            ))
        else:
            response_times = {}

            processed_count = 0
            target_percentiles = sorted(percentiles, reverse=True)
            for response_time, count in sorted(six.iteritems(self.response_times), reverse=True):
                processed_count += count
                while target_percentiles and float(self.num_requests - processed_count) / self.num_requests <= target_percentiles[0]:
                    response_times[target_percentiles.pop(0)] = response_time

            return response_times

    if CONFIDENCE_INTERVALS:
        def get_percentile_confidence_intervals(self, percentiles=PERCENTILES):
            """
            Return a dictionary mapping each supplied percentile value to
            ErrorBar objects representing the lower and upper percentile bounds (at 95% confidence).
            """
            console_logger.info("Computing confidence intervals on {0} requests. This may take a while...".format(self.num_requests))

            # This prevents the bootstrap process from falling over in the jacknife step
            # if all of the jacknifed stats are equal. (This has been reported to the
            # maintainer of scikits.bootstrap in https://github.com/cgevans/scikits-bootstrap/issues/6).
            all_response_times = self.expand_response_times()
            jittered_response_times = numpy.array(all_response_times) + numpy.random.randn(len(all_response_times)) * 0.001

            intervals = bootstrap.ci(
                jittered_response_times,
                partial(numpy.percentile, q=[percent*100 for percent in percentiles]),
                output="errorbar",
                method="bca" if self.num_requests > 1 else "pi",  # bca relies on the jacknife procedure, which needs more that one value
            )

            console_logger.info("Configence intervals computed.")
            return dict(zip(percentiles, [ErrorBar(float(interval[0]), float(interval[1])) for interval in intervals]))

    def percentile(self, include_empty=False):
        if not self.num_requests and not include_empty:
            raise ValueError("Can't calculate percentile on url with no successful requests")

        results = [self.method, self.name, self.num_requests]

        if self.num_requests > 0:

            percentiles = self.get_response_time_percentiles()

            if CONFIDENCE_INTERVALS:
                intervals = self.get_percentile_confidence_intervals()

            for percentile in PERCENTILES:
                results.append(percentiles[percentile])

                if CONFIDENCE_INTERVALS:
                    results.extend(intervals[percentile])

            results.append(self.max_response_time)
        else:
            if CONFIDENCE_INTERVALS:
                entry_count = 3*len(PERCENTILES) + 1
            else:
                entry_count = len(PERCENTILES) + 1

            result.extend(["N/A"] * entry_count)

        return tuple(results)


class StatsError(object):
    def __init__(self, method, name, error, occurences=0):
        self.method = method
        self.name = name
        self.error = error
        self.occurences = occurences

    @classmethod
    def create_key(cls, method, name, error):
        key = "%s.%s.%r" % (method, name, error)
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    def occured(self):
        self.occurences += 1

    def to_name(self):
        return "%s %s: %r" % (self.method, 
            self.name, repr(self.error))

    def to_dict(self):
        return {
            "method": self.method,
            "name": self.name,
            "error": repr(self.error),
            "occurences": self.occurences
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["method"], 
            data["name"], 
            data["error"], 
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

def on_request_success(request_type, name, response_time, response_length):
    if global_stats.max_requests is not None and (global_stats.num_requests + global_stats.num_failures) >= global_stats.max_requests:
        raise StopLocust("Maximum number of requests reached")
    global_stats.get(name, request_type).log(response_time, response_length)

def on_request_failure(request_type, name, response_time, exception):
    if global_stats.max_requests is not None and (global_stats.num_requests + global_stats.num_failures) >= global_stats.max_requests:
        raise StopLocust("Maximum number of requests reached")
    global_stats.get(name, request_type).log_error(exception)

def on_report_to_master(client_id, data):
    data["stats"] = [global_stats.entries[key].get_stripped_report() for key in six.iterkeys(global_stats.entries) if not (global_stats.entries[key].num_requests == 0 and global_stats.entries[key].num_failures == 0)]
    data["errors"] =  dict([(k, e.to_dict()) for k, e in six.iteritems(global_stats.errors)])
    global_stats.errors = {}

def on_slave_report(client_id, data):
    for stats_data in data["stats"]:
        entry = StatsEntry.unserialize(stats_data)
        request_key = (entry.name, entry.method)
        if not request_key in global_stats.entries:
            global_stats.entries[request_key] = StatsEntry(global_stats, entry.name, entry.method)
        global_stats.entries[request_key].extend(entry, full_request_history=True)
        global_stats.last_request_timestamp = max(global_stats.last_request_timestamp or 0, entry.last_request_timestamp)

    for error_key, error in six.iteritems(data["errors"]):
        if error_key not in global_stats.errors:
            global_stats.errors[error_key] = StatsError.from_dict(error)
        else:
            global_stats.errors[error_key].occurences += error["occurences"]

events.request_success += on_request_success
events.request_failure += on_request_failure
events.report_to_master += on_report_to_master
events.slave_report += on_slave_report


def print_stats(stats):
    data = stats.get_request_stats_dataset()
    console_logger.info(tabulate(data.dict, headers="keys"))
    console_logger.info("")

def print_percentile_stats(stats):
    data = stats.get_percentile_dataset()

    if CONFIDENCE_INTERVALS:
        for percentile in PERCENTILES:
            new_col_name = "{0} (+/-)".format(
                stats.percentile_column_name(percentile)
            )
            data.append_col([
                "{0} (+{1:.2%}/-{2:.2%})".format(
                    value, float(upper)/value, float(lower)/value
                )
                for (value, upper, lower)
                in zip(
                    data[stats.percentile_column_name(percentile)],
                    data[stats.confidence_interval_column_name(percentile)[1]],
                    data[stats.confidence_interval_column_name(percentile)[0]],
                )
            ], header=new_col_name)

            del data[stats.percentile_column_name(percentile)]
            del data[stats.confidence_interval_column_name(percentile)[0]]
            del data[stats.confidence_interval_column_name(percentile)[1]]

    # Move the 100% to the end
    values = data['100%']
    del data['100%']
    data.append_col(values, header='100%')

    console_logger.info("Percentage of the requests completed within given times")
    console_logger.info(tabulate(data.dict, headers="keys"))
    console_logger.info("")

def print_error_report():
    if not len(global_stats.errors):
        return
    console_logger.info("Error report")
    console_logger.info(" %-18s %-100s" % ("# occurences", "Error"))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    for error in six.itervalues(global_stats.errors):
        console_logger.info(" %-18i %-100s" % (error.occurences, error.to_name()))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    console_logger.info("")

def stats_printer():
    from runners import locust_runner
    while True:
        print_stats(locust_runner.stats)
        gevent.sleep(2)
