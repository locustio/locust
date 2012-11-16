import time
import gevent
from copy import copy

import events
from exception import StopLocust
from log import console_logger

STATS_NAME_WIDTH = 60

class RequestStatsAdditionError(Exception):
    pass

class RequestStats(object):
    requests = {}
    total_num_requests = 0
    global_max_requests = None
    global_last_request_timestamp = None
    global_start_time = None
    errors = {}

    def __init__(self, method, name):
        self.method = method
        self.name = name
        self.num_reqs_per_sec = {}
        self.last_request_timestamp = 0
        self.reset()

    @classmethod
    def clear_all(cls):
        cls.total_num_requests = 0
        cls.requests = {}
        cls.errors = {}
        cls.global_max_requests = None
        cls.global_last_request_timestamp = None
        cls.global_start_time = None

    @classmethod
    def reset_all(cls):
        cls.global_start_time = time.time()
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
        self.min_response_time = 0
        self.max_response_time = 0
        self.last_request_timestamp = int(time.time())
        self.num_reqs_per_sec = {}
        self.total_content_length = 0

    def log(self, response_time, content_length):
        RequestStats.total_num_requests += 1
        self.num_reqs += 1

        self.log_request_time()
        self.log_response_time(response_time)

        # increase total content-length
        self.total_content_length += content_length

    def log_request_time(self):
        t = int(time.time())
        self.num_reqs_per_sec[t] = self.num_reqs_per_sec.setdefault(t, 0) + 1
        self.last_request_timestamp = t
        RequestStats.global_last_request_timestamp = t

    def log_response_time(self, response_time):
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
        key = "%r: %s" % (error, repr(str(error)))
        RequestStats.errors.setdefault(key, 0)
        RequestStats.errors[key] += 1

    @property
    def fail_ratio(self):
        try:
            return float(self.num_failures) / (self.num_reqs + self.num_failures)
        except ZeroDivisionError:
            if self.num_failures > 0:
                return 1.0
            else:
                return 0.0

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

        return median_from_dict(self.num_reqs, self.response_times)

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

    def __iadd__(self, other):
        self.iadd_stats(other)
        return self

    def iadd_stats(self, other, full_request_history=False):
        self.last_request_timestamp = max(self.last_request_timestamp, other.last_request_timestamp)
        self.start_time = min(self.start_time, other.start_time)

        self.num_reqs = self.num_reqs + other.num_reqs
        self.num_failures = self.num_failures + other.num_failures
        self.total_response_time = self.total_response_time + other.total_response_time
        self.max_response_time = max(self.max_response_time, other.max_response_time)
        self.min_response_time = min(self.min_response_time, other.min_response_time) or other.min_response_time
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

        return (" %-" + str(STATS_NAME_WIDTH) + "s %7d %12s %7d %7d %7d  | %7d %7.2f") % (
            self.name,
            self.num_reqs,
            "%d(%.2f%%)" % (self.num_failures, fail_percent),
            self.avg_response_time,
            self.min_response_time,
            self.max_response_time,
            self.median_response_time or 0,
            self.current_rps or 0
        )

    def get_response_time_percentile(self, percent):
        """
        Percent specified in range: 0.0 - 1.0
        """
        num_of_request = int((self.num_reqs * percent))

        processed_count = 0
        for response_time in sorted(self.response_times.iterkeys(), reverse=True):
            processed_count += self.response_times[response_time]
            if((self.num_reqs - processed_count) <= num_of_request):
                return response_time

    def percentile(self, tpl=" %-" + str(STATS_NAME_WIDTH) + "s %8d %6d %6d %6d %6d %6d %6d %6d %6d %6d"):
        if not self.num_reqs:
            raise ValueError("Can't calculate percentile on url with no successful requests")
        return tpl % (
            self.name,
            self.num_reqs,
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

    @classmethod
    def get(cls, method, name):
        request = cls.requests.get((method, name), None)
        if not request:
            request = RequestStats(method, name)
            cls.requests[(method, name)] = request
        return request

    @classmethod
    def sum_stats(cls, name="Total", full_request_history=False):
        stats = RequestStats(None, name)
        for s in cls.requests.itervalues():
            stats.iadd_stats(s, full_request_history)
        return stats

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

def on_request_success(method, name, response_time, response_length):
    if RequestStats.global_max_requests is not None and RequestStats.total_num_requests >= RequestStats.global_max_requests:
        raise StopLocust("Maximum number of requests reached")
    
    RequestStats.get(method, name).log(response_time, response_length)

def on_request_failure(method, name, response_time, error, response=None):
    RequestStats.get(method, name).log_error(error)

def on_report_to_master(client_id, data):
    data["stats"] = [RequestStats.requests[name].get_stripped_report() for name in RequestStats.requests if not (RequestStats.requests[name].num_reqs == 0 and RequestStats.requests[name].num_failures == 0)]
    data["errors"] =  RequestStats.errors
    RequestStats.errors = {}

def on_slave_report(client_id, data):
    for stats in data["stats"]:
        request_key = (stats.method, stats.name)
        if not request_key in RequestStats.requests:
            RequestStats.requests[request_key] = RequestStats(stats.method, stats.name)
        RequestStats.requests[request_key].iadd_stats(stats, full_request_history=True)
        RequestStats.global_last_request_timestamp = max(RequestStats.global_last_request_timestamp, stats.last_request_timestamp)

    for err_message, err_count in data["errors"].iteritems():
        RequestStats.errors[err_message] = RequestStats.errors.setdefault(err_message, 0) + err_count

events.request_success += on_request_success
events.request_failure += on_request_failure
events.report_to_master += on_report_to_master
events.slave_report += on_slave_report


def print_stats(stats):
    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %7s %12s %7s %7s %7s  | %7s %7s") % ('Name', '# reqs', '# fails', 'Avg', 'Min', 'Max', 'Median', 'req/s'))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    total_rps = 0
    total_reqs = 0
    total_failures = 0
    for key in sorted(stats.iterkeys()):
        r = stats[key]
        total_rps += r.current_rps
        total_reqs += r.num_reqs
        total_failures += r.num_failures
        console_logger.info(r)
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))

    try:
        fail_percent = (total_failures/float(total_reqs))*100
    except ZeroDivisionError:
        fail_percent = 0

    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %7d %12s %42.2f") % ('Total', total_reqs, "%d(%.2f%%)" % (total_failures, fail_percent), total_rps))
    console_logger.info("")

def print_percentile_stats(stats):
    console_logger.info("Percentage of the requests completed within given times")
    console_logger.info((" %-" + str(STATS_NAME_WIDTH) + "s %8s %6s %6s %6s %6s %6s %6s %6s %6s %6s") % ('Name', '# reqs', '50%', '66%', '75%', '80%', '90%', '95%', '98%', '99%', '100%'))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    total_stats = RequestStats("", "Total")
    for key in sorted(stats.iterkeys()):
        r = stats[key]
        if r.response_times:
            console_logger.info(r.percentile())
            total_stats += r
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    if total_stats.response_times:
        console_logger.info(total_stats.percentile())
    console_logger.info("")

def print_error_report():
    console_logger.info("Error report")
    console_logger.info(" %-18s %-100s" % ("# occurences", "Error"))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    for error, count in RequestStats.errors.iteritems():
        console_logger.info(" %-18i %-100s" % (count, error))
    console_logger.info("-" * (80 + STATS_NAME_WIDTH))
    console_logger.info("")

def stats_printer():
    from runners import locust_runner
    while True:
        print_stats(locust_runner.request_stats)
        gevent.sleep(2)
