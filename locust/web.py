import json
import os.path
from gevent import wsgi
from locust.stats import RequestStats

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
            '"Reqests/s"',
        ])
    ]
    
    for s in list(locust_runner.request_stats.itervalues()) + [RequestStats.sum_stats("Total")]:
        rows.append('"%s",%i,%i,%i,%i,%i,%i,%.2f' % (
            s.name,
            s.num_reqs,
            s.num_failures,
            s.median_response_time,
            s.avg_response_time,
            s.min_response_time or 0,
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
    for s in list(locust_runner.request_stats.itervalues()) + [RequestStats.sum_stats("Total")]:
        rows.append(s.percentile(tpl='"%s",%i,%i,%i,%i,%i,%i,%i,%i,%i,%i'))
    
    response = make_response("\n".join(rows))
    response.headers["Content-type"] = "text/csv"
    return response

@app.route('/stats/requests')
def request_stats():
    from core import locust_runner
    
    stats = []
    for s in list(locust_runner.request_stats.itervalues()) + [RequestStats.sum_stats("Total")]:
        stats.append({
            "name": s.name,
            "num_reqs": s.num_reqs,
            "num_failures": s.num_failures,
            "avg_response_time": s.avg_response_time,
            "min_response_time": s.min_response_time,
            "max_response_time": s.max_response_time,
            "current_rps": s.current_rps,
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
