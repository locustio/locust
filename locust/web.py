# -*- coding: utf-8 -*-

import csv
import json
import logging
import os.path
from collections import defaultdict
from itertools import chain
from time import time

try:
    # >= Py3.2
    from html import escape
except ImportError:
    # < Py3.2
    from cgi import escape

from flask import Flask, make_response, jsonify, render_template, request
from gevent import pywsgi

from locust import __version__ as version
from io import StringIO

from . import runners
from .runners import MasterLocustRunner
from .stats import failures_csv, median_from_dict, requests_csv, sort_stats, stats_history_csv
from .util.cache import memoize
from .util.rounding import proper_round
from .util.timespan import parse_timespan

logger = logging.getLogger(__name__)

DEFAULT_CACHE_TIME = 2.0



class WebUI:
    server = None
    """Refernce to pyqsgi.WSGIServer once it's started"""
    
    def __init__(self, environment):
        environment.web_ui = self
        self.environment = environment
        app = Flask(__name__)
        self.app = app
        app.debug = True
        app.root_path = os.path.dirname(os.path.abspath(__file__))
        
        @app.route('/')
        def index():
            if not environment.runner:
                return make_response("Error: Locust Environment does not have any runner", 500)
            
            is_distributed = isinstance(environment.runner, MasterLocustRunner)
            if is_distributed:
                worker_count = environment.runner.worker_count
            else:
                worker_count = 0
            
            override_host_warning = False
            if environment.host:
                host = environment.host
            elif environment.runner.locust_classes:
                all_hosts = set([l.host for l in environment.runner.locust_classes])
                if len(all_hosts) == 1:
                    host = list(all_hosts)[0]
                else:
                    # since we have mulitple Locust classes with different host attributes, we'll
                    # inform that specifying host will override the host for all Locust classes
                    override_host_warning = True
                    host = None
            else:
                host = None
            
            return render_template("index.html",
                state=environment.runner.state,
                is_distributed=is_distributed,
                user_count=environment.runner.user_count,
                version=version,
                host=host,
                override_host_warning=override_host_warning,
                worker_count=worker_count,
                is_step_load=environment.step_load,
            )
        
        @app.route('/swarm', methods=["POST"])
        def swarm():
            assert request.method == "POST"
            locust_count = int(request.form["locust_count"])
            hatch_rate = float(request.form["hatch_rate"])
            if (request.form.get("host")):
                environment.host = str(request.form["host"])
        
            if environment.step_load:
                step_locust_count = int(request.form["step_locust_count"])
                step_duration = parse_timespan(str(request.form["step_duration"]))
                environment.runner.start_stepload(locust_count, hatch_rate, step_locust_count, step_duration)
                return jsonify({'success': True, 'message': 'Swarming started in Step Load Mode', 'host': environment.host})
            
            environment.runner.start(locust_count, hatch_rate)
            return jsonify({'success': True, 'message': 'Swarming started', 'host': environment.host})
        
        @app.route('/stop')
        def stop():
            environment.runner.stop()
            return jsonify({'success':True, 'message': 'Test stopped'})
        
        @app.route("/stats/reset")
        def reset_stats():
            environment.runner.stats.reset_all()
            environment.runner.exceptions = {}
            return "ok"
            
        @app.route("/stats/requests/csv")
        def request_stats_csv():
            response = make_response(requests_csv(self.environment.runner.stats))
            file_name = "requests_{0}.csv".format(time())
            disposition = "attachment;filename={0}".format(file_name)
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response
        
        @app.route("/stats/stats_history/csv")
        def stats_history_stats_csv():
            response = make_response(stats_history_csv(self.environment.runner.stats, False, True))
            file_name = "stats_history_{0}.csv".format(time())
            disposition = "attachment;filename={0}".format(file_name)
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response
        
        @app.route("/stats/failures/csv")
        def failures_stats_csv():
            response = make_response(failures_csv(self.environment.runner.stats))
            file_name = "failures_{0}.csv".format(time())
            disposition = "attachment;filename={0}".format(file_name)
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response
        
        @app.route('/stats/requests')
        @memoize(timeout=DEFAULT_CACHE_TIME, dynamic_timeout=True)
        def request_stats():
            stats = []
        
            for s in chain(sort_stats(self.environment.runner.stats.entries), [environment.runner.stats.total]):
                stats.append({
                    "method": s.method,
                    "name": s.name,
                    "safe_name": escape(s.name, quote=False),
                    "num_requests": s.num_requests,
                    "num_failures": s.num_failures,
                    "avg_response_time": s.avg_response_time,
                    "min_response_time": 0 if s.min_response_time is None else proper_round(s.min_response_time),
                    "max_response_time": proper_round(s.max_response_time),
                    "current_rps": s.current_rps,
                    "current_fail_per_sec": s.current_fail_per_sec,
                    "median_response_time": s.median_response_time,
                    "ninetieth_response_time": s.get_response_time_percentile(0.9),
                    "avg_content_length": s.avg_content_length,
                })
            
            errors = []
            for e in environment.runner.errors.values():
                err_dict = e.to_dict()
                err_dict["name"] = escape(err_dict["name"])
                err_dict["error"] = escape(err_dict["error"])
                errors.append(err_dict)

            # Truncate the total number of stats and errors displayed since a large number of rows will cause the app
            # to render extremely slowly. Aggregate stats should be preserved.
            report = {"stats": stats[:500], "errors": errors[:500]}
            if len(stats) > 500:
                report["stats"] += [stats[-1]]
        
            if stats:
                report["total_rps"] = stats[len(stats)-1]["current_rps"]
                report["fail_ratio"] = environment.runner.stats.total.fail_ratio
                report["current_response_time_percentile_95"] = environment.runner.stats.total.get_current_response_time_percentile(0.95)
                report["current_response_time_percentile_50"] = environment.runner.stats.total.get_current_response_time_percentile(0.5)
            
            is_distributed = isinstance(environment.runner, MasterLocustRunner)
            if is_distributed:
                workers = []
                for worker in environment.runner.clients.values():
                    workers.append({"id":worker.id, "state":worker.state, "user_count": worker.user_count, "cpu_usage":worker.cpu_usage})
        
                report["workers"] = workers
            
            report["state"] = environment.runner.state
            report["user_count"] = environment.runner.user_count
        
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
                    } for row in environment.runner.exceptions.values()
                ]
            })
        
        @app.route("/exceptions/csv")
        def exceptions_csv():
            data = StringIO()
            writer = csv.writer(data)
            writer.writerow(["Count", "Message", "Traceback", "Nodes"])
            for exc in environment.runner.exceptions.values():
                nodes = ", ".join(exc["nodes"])
                writer.writerow([exc["count"], exc["msg"], exc["traceback"], nodes])
            
            data.seek(0)
            response = make_response(data.read())
            file_name = "exceptions_{0}.csv".format(time())
            disposition = "attachment;filename={0}".format(file_name)
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response

    def start(self, host, port):
        self.server = pywsgi.WSGIServer((host, port), self.app, log=None)
        self.server.serve_forever()
    
    def stop(self):
        self.server.stop()
