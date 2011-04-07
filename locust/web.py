import json
import os.path
from gevent import wsgi

from flask import Flask, make_response, request
app = Flask("Locust Monitor")
app.debug = True
app.root_path = os.path.dirname(__file__)

_locust = None
_num_clients = None
_num_requests = None
_hatch_rate = None

@app.route('/')
def index():
    response = make_response(open(os.path.join(app.root_path, "static", "index.html")).read())
    response.headers["Content-type"] = "text/html"
    return response

@app.route('/swarm', methods=["POST"])
def swarm():
    assert request.method == "POST"
    from core import locust_runner
    
    locust_count = int(request.form["locust_count"])
    locust_runner.start_hatching(locust_count=locust_count)
    return json.dumps({'message': 'Swarming started'})

@app.route('/stats/requests')
def request_stats():
    from core import locust_runner
    stats = []
    
    total_requests = 0
    total_rps = 0
    total_fails = 0
    
    for s in locust_runner.request_stats.itervalues():
        total_requests += s.num_reqs
        total_rps += s.reqs_per_sec
        total_fails += s.num_failures
        
        stats.append({
            "name": s.name,
            "num_reqs": s.num_reqs,
            "num_failures": s.num_failures,
            "avg_response_time": s.avg_response_time,
            "min_response_time": s.min_response_time,
            "max_response_time": s.max_response_time,
            "reqs_per_sec": s.reqs_per_sec,
        })
    stats.append({
        "name": "Total",
        "num_reqs": total_requests,
        "num_failures": total_fails,
        "avg_response_time": "",
        "min_response_time": "",
        "max_response_time": "",
        "reqs_per_sec": round(total_rps, 2),
    })
    
    report = {"stats":stats, "errors":list(locust_runner.errors.iteritems())}
    return json.dumps(report)

def start(locust, hatch_rate, num_clients, num_requests):
    global _locust, _hatch_rate, _num_clients, _num_requests
    _locust = locust
    _hatch_rate = hatch_rate
    _num_clients = num_clients
    _num_requests = num_requests
    wsgi.WSGIServer(('', 8089), app, log=None).serve_forever()
