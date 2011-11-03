from stats import percentile, RequestStats
from core import locust_runner, DistributedLocustRunner
from collections import deque
import events
import math

master_response_times = deque([])
slave_response_times = []

# Are we running in distributed mode or not?
is_distributed = isinstance(locust_runner, DistributedLocustRunner)

# The time window in seconds that current_percentile use data from
PERCENTILE_TIME_WINDOW = 15.0

def current_percentile(percent):
    if is_distributed:
        # Flatten out the deque of lists and calculate the percentile to be returned
        return percentile(sorted([item for sublist in master_response_times for item in sublist]), percent)
    else:
        return percentile(sorted(master_response_times), percent)

def on_request_success(_, response_time, _2):
    if is_distributed:
        slave_response_times.append(response_time)
    else:
        master_response_times.append(response_time)

        # remove from the queue
        rps = RequestStats.sum_stats().current_rps
        if len(master_response_times) > rps*PERCENTILE_TIME_WINDOW:
            for i in xrange(len(master_response_times) - int(math.ceil(rps*PERCENTILE_TIME_WINDOW))):
                master_response_times.popleft()

def on_report_to_master(_, data):
    global slave_response_times
    data["current_responses"] = slave_response_times
    slave_response_times = []

def on_slave_report(_, data):
    from core import locust_runner, SLAVE_REPORT_INTERVAL
    if "current_responses" in data:
        master_response_times.append(data["current_responses"])

    # remove from the queue
    slaves = locust_runner.slave_count
    response_times_per_slave_count = PERCENTILE_TIME_WINDOW/SLAVE_REPORT_INTERVAL
    if len(master_response_times) > slaves * response_times_per_slave_count:
        master_response_times.popleft()
