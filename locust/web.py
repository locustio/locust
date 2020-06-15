# -*- coding: utf-8 -*-

import csv
import logging
import os.path
from functools import wraps
from html import escape
from io import StringIO
from itertools import chain
from time import time

import gevent
from flask import Flask, make_response, jsonify, render_template, request
from flask_basicauth import BasicAuth
from gevent import pywsgi

from locust import __version__ as version
from .exception import AuthCredentialsError
from .runners import MasterRunner
from .log import greenlet_exception_logger
from .stats import failures_csv, requests_csv, sort_stats
from .util.cache import memoize
from .util.rounding import proper_round
from .util.timespan import parse_timespan


logger = logging.getLogger(__name__)
greenlet_exception_handler = greenlet_exception_logger(logger)

DEFAULT_CACHE_TIME = 2.0


class WebUI:
    """
    Sets up and runs a Flask web app that can start and stop load tests using the 
    :attr:`environment.runner <locust.env.Environment.runner>` as well as show the load test statistics 
    in :attr:`environment.stats <locust.env.Environment.stats>`
    """
    
    app = None
    """
    Reference to the :class:`flask.Flask` app. Can be used to add additional web routes and customize
    the Flask app in other various ways. Example::
    
        from flask import request
        
        @web_ui.app.route("/my_custom_route")
        def my_custom_route():
            return "your IP is: %s" % request.remote_addr
    """
    
    greenlet = None
    """
    Greenlet of the running web server
    """
    
    server = None
    """Reference to the :class:`pyqsgi.WSGIServer` instance"""
    
    def __init__(self, environment, host, port, auth_credentials=None, tls_cert=None, tls_key=None):
        """
        Create WebUI instance and start running the web server in a separate greenlet (self.greenlet)
        
        Arguments:
        environment: Reference to the curren Locust Environment
        host: Host/interface that the web server should accept connections to
        port: Port that the web server should listen to
        auth_credentials:  If provided, it will enable basic auth with all the routes protected by default.
                           Should be supplied in the format: "user:pass".
        tls_cert: A path to a TLS certificate
        tls_key: A path to a TLS private key
        """
        environment.web_ui = self
        self.environment = environment
        self.host = host
        self.port = port
        self.tls_cert = tls_cert
        self.tls_key = tls_key
        app = Flask(__name__)
        self.app = app
        app.debug = True
        app.root_path = os.path.dirname(os.path.abspath(__file__))
        self.app.config["BASIC_AUTH_ENABLED"] = False
        self.auth = None
        self.greenlet = None

        if auth_credentials is not None:
            credentials = auth_credentials.split(':')
            if len(credentials) == 2:
                self.app.config["BASIC_AUTH_USERNAME"] = credentials[0]
                self.app.config["BASIC_AUTH_PASSWORD"] = credentials[1]
                self.app.config["BASIC_AUTH_ENABLED"] = True
                self.auth = BasicAuth()
                self.auth.init_app(self.app)
            else:
                raise AuthCredentialsError("Invalid auth_credentials. It should be a string in the following format: 'user.pass'")

        @app.route('/')
        @self.auth_required_if_enabled
        def index():
            if not environment.runner:
                return make_response("Error: Locust Environment does not have any runner", 500)
            
            is_distributed = isinstance(environment.runner, MasterRunner)
            if is_distributed:
                worker_count = environment.runner.worker_count
            else:
                worker_count = 0
            
            override_host_warning = False
            if environment.host:
                host = environment.host
            elif environment.runner.user_classes:
                all_hosts = set([l.host for l in environment.runner.user_classes])
                if len(all_hosts) == 1:
                    host = list(all_hosts)[0]
                else:
                    # since we have mulitple User classes with different host attributes, we'll
                    # inform that specifying host will override the host for all User classes
                    override_host_warning = True
                    host = None
            else:
                host = None
            
            options = environment.parsed_options
            return render_template("index.html",
                state=environment.runner.state,
                is_distributed=is_distributed,
                user_count=environment.runner.user_count,
                version=version,
                host=host,
                override_host_warning=override_host_warning,
                num_users=options and options.num_users,
                hatch_rate=options and options.hatch_rate,
                step_users=options and options.step_users,
                step_time=options and options.step_time,
                worker_count=worker_count,
                is_step_load=environment.step_load,
            )
        
        @app.route('/swarm', methods=["POST"])
        @self.auth_required_if_enabled
        def swarm():
            assert request.method == "POST"
            user_count = int(request.form["user_count"])
            hatch_rate = float(request.form["hatch_rate"])
            if (request.form.get("host")):
                environment.host = str(request.form["host"])
        
            if environment.step_load:
                step_user_count = int(request.form["step_user_count"])
                step_duration = parse_timespan(str(request.form["step_duration"]))
                environment.runner.start_stepload(user_count, hatch_rate, step_user_count, step_duration)
                return jsonify({'success': True, 'message': 'Swarming started in Step Load Mode', 'host': environment.host})
            
            environment.runner.start(user_count, hatch_rate)
            return jsonify({'success': True, 'message': 'Swarming started', 'host': environment.host})
        
        @app.route('/stop')
        @self.auth_required_if_enabled
        def stop():
            environment.runner.stop()
            return jsonify({'success':True, 'message': 'Test stopped'})
        
        @app.route("/stats/reset")
        @self.auth_required_if_enabled
        def reset_stats():
            environment.runner.stats.reset_all()
            environment.runner.exceptions = {}
            return "ok"
            
        @app.route("/stats/requests/csv")
        @self.auth_required_if_enabled
        def request_stats_csv():
            data = StringIO()
            writer = csv.writer(data)
            requests_csv(self.environment.runner.stats, writer)
            response = make_response(data.getvalue())
            file_name = "requests_{0}.csv".format(time())
            disposition = "attachment;filename={0}".format(file_name)
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response
        
        @app.route("/stats/failures/csv")
        @self.auth_required_if_enabled
        def failures_stats_csv():
            data = StringIO()
            writer = csv.writer(data)
            failures_csv(self.environment.runner.stats, writer)
            response = make_response(data.getvalue())
            file_name = "failures_{0}.csv".format(time())
            disposition = "attachment;filename={0}".format(file_name)
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response
        
        @app.route('/stats/requests')
        @self.auth_required_if_enabled
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
            
            is_distributed = isinstance(environment.runner, MasterRunner)
            if is_distributed:
                workers = []
                for worker in environment.runner.clients.values():
                    workers.append({"id":worker.id, "state":worker.state, "user_count": worker.user_count, "cpu_usage":worker.cpu_usage})
        
                report["workers"] = workers
            
            report["state"] = environment.runner.state
            report["user_count"] = environment.runner.user_count
        
            return jsonify(report)
        
        @app.route("/exceptions")
        @self.auth_required_if_enabled
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
        @self.auth_required_if_enabled
        def exceptions_csv():
            data = StringIO()
            writer = csv.writer(data)
            writer.writerow(["Count", "Message", "Traceback", "Nodes"])
            for exc in environment.runner.exceptions.values():
                nodes = ", ".join(exc["nodes"])
                writer.writerow([exc["count"], exc["msg"], exc["traceback"], nodes])

            response = make_response(data.getvalue())
            file_name = "exceptions_{0}.csv".format(time())
            disposition = "attachment;filename={0}".format(file_name)
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response
        
        # start the web server
        self.greenlet = gevent.spawn(self.start)
        self.greenlet.link_exception(greenlet_exception_handler)

    def start(self):
        if self.tls_cert and self.tls_key:
            self.server = pywsgi.WSGIServer((self.host, self.port), self.app, log=None, keyfile=self.tls_key, certfile=self.tls_cert)
        else:
            self.server = pywsgi.WSGIServer((self.host, self.port), self.app, log=None)
        self.server.serve_forever()
    
    def stop(self):
        """
        Stop the running web server
        """
        self.server.stop()

    def auth_required_if_enabled(self, view_func):
        """
        Decorator that can be used on custom route methods that will turn on Basic Auth 
        authentication if the ``--web-auth`` flag is used. Example::
        
            @web_ui.app.route("/my_custom_route")
            @web_ui.auth_required_if_enabled
            def my_custom_route():
                return "custom response"
        """
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if self.app.config["BASIC_AUTH_ENABLED"]:
                if self.auth.authenticate():
                    return view_func(*args, **kwargs)
                else:
                    return self.auth.challenge()
            else:
                return view_func(*args, **kwargs)

        return wrapper
