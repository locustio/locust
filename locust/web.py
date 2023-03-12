from __future__ import annotations
import csv
import logging
import os.path
from functools import wraps

from html import escape
from io import StringIO
from json import dumps
from itertools import chain
from time import time
from typing import TYPE_CHECKING, Optional, Any, Dict, List

import gevent
from flask import Flask, make_response, jsonify, render_template, request, send_file, Response
from flask_basicauth import BasicAuth
from gevent import pywsgi

from .exception import AuthCredentialsError
from .runners import MasterRunner, STATE_RUNNING, STATE_MISSING
from .log import greenlet_exception_logger
from .stats import StatsCSVFileWriter, StatsErrorDict, sort_stats
from . import stats as stats_module, __version__ as version, argument_parser
from .stats import StatsCSV
from .user.inspectuser import get_ratio
from .util.cache import memoize
from .util.rounding import proper_round
from .util.timespan import parse_timespan
from .html import get_html_report
from flask_cors import CORS

if TYPE_CHECKING:
    from .env import Environment


logger = logging.getLogger(__name__)
greenlet_exception_handler = greenlet_exception_logger(logger)

DEFAULT_CACHE_TIME = 2.0


class WebUI:
    """
    Sets up and runs a Flask web app that can start and stop load tests using the
    :attr:`environment.runner <locust.env.Environment.runner>` as well as show the load test statistics
    in :attr:`environment.stats <locust.env.Environment.stats>`
    """

    app: Optional[Flask] = None
    """
    Reference to the :class:`flask.Flask` app. Can be used to add additional web routes and customize
    the Flask app in other various ways. Example::

        from flask import request

        @web_ui.app.route("/my_custom_route")
        def my_custom_route():
            return "your IP is: %s" % request.remote_addr
    """

    greenlet: Optional[gevent.Greenlet] = None
    """
    Greenlet of the running web server
    """

    server: Optional[pywsgi.WSGIServer] = None
    """Reference to the :class:`pyqsgi.WSGIServer` instance"""

    template_args: Dict[str, Any]
    """Arguments used to render index.html for the web UI. Must be used with custom templates
    extending index.html."""

    def __init__(
        self,
        environment: "Environment",
        host: str,
        port: int,
        auth_credentials: Optional[str] = None,
        tls_cert: Optional[str] = None,
        tls_key: Optional[str] = None,
        stats_csv_writer: Optional[StatsCSV] = None,
        delayed_start=False,
        userclass_picker_is_active=False,
    ):
        """
        Create WebUI instance and start running the web server in a separate greenlet (self.greenlet)

        Arguments:
        environment: Reference to the current Locust Environment
        host: Host/interface that the web server should accept connections to
        port: Port that the web server should listen to
        auth_credentials:  If provided, it will enable basic auth with all the routes protected by default.
                           Should be supplied in the format: "user:pass".
        tls_cert: A path to a TLS certificate
        tls_key: A path to a TLS private key
        delayed_start: Whether or not to delay starting web UI until `start()` is called. Delaying web UI start
                       allows for adding Flask routes or Blueprints before accepting requests, avoiding errors.
        """
        environment.web_ui = self
        self.stats_csv_writer = stats_csv_writer or StatsCSV(environment, stats_module.PERCENTILES_TO_REPORT)
        self.environment = environment
        self.host = host
        self.port = port
        self.tls_cert = tls_cert
        self.tls_key = tls_key
        self.userclass_picker_is_active = userclass_picker_is_active
        app = Flask(__name__)
        CORS(app)
        self.app = app
        app.jinja_env.add_extension("jinja2.ext.do")
        app.debug = True
        app.root_path = os.path.dirname(os.path.abspath(__file__))
        self.app.config["BASIC_AUTH_ENABLED"] = False
        self.auth: Optional[BasicAuth] = None
        self.greenlet: Optional[gevent.Greenlet] = None
        self._swarm_greenlet: Optional[gevent.Greenlet] = None
        self.template_args = {}

        if auth_credentials is not None:
            credentials = auth_credentials.split(":")
            if len(credentials) == 2:
                self.app.config["BASIC_AUTH_USERNAME"] = credentials[0]
                self.app.config["BASIC_AUTH_PASSWORD"] = credentials[1]
                self.app.config["BASIC_AUTH_ENABLED"] = True
                self.auth = BasicAuth()
                self.auth.init_app(self.app)
            else:
                raise AuthCredentialsError(
                    "Invalid auth_credentials. It should be a string in the following format: 'user:pass'"
                )
        if environment.runner:
            self.update_template_args()
        if not delayed_start:
            self.start()

        @app.route("/")
        @self.auth_required_if_enabled
        def index() -> str | Response:
            if not environment.runner:
                return make_response("Error: Locust Environment does not have any runner", 500)
            self.update_template_args()
            return render_template("index.html", **self.template_args)

        @app.route("/swarm", methods=["POST"])
        @self.auth_required_if_enabled
        def swarm() -> Response:
            assert request.method == "POST"

            # Loading UserClasses & ShapeClasses if Locust is running with UserClass Picker
            if self.userclass_picker_is_active:
                if not self.environment.available_user_classes:
                    err_msg = "UserClass picker is active but there are no available UserClasses"
                    return jsonify({"success": False, "message": err_msg, "host": environment.host})

                # Getting Specified User Classes
                form_data_user_class_names = request.form.getlist("user_classes")

                # Updating UserClasses
                if form_data_user_class_names:
                    user_classes = {}
                    for user_class_name, user_class_object in self.environment.available_user_classes.items():
                        if user_class_name in form_data_user_class_names:
                            user_classes[user_class_name] = user_class_object

                else:
                    if self.environment.runner and self.environment.runner.state == STATE_RUNNING:
                        # Test is already running
                        # Using the user classes that have already been selected
                        user_classes = {
                            key: value
                            for (key, value) in self.environment.available_user_classes.items()
                            if value in self.environment.user_classes
                        }
                    else:
                        # Starting test with no user class selection
                        # Defaulting to using all available user classes
                        user_classes = self.environment.available_user_classes

                self._update_user_classes(user_classes)

                # Updating ShapeClass if specified in WebUI Form
                form_data_shape_class_name = request.form.get("shape_class", "Default")
                if form_data_shape_class_name == "Default":
                    self._update_shape_class(None)
                else:
                    self._update_shape_class(form_data_shape_class_name)

            parsed_options_dict = vars(environment.parsed_options) if environment.parsed_options else {}
            run_time = None
            for key, value in request.form.items():
                if key == "user_count":  # if we just renamed this field to "users" we wouldn't need this
                    user_count = int(value)
                elif key == "spawn_rate":
                    spawn_rate = float(value)
                elif key == "host":
                    # Replace < > to guard against XSS
                    environment.host = str(request.form["host"]).replace("<", "").replace(">", "")
                elif key == "user_classes":
                    # Set environment.parsed_options.user_classes to the selected user_classes
                    parsed_options_dict[key] = request.form.getlist("user_classes")
                elif key == "run_time":
                    if not value:
                        continue
                    try:
                        run_time = parse_timespan(value)
                    except ValueError:
                        err_msg = "Valid run_time formats are : 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc."
                        logger.error(err_msg)
                        return jsonify({"success": False, "message": err_msg, "host": environment.host})
                elif key in parsed_options_dict:
                    # update the value in environment.parsed_options, but dont change the type.
                    # This won't work for parameters that are None
                    parsed_options_dict[key] = type(parsed_options_dict[key])(value)

            if environment.shape_class and environment.runner is not None:
                environment.runner.start_shape()
                return jsonify(
                    {"success": True, "message": "Swarming started using shape class", "host": environment.host}
                )

            if self._swarm_greenlet is not None:
                self._swarm_greenlet.kill(block=True)
                self._swarm_greenlet = None

            if environment.runner is not None:
                self._swarm_greenlet = gevent.spawn(environment.runner.start, user_count, spawn_rate)
                self._swarm_greenlet.link_exception(greenlet_exception_handler)
                response_data = {
                    "success": True,
                    "message": "Swarming started",
                    "host": environment.host,
                }
                if run_time:
                    gevent.spawn_later(run_time, self._stop_runners).link_exception(greenlet_exception_handler)
                    response_data["run_time"] = run_time

                if self.userclass_picker_is_active:
                    response_data["user_classes"] = sorted(user_classes.keys())

                return jsonify(response_data)
            else:
                return jsonify({"success": False, "message": "No runner", "host": environment.host})

        @app.route("/stop")
        @self.auth_required_if_enabled
        def stop() -> Response:
            if self._swarm_greenlet is not None:
                self._swarm_greenlet.kill(block=True)
                self._swarm_greenlet = None
            if environment.runner is not None:
                environment.runner.stop()
            return jsonify({"success": True, "message": "Test stopped"})

        @app.route("/stats/reset")
        @self.auth_required_if_enabled
        def reset_stats() -> str:
            environment.events.reset_stats.fire()
            if environment.runner is not None:
                environment.runner.stats.reset_all()
                environment.runner.exceptions = {}
            return "ok"

        @app.route("/stats/report")
        @self.auth_required_if_enabled
        def stats_report() -> Response:
            res = get_html_report(self.environment, show_download_link=not request.args.get("download"))
            if request.args.get("download"):
                res = app.make_response(res)
                res.headers["Content-Disposition"] = f"attachment;filename=report_{time()}.html"
            return res

        def _download_csv_suggest_file_name(suggest_filename_prefix: str) -> str:
            """Generate csv file download attachment filename suggestion.

            Arguments:
            suggest_filename_prefix: Prefix of the filename to suggest for saving the download. Will be appended with timestamp.
            """

            return f"{suggest_filename_prefix}_{time()}.csv"

        def _download_csv_response(csv_data: str, filename_prefix: str) -> Response:
            """Generate csv file download response with 'csv_data'.

            Arguments:
            csv_data: CSV header and data rows.
            filename_prefix: Prefix of the filename to suggest for saving the download. Will be appended with timestamp.
            """

            response = make_response(csv_data)
            response.headers["Content-type"] = "text/csv"
            response.headers[
                "Content-disposition"
            ] = f"attachment;filename={_download_csv_suggest_file_name(filename_prefix)}"
            return response

        @app.route("/stats/requests/csv")
        @self.auth_required_if_enabled
        def request_stats_csv() -> Response:
            data = StringIO()
            writer = csv.writer(data)
            self.stats_csv_writer.requests_csv(writer)
            return _download_csv_response(data.getvalue(), "requests")

        @app.route("/stats/requests_full_history/csv")
        @self.auth_required_if_enabled
        def request_stats_full_history_csv() -> Response:
            options = self.environment.parsed_options
            if options and options.stats_history_enabled and isinstance(self.stats_csv_writer, StatsCSVFileWriter):
                return send_file(
                    os.path.abspath(self.stats_csv_writer.stats_history_file_name()),
                    mimetype="text/csv",
                    as_attachment=True,
                    download_name=_download_csv_suggest_file_name("requests_full_history"),
                    etag=True,
                    max_age=0,
                    conditional=True,
                    last_modified=None,
                )

            return make_response("Error: Server was not started with option to generate full history.", 404)

        @app.route("/stats/failures/csv")
        @self.auth_required_if_enabled
        def failures_stats_csv() -> Response:
            data = StringIO()
            writer = csv.writer(data)
            self.stats_csv_writer.failures_csv(writer)
            return _download_csv_response(data.getvalue(), "failures")

        @app.route("/stats/requests")
        @self.auth_required_if_enabled
        @memoize(timeout=DEFAULT_CACHE_TIME, dynamic_timeout=True)
        def request_stats() -> Response:
            stats: List[Dict[str, Any]] = []
            errors: List[StatsErrorDict] = []

            if environment.runner is None:
                report = {
                    "stats": stats,
                    "errors": errors,
                    "total_rps": 0.0,
                    "fail_ratio": 0.0,
                    "current_response_time_percentile_1": None,
                    "current_response_time_percentile_2": None,
                    "state": STATE_MISSING,
                    "user_count": 0,
                }

                if isinstance(environment.runner, MasterRunner):
                    report.update({"workers": []})

                return jsonify(report)

            for s in chain(sort_stats(environment.runner.stats.entries), [environment.runner.stats.total]):
                stats.append(
                    {
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
                        "ninety_ninth_response_time": s.get_response_time_percentile(0.99),
                        "avg_content_length": s.avg_content_length,
                    }
                )

            for e in environment.runner.errors.values():
                err_dict = e.serialize()
                err_dict["name"] = escape(err_dict["name"])
                err_dict["error"] = escape(err_dict["error"])
                errors.append(err_dict)

            # Truncate the total number of stats and errors displayed since a large number of rows will cause the app
            # to render extremely slowly. Aggregate stats should be preserved.
            truncated_stats = stats[:500]
            if len(stats) > 500:
                truncated_stats += [stats[-1]]

            report = {"stats": truncated_stats, "errors": errors[:500]}

            if stats:
                report["total_rps"] = stats[len(stats) - 1]["current_rps"]
                report["fail_ratio"] = environment.runner.stats.total.fail_ratio
                report[
                    "current_response_time_percentile_1"
                ] = environment.runner.stats.total.get_current_response_time_percentile(
                    stats_module.PERCENTILES_TO_CHART[0]
                )
                report[
                    "current_response_time_percentile_2"
                ] = environment.runner.stats.total.get_current_response_time_percentile(
                    stats_module.PERCENTILES_TO_CHART[1]
                )

            if isinstance(environment.runner, MasterRunner):
                workers = []
                for worker in environment.runner.clients.values():
                    workers.append(
                        {
                            "id": worker.id,
                            "state": worker.state,
                            "user_count": worker.user_count,
                            "cpu_usage": worker.cpu_usage,
                            "memory_usage": worker.memory_usage,
                        }
                    )

                report["workers"] = workers

            report["state"] = environment.runner.state
            report["user_count"] = environment.runner.user_count

            return jsonify(report)

        @app.route("/exceptions")
        @self.auth_required_if_enabled
        def exceptions() -> Response:
            return jsonify(
                {
                    "exceptions": [
                        {
                            "count": row["count"],
                            "msg": escape(row["msg"]),
                            "traceback": escape(row["traceback"]),
                            "nodes": ", ".join(row["nodes"]),
                        }
                        for row in (environment.runner.exceptions.values() if environment.runner is not None else [])
                    ]
                }
            )

        @app.route("/exceptions/csv")
        @self.auth_required_if_enabled
        def exceptions_csv() -> Response:
            data = StringIO()
            writer = csv.writer(data)
            self.stats_csv_writer.exceptions_csv(writer)
            return _download_csv_response(data.getvalue(), "exceptions")

        @app.route("/tasks")
        @self.auth_required_if_enabled
        def tasks() -> Dict[str, Dict[str, Dict[str, float]]]:
            runner = self.environment.runner
            user_spawned: Dict[str, int]
            if runner is None:
                user_spawned = {}
            else:
                user_spawned = (
                    runner.reported_user_classes_count
                    if isinstance(runner, MasterRunner)
                    else runner.user_classes_count
                )

            task_data = {
                "per_class": get_ratio(self.environment.user_classes, user_spawned, False),
                "total": get_ratio(self.environment.user_classes, user_spawned, True),
            }
            return task_data

    def start(self):
        self.greenlet = gevent.spawn(self.start_server)
        self.greenlet.link_exception(greenlet_exception_handler)

    def start_server(self):
        if self.tls_cert and self.tls_key:
            self.server = pywsgi.WSGIServer(
                (self.host, self.port), self.app, log=None, keyfile=self.tls_key, certfile=self.tls_cert
            )
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

    def update_template_args(self):
        override_host_warning = False
        if self.environment.host:
            host = self.environment.host
        elif self.environment.runner.user_classes:
            all_hosts = {l.host for l in self.environment.runner.user_classes}
            if len(all_hosts) == 1:
                host = list(all_hosts)[0]
            else:
                # since we have multiple User classes with different host attributes, we'll
                # inform that specifying host will override the host for all User classes
                override_host_warning = True
                host = None
        else:
            host = None

        options = self.environment.parsed_options

        is_distributed = isinstance(self.environment.runner, MasterRunner)
        if is_distributed:
            worker_count = self.environment.runner.worker_count
        else:
            worker_count = 0

        stats = self.environment.runner.stats
        extra_options = argument_parser.ui_extra_args_dict()

        available_user_classes = (
            None if not self.environment.available_user_classes else sorted(self.environment.available_user_classes)
        )

        available_shape_classes = ["Default"]
        if self.environment.available_shape_classes:
            available_shape_classes += sorted(self.environment.available_shape_classes.keys())

        self.template_args = {
            "locustfile": self.environment.locustfile,
            "state": self.environment.runner.state,
            "is_distributed": is_distributed,
            "user_count": self.environment.runner.user_count,
            "version": version,
            "host": host,
            "history": stats.history if stats.num_requests > 0 else {},
            "override_host_warning": override_host_warning,
            "num_users": options and options.num_users,
            "spawn_rate": options and options.spawn_rate,
            "worker_count": worker_count,
            "is_shape": self.environment.shape_class and not self.userclass_picker_is_active,
            "stats_history_enabled": options and options.stats_history_enabled,
            "tasks": dumps({}),
            "extra_options": extra_options,
            "show_userclass_picker": self.userclass_picker_is_active,
            "available_user_classes": available_user_classes,
            "available_shape_classes": available_shape_classes,
            "percentile1": stats_module.PERCENTILES_TO_CHART[0],
            "percentile2": stats_module.PERCENTILES_TO_CHART[1],
        }

    def _update_shape_class(self, shape_class_name):
        if shape_class_name:
            shape_class = self.environment.available_shape_classes[shape_class_name]
        else:
            shape_class = None

        # Validating ShapeClass
        self.environment.shape_class = shape_class
        self.environment._validate_shape_class_instance()

    def _update_user_classes(self, user_classes):
        self.environment.user_classes = list(user_classes.values())
        # populate the locustfile which used in web ui title only
        if self.environment.locustfile is None:
            self.environment.locustfile = ",".join(self.environment.user_classes_by_name.keys())

        # Validating UserClasses
        self.environment._remove_user_classes_with_weight_zero()
        self.environment._validate_user_class_name_uniqueness()

    def _stop_runners(self):
        self.environment.runner.stop()
