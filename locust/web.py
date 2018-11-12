# -*- coding: utf-8 -*-

import csv
import json
import logging
import os.path
from collections import defaultdict
from itertools import chain
from time import time

import six
from flask import Flask, make_response, jsonify, render_template, request
from gevent import pywsgi

from locust import __version__ as version
from six.moves import StringIO, xrange

from . import runners
from .runners import MasterLocustRunner
from .stats import distribution_csv, median_from_dict, requests_csv, sort_stats, request_json
from .util.cache import memoize

logger = logging.getLogger(__name__)

DEFAULT_CACHE_TIME = 2.0

app = Flask(__name__)
app.debug = True
app.root_path = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def index():
    is_distributed = isinstance(runners.locust_runner, MasterLocustRunner)
    if is_distributed:
        slave_count = runners.locust_runner.slave_count
    else:
        slave_count = 0

    if runners.locust_runner.host:
        host = runners.locust_runner.host
    elif len(runners.locust_runner.locust_classes) > 0:
        host = runners.locust_runner.locust_classes[0].host
    else:
        host = None
    
    return render_template("index.html",
        state=runners.locust_runner.state,
        is_distributed=is_distributed,
        user_count=runners.locust_runner.user_count,
        version=version,
        host=host
    )

@app.route('/swarm', methods=["POST"])
def swarm():
    assert request.method == "POST"

    locust_count = int(request.form["locust_count"])
    hatch_rate = float(request.form["hatch_rate"])
    runners.locust_runner.start_hatching(locust_count, hatch_rate)
    return jsonify({'success': True, 'message': 'Swarming started'})

@app.route('/stop')
def stop():
    runners.locust_runner.stop()
    return jsonify({'success':True, 'message': 'Test stopped'})

@app.route("/stats/reset")
def reset_stats():
    runners.locust_runner.stats.reset_all()
    return "ok"
    
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
    report = request_json()
    return jsonify(report)

@app.route("/exceptions")
def exceptions():
    return jsonify({
        'exceptions': [
            {
                "count": row["count"],
                "msg": row["msg"],
                "traceback": row["traceback"],
                "nodes" : ", ".join(row["nodes"])
            } for row in six.itervalues(runners.locust_runner.exceptions)
        ]
    })

@app.route("/exceptions/csv")
def exceptions_csv():
    data = StringIO()
    writer = csv.writer(data)
    writer.writerow(["Count", "Message", "Traceback", "Nodes"])
    for exc in six.itervalues(runners.locust_runner.exceptions):
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
    pywsgi.WSGIServer((options.web_host, options.port),
                      app, log=None).serve_forever()
