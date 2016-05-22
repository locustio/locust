#!/usr/bin/env python
# encoding: utf-8

import csv
from StringIO import StringIO
from . import runners
from itertools import chain

def _sort_stats(stats):
    return [stats[key] for key in sorted(stats.iterkeys())]

def write_exceptions_csv(filelike):
    writer = csv.writer(filelike)
    writer.writerow(["Count", "Message", "Traceback", "Nodes"])
    for exc in runners.locust_runner.exceptions.itervalues():
        nodes = ", ".join(exc["nodes"])
        writer.writerow([exc["count"], exc["msg"], exc["traceback"], nodes])
    return filelike

def write_distribution_stats_csv(filelike):
    writer = csv.writer(filelike)
    writer.writerow(['Name', '# requests', '50%', '66%', '75%', '80%', '90%', '95%', '98%', '99%', '100%'])
    for s in chain(_sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.aggregated_stats("Total", full_request_history=True)]):
        if s.num_requests:
            writer.writerow(s.percentiles())
        else:
            writer.writerow([s.name, 0] + ['N/A'] * 9)
    return filelike

def write_request_stats_csv(filelike):
    writer = csv.writer(filelike)
    extra_headers = {}
    extra_headers = dict(zip(extra_headers.values(), extra_headers.keys()))

    writer.writerow(['Method', 'Name', '# requests', '# failures', 'Median response time',
        'Average response time', 'Min response time', 'Max response time',
        'Average Content Size', 'Requests/s'] + [extra_headers[i] for i in range(len(extra_headers))])

    request_stats = runners.locust_runner.request_stats
    stats = runners.locust_runner.stats

    for s in chain(_sort_stats(request_stats), [stats.aggregated_stats("Total", full_request_history=True)]):
        writer.writerow([s.method, s.name, s.num_requests, s.num_failures, s.median_response_time,
                        s.avg_response_time, s.min_response_time or 0, s.max_response_time,
                        s.avg_content_length, s.total_rps,])
    return filelike
