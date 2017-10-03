# -*- coding: utf-8 -*-

import csv
import json
import logging
import os.path
from collections import defaultdict
from itertools import chain
from time import time

import six
from six.moves.urllib.parse import urlparse
from flask import Flask, make_response, render_template, request
from gevent import pywsgi

from locust import __version__ as version
from six.moves import StringIO, xrange

from . import runners
from .cache import memoize
# from .runners import MasterLocustRunner
from .stats import distribution_csv, median_from_dict, requests_csv, sort_stats


logger = logging.getLogger(__name__)

DEFAULT_CACHE_TIME = 2.0

app = Flask(__name__)
app.debug = True
app.root_path = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def index():
    if runners.main.options.host:
        host = runners.main.options.host
    elif len(runners.main.locust_classes) > 0:
        host = runners.main.locust_classes[0].host
    else:
        host = None

    return render_template("index.html",
        state=runners.main.state,
        slave_count=runners.main.slave_count,
        worker_count=runners.main.worker_count,
        user_count=runners.main.user_count,
        version=version,
        host=host
    )

@app.route('/swarm', methods=["POST"])
def swarm():
    assert request.method == "POST"

    locust_count = int(request.form["locust_count"])
    hatch_rate = float(request.form["hatch_rate"])
    runners.main.start_hatching(locust_count, hatch_rate)
    response = make_response(json.dumps({'success': True, 'message': 'Swarming started'}))
    response.headers["Content-type"] = "application/json"
    return response

@app.route('/stop')
def stop():
    runners.main.stop()
    response = make_response(json.dumps({'success':True, 'message': 'Test stopped'}))
    response.headers["Content-type"] = "application/json"
    return response

@app.route("/stats/reset")
def reset_stats():
    runners.main.stats.reset_all()
    return "ok"

@app.route("/config", methods=["POST"])
def propagate_config():
    assert request.method == "POST"
    url = urlparse(request.form["host_url"])
    password = ":{}".format(url.password) if url.password else ''
    userdata = "{}{}@".format(url.username, password) if (password or url.username) else ''
    updates = {
        'scheme': url.scheme or runners.main.options.scheme,
        'host': "{}{}".format(userdata, url.hostname),
        'port': url.port,
    }
    runners.main.propagate_config(updates=updates)
    response = make_response(json.dumps({'success': True, 'new_host': runners.main.options.host}))
    response.headers["Content-type"] = "application/json"
    return response

@app.route("/stats/requests/csv")
def request_stats_csv():
    response = make_response(requests_csv())

    file_name = "requests_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response

@app.route("/stats/distribution/csv")
def distribution_stats_csv():

    response = make_response(distribution_csv())
    file_name = "distribution_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response

@app.route('/stats/requests')
@memoize(timeout=DEFAULT_CACHE_TIME, dynamic_timeout=True)
def request_stats():
    stats = []
    for s in chain(sort_stats(runners.main.request_stats), [runners.main.stats.aggregated_stats("Total")]):
        stats.append({
            "task": s.task,
            "method": s.method,
            "name": s.name,
            "num_requests": s.num_requests,
            "num_failures": s.num_failures,
            "avg_response_time": s.avg_response_time,
            "min_response_time": s.min_response_time or 0,
            "max_response_time": s.max_response_time,
            "current_rps": s.current_rps,
            "median_response_time": s.median_response_time,
            "avg_content_length": s.avg_content_length,
        })

    errors = [e.to_dict() for e in six.itervalues(runners.main.errors)]

    # Truncate the total number of stats and errors displayed since a large number of rows will cause the app
    # to render extremely slowly. Aggregate stats should be preserved.
    report = {"stats": stats[:500], "errors": errors[:500]}

    if stats:
        report["total_rps"] = stats[len(stats)-1]["current_rps"]
        report["fail_ratio"] = runners.main.stats.aggregated_stats("Total").fail_ratio

        # since generating a total response times dict with all response times from all
        # urls is slow, we make a new total response time dict which will consist of one
        # entry per url with the median response time as key and the number of requests as
        # value
        response_times = defaultdict(int) # used for calculating total median
        for i in xrange(len(stats)-1):
            response_times[stats[i]["median_response_time"]] += stats[i]["num_requests"]

        # calculate total median
        stats[len(stats)-1]["median_response_time"] = median_from_dict(stats[len(stats)-1]["num_requests"], response_times)

    task_stats = []
    for t in chain(sort_stats(runners.main.task_stats), [runners.main.stats.aggregated_task_stats("Total")]):
        task_stats.append({
            "task": t.task,
            "num_success": t.num_success,
            "num_failures": t.num_failures,
            "avg_execution_time": t.avg_execution_time,
            "max_execution_time": t.max_execution_time,
            "min_execution_time": t.min_execution_time
        })
    
    tasks_failures = [f.to_dict() for f in six.itervalues(runners.main.stats.tasks_failures)]
    report["taskStats"] = task_stats
    report["tasksFailures"] = tasks_failures

    report["slave_count"] = runners.main.slave_count

    report["state"] = runners.main.state
    report["user_count"] = runners.main.user_count
    report["worker_count"] = runners.main.worker_count
    
    return json.dumps(report)

@app.route("/exceptions")
def exceptions():
    response = make_response(json.dumps({
        'exceptions': [
            {
                "count": row["count"],
                "msg": row["msg"],
                "traceback": row["traceback"],
                "nodes" : ", ".join(row["nodes"])
            } for row in six.itervalues(runners.main.exceptions)
        ]
    }))
    response.headers["Content-type"] = "application/json"
    return response

@app.route("/exceptions/csv")
def exceptions_csv():
    data = StringIO()
    writer = csv.writer(data)
    writer.writerow(["Count", "Message", "Traceback", "Nodes"])
    for exc in six.itervalues(runners.main.exceptions):
        nodes = ", ".join(exc["nodes"])
        writer.writerow([exc["count"], exc["msg"], exc["traceback"], nodes])

    data.seek(0)
    response = make_response(data.read())
    file_name = "exceptions_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response

def start(locust, options):
    pywsgi.WSGIServer((options.web_host, options.web_port),
                      app, log=None).serve_forever()
