# encoding: utf-8

import json
import os.path
from time import time
from gevent import wsgi
from locust.stats import RequestStats
from locust import version

from flask import Flask, make_response, request, render_template

DEFAULT_CACHE_TIME = 2.0

app = Flask("Locust Monitor")
app.debug = True
app.root_path = os.path.dirname(os.path.abspath(__file__))

_locust = None
_num_clients = None
_num_requests = None
_hatch_rate = None
_request_stats_context_cache = {}


@app.route('/')
def index():
    from core import locust_runner, MasterLocustRunner
    is_distributed = isinstance(locust_runner, MasterLocustRunner)
    if is_distributed:
        slave_count = locust_runner.slave_count
    else:
        slave_count = 0
    
    return render_template("index.html",
        state=locust_runner.state,
        is_distributed=is_distributed,
        slave_count=slave_count,
        user_count=locust_runner.user_count,
        version=version
    )

@app.route('/swarm', methods=["POST"])
def swarm():
    assert request.method == "POST"
    from core import locust_runner

    locust_count = int(request.form["locust_count"])
    hatch_rate = float(request.form["hatch_rate"])
    locust_runner.start_hatching(locust_count, hatch_rate)
    response = make_response(json.dumps({'success':True, 'message': 'Swarming started'}))
    response.headers["Content-type"] = "application/json"
    return response

@app.route('/stop')
def stop():
    from core import locust_runner
    locust_runner.stop()
    response = make_response(json.dumps({'success':True, 'message': 'Test stopped'}))
    response.headers["Content-type"] = "application/json"
    return response

@app.route("/stats/reset")
def reset_stats():
    RequestStats.reset_all()
    
@app.route("/stats/requests/csv")
def request_stats_csv():
    from core import locust_runner
    
    rows = [
        ",".join([
            '"Name"',
            '"# requests"',
            '"# failures"',
            '"Median response time"',
            '"Average response time"',
            '"Min response time"', 
            '"Max response time"',
            '"Average Content-Length"',
            '"Reqests/s"',
        ])
    ]
    
    for s in _sort_stats(locust_runner.request_stats) + [RequestStats.sum_stats("Total")]:
        rows.append('"%s",%i,%i,%i,%i,%i,%i,%i,%.2f' % (
            s.name,
            s.num_reqs,
            s.num_failures,
            s.median_response_time,
            s.avg_response_time,
            s.min_response_time or 0,
            s.avg_content_length,
            s.max_response_time,
            s.total_rps,
        ))
    
    response = make_response("\n".join(rows))
    response.headers["Content-type"] = "text/csv"
    return response

@app.route("/stats/distribution/csv")
def distribution_stats_csv():
    from core import locust_runner
    
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
    for s in _sort_stats(locust_runner.request_stats) + [RequestStats.sum_stats("Total")]:
        rows.append(s.percentile(tpl='"%s",%i,%i,%i,%i,%i,%i,%i,%i,%i,%i'))
    
    response = make_response("\n".join(rows))
    response.headers["Content-type"] = "text/csv"
    return response

@app.route('/stats/requests')
def request_stats():
    global _request_stats_context_cache
    from core import locust_runner, MasterLocustRunner
    
    if not _request_stats_context_cache or _request_stats_context_cache["last_time"] < time() - _request_stats_context_cache.get("cache_time", DEFAULT_CACHE_TIME):
        cache_time = _request_stats_context_cache.get("cache_time", DEFAULT_CACHE_TIME)
        now = time()
        stats = []
        for s in _sort_stats(locust_runner.request_stats) + [RequestStats.sum_stats("Total")]:
            stats.append({
                "name": s.name,
                "num_reqs": s.num_reqs,
                "num_failures": s.num_failures,
                "avg_response_time": s.avg_response_time,
                "min_response_time": s.min_response_time,
                "max_response_time": s.max_response_time,
                "current_rps": s.current_rps,
                "median_response_time": s.median_response_time,
                "avg_content_length": s.avg_content_length,
            })
        
        report = {"stats":stats, "errors":list(locust_runner.errors.iteritems())}
        if stats:
            report["total_rps"] = stats[len(stats)-1]["current_rps"]
            try:
                report["fail_ratio"] = float(stats[len(stats)-1]["num_failures"]) / stats[len(stats)-1]["num_reqs"]
            except ZeroDivisionError:
                if stats[len(stats)-1]["num_failures"] > 0:
                    report["fail_ratio"] = 100
                else:
                    report["fail_ratio"] = 0
        
        is_distributed = isinstance(locust_runner, MasterLocustRunner)
        if is_distributed:
            report["slave_count"] = locust_runner.slave_count
        
        report["state"] = locust_runner.state
        report["user_count"] = locust_runner.user_count

        elapsed = time() - now
        cache_time = max(cache_time, elapsed * 2.0) # Increase cache_time when report generating starts to take longer time
        _request_stats_context_cache = {"last_time": elapsed - now, "report": report, "cache_time": cache_time}
    else:
        report = _request_stats_context_cache["report"]
    return json.dumps(report)

def start(locust, hatch_rate, num_clients, num_requests):
    global _locust, _hatch_rate, _num_clients, _num_requests
    _locust = locust
    _hatch_rate = hatch_rate
    _num_clients = num_clients
    _num_requests = num_requests
    wsgi.WSGIServer(('', 8089), app, log=None).serve_forever()

def _sort_stats(stats):
    return [stats[key] for key in sorted(stats.iterkeys())]
