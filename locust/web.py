# encoding: utf-8

import json
import os.path
from time import time
from itertools import chain
from collections import defaultdict

from gevent import wsgi
from flask import Flask, make_response, request, render_template

import runners
from runners import MasterLocustRunner
from locust.stats import median_from_dict
from locust import version
import gevent

import logging
logger = logging.getLogger(__name__)

DEFAULT_CACHE_TIME = 2.0

app = Flask(__name__)
app.debug = True
app.root_path = os.path.dirname(os.path.abspath(__file__))

_request_stats_context_cache = {}
_ramp = False

@app.route('/')
def index():
    is_distributed = isinstance(runners.locust_runner, MasterLocustRunner)
    if is_distributed:
        slave_count = runners.locust_runner.slave_count
    else:
        slave_count = 0
    
    return render_template("index.html",
        state=runners.locust_runner.state,
        is_distributed=is_distributed,
        slave_count=slave_count,
        user_count=runners.locust_runner.user_count,
        ramp = _ramp,
        version=version
    )

@app.route('/swarm', methods=["POST"])
def swarm():
    assert request.method == "POST"

    locust_count = int(request.form["locust_count"])
    hatch_rate = float(request.form["hatch_rate"])
    runners.locust_runner.start_hatching(locust_count, hatch_rate)
    response = make_response(json.dumps({'success':True, 'message': 'Swarming started'}))
    response.headers["Content-type"] = "application/json"
    return response

@app.route('/stop')
def stop():
    runners.locust_runner.stop()
    response = make_response(json.dumps({'success':True, 'message': 'Test stopped'}))
    response.headers["Content-type"] = "application/json"
    return response

@app.route("/ramp", methods=["POST"])
def ramp():
    from ramping import start_ramping
    
    init_clients = int(request.form["init_count"])
    hatch_rate = int(request.form["hatch_rate"])
    hatch_stride = int(request.form["hatch_stride"])
    precision = int(request.form["precision"])
    max_clients = int(request.form["max_count"])
    response_time = int(request.form["response_time"])
    percentile = float(int(request.form["percentile"]) / 100.0)
    fail_rate = float(int(request.form["fail_rate"]) / 100.0)
    calibration_time = int(request.form["wait_time"])
    gevent.spawn(start_ramping, hatch_rate, max_clients, hatch_stride, percentile, response_time, fail_rate, precision, init_clients, calibration_time)
    response = make_response(json.dumps({'success':True, 'message': 'Ramping started'}))
    response.headers["Content-type"] = "application/json"
    return response

@app.route("/stats/reset")
def reset_stats():
    runners.locust_runner.stats.reset_all()
    return "ok"
    
@app.route("/stats/requests/csv")
def request_stats_csv():
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
    
    for s in chain(_sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.aggregated_stats("Total", full_request_history=True)]):
        rows.append('"%s","%s",%i,%i,%i,%i,%i,%i,%i,%.2f' % (
            s.key[0],
            s.key[1],
            s.num_items,
            s.num_failures,
            s.median_time,
            s.avg_time,
            s.min_time or 0,
            s.max_time,
            s.avg_content_length,
            s.total_per_sec,
        ))

    response = make_response("\n".join(rows))
    file_name = "requests_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response

@app.route("/stats/distribution/csv")
def distribution_stats_csv():
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
    for s in chain(_sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.aggregated_stats("Total", full_request_history=True)]):
        if s.num_items:
            rows.append(s.percentile(tpl='"%s",%i,%i,%i,%i,%i,%i,%i,%i,%i,%i'))
        else:
            rows.append('"%s",0,"N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"' % s.name)

    response = make_response("\n".join(rows))
    file_name = "distribution_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response

@app.route('/stats/requests')
def request_stats():
    global _request_stats_context_cache
    
    if not _request_stats_context_cache or _request_stats_context_cache["last_time"] < time() - _request_stats_context_cache.get("cache_time", DEFAULT_CACHE_TIME):
        cache_time = _request_stats_context_cache.get("cache_time", DEFAULT_CACHE_TIME)
        now = time()
        
        stats = []
        for s in chain(_sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.aggregated_stats("Total")]):
            stats.append({
                "key": s.key,
                "num_items": s.num_items,
                "num_failures": s.num_failures,
                "avg_time": s.avg_time,
                "min_time": s.min_time,
                "max_time": s.max_time,
                "current_per_sec": s.current_per_sec,
                "median_time": s.median_time,
                "avg_content_length": s.avg_content_length,
            })
        
        report = {"stats":stats, "errors":[e.to_dict() for e in runners.locust_runner.errors.itervalues()]}
        if stats:
            report["total_per_sec"] = stats[len(stats)-1]["current_per_sec"]
            report["fail_ratio"] = runners.locust_runner.stats.aggregated_stats("Total").fail_ratio
            
            # since generating a total response times dict with all response times from all
            # urls is slow, we make a new total response time dict which will consist of one
            # entry per url with the median response time as key and the number of requests as
            # value
            response_times = defaultdict(int) # used for calculating total median
            for i in xrange(len(stats)-1):
                response_times[stats[i]["median_time"]] += stats[i]["num_items"]
            
            # calculate total median
            stats[len(stats)-1]["median_time"] = median_from_dict(stats[len(stats)-1]["num_items"], response_times)
        
        is_distributed = isinstance(runners.locust_runner, MasterLocustRunner)
        if is_distributed:
            report["slave_count"] = runners.locust_runner.slave_count
        
        report["state"] = runners.locust_runner.state
        report["user_count"] = runners.locust_runner.user_count

        elapsed = time() - now
        cache_time = max(cache_time, elapsed * 2.0) # Increase cache_time when report generating starts to take longer time
        _request_stats_context_cache = {"last_time": elapsed - now, "report": report, "cache_time": cache_time}
    else:
        report = _request_stats_context_cache["report"]
    return json.dumps(report)

@app.route("/exceptions")
def exceptions():
    response = make_response(json.dumps({'exceptions': [{"count": row["count"], "msg": row["msg"], "traceback": row["traceback"], "nodes" : ", ".join(row["nodes"])} for row in runners.locust_runner.exceptions.itervalues()]}))
    response.headers["Content-type"] = "application/json"
    return response

def start(locust, hatch_rate, num_clients, num_requests, ramp, port):
    global _ramp
    _ramp = ramp
    
    wsgi.WSGIServer(('', port), app, log=None).serve_forever()

def _sort_stats(stats):
    return [stats[key] for key in sorted(stats.iterkeys())]
