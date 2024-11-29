from __future__ import annotations

import csv
import json
import logging
import mimetypes
import os.path
from functools import wraps
from html import escape
from io import StringIO
from itertools import chain
from json import dumps
from time import time
from typing import TYPE_CHECKING, Any, TypedDict

import gevent
from flask import (
    Blueprint,
    Flask,
    Response,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)
from flask_cors import CORS
from flask_login import LoginManager, login_required
from gevent import pywsgi

from . import __version__ as version
from . import argument_parser
from . import stats as stats_module
from .html import DEFAULT_BUILD_PATH, get_html_report, render_template_from
from .log import get_logs, greenlet_exception_logger
from .runners import STATE_MISSING, STATE_RUNNING, MasterRunner
from .stats import StatsCSV, StatsCSVFileWriter, StatsErrorDict, sort_stats
from .user.inspectuser import get_ratio
from .util.cache import memoize
from .util.date import format_safe_timestamp
from .util.timespan import parse_timespan

if TYPE_CHECKING:
    from .env import Environment


logger = logging.getLogger(__name__)
greenlet_exception_handler = greenlet_exception_logger(logger)

DEFAULT_CACHE_TIME = 2.0


class InputField(TypedDict, total=False):
    label: str
    name: str
    type: str | None
    default_value: bool | None
    choices: list[str] | None
    is_secret: bool | None
    is_required: bool | None


class CustomForm(TypedDict, total=False):
    inputs: list[InputField] | None
    callback_url: str
    submit_button_text: str | None


class AuthProvider(TypedDict, total=False):
    label: str | None
    callback_url: str
    icon_url: str | None


class AuthArgs(TypedDict, total=False):
    custom_form: CustomForm
    auth_providers: list[AuthProvider]
    username_password_callback: str
    error: str
    info: str


class WebUI:
    """
    Sets up and runs a Flask web app that can start and stop load tests using the
    :attr:`environment.runner <locust.env.Environment.runner>` as well as show the load test statistics
    in :attr:`environment.stats <locust.env.Environment.stats>`
    """

    app: Flask | None = None
    """
    Reference to the :class:`flask.Flask` app. Can be used to add additional web routes and customize
    the Flask app in other various ways. Example::

        from flask import request

        @web_ui.app.route("/my_custom_route")
        def my_custom_route():
            return "your IP is: %s" % request.remote_addr
    """

    greenlet: gevent.Greenlet | None = None
    """
    Greenlet of the running web server
    """

    server: pywsgi.WSGIServer | None = None
    """Reference to the :class:`pyqsgi.WSGIServer` instance"""

    template_args: dict[str, Any]
    """Arguments used to render index.html for the web UI. Must be used with custom templates
    extending index.html."""

    auth_args: AuthArgs
    """Arguments used to render auth.html for the web UI auth page. Must be used when configuring auth"""

    def __init__(
        self,
        environment: Environment,
        host: str,
        port: int,
        web_base_path: str | None = None,
        web_login: bool = False,
        tls_cert: str | None = None,
        tls_key: str | None = None,
        stats_csv_writer: StatsCSV | None = None,
        delayed_start=False,
        userclass_picker_is_active=False,
        build_path: str | None = None,
    ):
        """
        Create WebUI instance and start running the web server in a separate greenlet (self.greenlet)

        Arguments:
        environment: Reference to the current Locust Environment
        host: Host/interface that the web server should accept connections to
        port: Port that the web server should listen to
        web_login:  Enables a login page
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
        self.web_login = web_login
        app = Flask(__name__)
        CORS(app)
        self.app = app
        app.jinja_env.add_extension("jinja2.ext.do")
        app.debug = True
        self.greenlet: gevent.Greenlet | None = None
        self._swarm_greenlet: gevent.Greenlet | None = None
        self.template_args = {}
        self.auth_args = {}
        self.app.template_folder = build_path or DEFAULT_BUILD_PATH
        self.app.static_url_path = "/assets/"

        app_blueprint = Blueprint("locust", __name__, url_prefix=web_base_path)
        # ensures static js files work on Windows
        mimetypes.add_type("application/javascript", ".js")
        if self.web_login:
            self._login_manager = LoginManager()
            self._login_manager.init_app(self.app)
            self._login_manager.login_view = "locust.login"

        if environment.runner:
            self.update_template_args()
        if not delayed_start:
            self.start()

        @app_blueprint.errorhandler(Exception)
        def handle_exception(error):
            error_message = str(error)
            error_code = getattr(error, "code", 500)
            logger.log(
                logging.DEBUG if error_code <= 404 else logging.ERROR,
                f"UI got request for {request.method} {request.path}, but it resulted in a {error_code}: {error.name}",
            )
            return make_response(error_message, error_code)

        @app_blueprint.route("/assets/<path:path>")
        def send_assets(path):
            directory = (
                os.path.join(self.app.template_folder, "assets")
                if os.path.exists(os.path.join(app.template_folder, "assets", path))
                else os.path.join(DEFAULT_BUILD_PATH, "assets")
            )

            return send_from_directory(directory, path)

        @app_blueprint.route("/")
        @self.auth_required_if_enabled
        def index() -> str | Response:
            if not environment.runner:
                return make_response("Error: Locust Environment does not have any runner", 500)
            self.update_template_args()

            return render_template("index.html", template_args=self.template_args)

        @app_blueprint.route("/swarm", methods=["POST"])
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
                    parsed_options_dict["users"] = user_count
                elif key == "spawn_rate":
                    spawn_rate = float(value)
                    parsed_options_dict[key] = spawn_rate
                elif key == "host":
                    # Replace < > to guard against XSS
                    environment.host = str(request.form["host"]).replace("<", "").replace(">", "")
                    parsed_options_dict[key] = environment.host
                elif key == "user_classes":
                    # Set environment.parsed_options.user_classes to the selected user_classes
                    parsed_options_dict[key] = request.form.getlist("user_classes")
                elif key == "run_time":
                    if not value:
                        continue
                    try:
                        run_time = parse_timespan(value)
                        parsed_options_dict[key] = run_time
                    except ValueError:
                        err_msg = "Valid run_time formats are : 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc."
                        logger.error(err_msg)
                        return jsonify({"success": False, "message": err_msg, "host": environment.host})
                elif key in parsed_options_dict:
                    # update the value in environment.parsed_options, but dont change the type.
                    parsed_options_value = parsed_options_dict[key]

                    if isinstance(parsed_options_value, bool):
                        parsed_options_dict[key] = value == "true"
                    elif parsed_options_value is None:
                        parsed_options_dict[key] = parsed_options_value
                    else:
                        parsed_options_dict[key] = type(parsed_options_dict[key])(value)

            if environment.shape_class and environment.runner is not None:
                environment.runner.start_shape()
                return jsonify(
                    {
                        "success": True,
                        "message": f"Swarming started using shape class '{type(environment.shape_class).__name__}'",
                        "host": environment.host,
                    }
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

        @app_blueprint.route("/stop")
        @self.auth_required_if_enabled
        def stop() -> Response:
            if self._swarm_greenlet is not None:
                self._swarm_greenlet.kill(block=True)
                self._swarm_greenlet = None
            if environment.runner is not None:
                environment.runner.stop()
            return jsonify({"success": True, "message": "Test stopped"})

        @app_blueprint.route("/stats/reset")
        @self.auth_required_if_enabled
        def reset_stats() -> str:
            environment.events.reset_stats.fire()
            if environment.runner is not None:
                environment.runner.stats.reset_all()
                environment.runner.exceptions = {}
            return "ok"

        @app_blueprint.route("/stats/report")
        @self.auth_required_if_enabled
        def stats_report() -> Response:
            theme = request.args.get("theme", "")
            res = get_html_report(
                self.environment,
                show_download_link=not request.args.get("download"),
                theme=theme,
            )
            if request.args.get("download"):
                res = app.make_response(res)
                host = f"_{self.environment.host}" if self.environment.host else ""
                res.headers["Content-Disposition"] = (
                    f"attachment;filename=Locust_{format_safe_timestamp(self.environment.stats.start_time)}_"
                    + f"{self.environment.locustfile}{host}.html"
                )
            return res

        def _download_csv_suggest_file_name(suggest_filename_prefix: str) -> str:
            """Generate csv file download attachment filename suggestion.

            Arguments:
            suggest_filename_prefix: Prefix of the filename to suggest for saving the download.
            Will be appended with timestamp.
            """
            host = f"_{self.environment.host}" if self.environment.host else ""
            return (
                f"Locust_{format_safe_timestamp(self.environment.stats.start_time)}_"
                + f"{self.environment.locustfile}{host}_{suggest_filename_prefix}.csv"
            )

        def _download_csv_response(csv_data: str, filename_prefix: str) -> Response:
            """Generate csv file download response with 'csv_data'.

            Arguments:
            csv_data: CSV header and data rows.
            filename_prefix: Prefix of the filename to suggest for saving the download. Will be appended with timestamp.
            """

            response = make_response(csv_data)
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = (
                f"attachment;filename={_download_csv_suggest_file_name(filename_prefix)}"
            )
            return response

        @app_blueprint.route("/stats/requests/csv")
        @self.auth_required_if_enabled
        def request_stats_csv() -> Response:
            data = StringIO()
            writer = csv.writer(data)
            self.stats_csv_writer.requests_csv(writer)
            return _download_csv_response(data.getvalue(), "requests")

        @app_blueprint.route("/stats/requests_full_history/csv")
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

        @app_blueprint.route("/stats/failures/csv")
        @self.auth_required_if_enabled
        def failures_stats_csv() -> Response:
            data = StringIO()
            writer = csv.writer(data)
            self.stats_csv_writer.failures_csv(writer)
            return _download_csv_response(data.getvalue(), "failures")

        @app_blueprint.route("/stats/requests")
        @self.auth_required_if_enabled
        @memoize(timeout=DEFAULT_CACHE_TIME, dynamic_timeout=True)
        def request_stats() -> Response:
            stats: list[dict[str, Any]] = []
            errors: list[StatsErrorDict] = []

            if environment.runner is None:
                report = {
                    "stats": stats,
                    "errors": errors,
                    "total_rps": 0.0,
                    "total_fail_per_sec": 0.0,
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
                stats.append(s.to_dict())

            errors = [e.serialize() for e in environment.runner.errors.values()]

            # Truncate the total number of stats and errors displayed since a large number of rows will cause the app
            # to render extremely slowly. Aggregate stats should be preserved.
            truncated_stats = stats[:500]
            if len(stats) > 500:
                truncated_stats += [stats[-1]]

            report = {"stats": truncated_stats, "errors": errors[:500]}
            total_stats = stats[-1]

            if stats:
                report["total_rps"] = total_stats["current_rps"]
                report["total_fail_per_sec"] = total_stats["current_fail_per_sec"]
                report["fail_ratio"] = environment.runner.stats.total.fail_ratio
                report["current_response_time_percentiles"] = {
                    f"response_time_percentile_{percentile}": environment.runner.stats.total.get_current_response_time_percentile(
                        percentile
                    )
                    for percentile in stats_module.PERCENTILES_TO_CHART
                }

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

        @app_blueprint.route("/exceptions")
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

        @app_blueprint.route("/exceptions/csv")
        @self.auth_required_if_enabled
        def exceptions_csv() -> Response:
            data = StringIO()
            writer = csv.writer(data)
            self.stats_csv_writer.exceptions_csv(writer)
            return _download_csv_response(data.getvalue(), "exceptions")

        @app_blueprint.route("/tasks")
        @self.auth_required_if_enabled
        def tasks() -> dict[str, dict[str, dict[str, float]]]:
            runner = self.environment.runner
            user_spawned: dict[str, int]
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

        @app_blueprint.route("/logs")
        @self.auth_required_if_enabled
        def logs():
            return jsonify({"master": get_logs(), "workers": self.environment.worker_logs})

        @app_blueprint.route("/login")
        def login():
            if not self.web_login:
                return redirect(url_for("locust.index"))

            self.auth_args["error"] = session.get("auth_error", None)
            self.auth_args["info"] = session.get("auth_info", None)

            return render_template_from(
                "auth.html", auth_args=self.auth_args, auth_title=self.auth_args.get("title", "Locust")
            )

        @app_blueprint.route("/user", methods=["POST"])
        def update_user():
            assert request.method == "POST"

            user_settings = json.loads(request.data)
            self.environment.update_user_class(user_settings)

            return {}, 201

        app.register_blueprint(app_blueprint)

    @property
    def login_manager(self):
        if self.web_login:
            return self._login_manager

        raise AttributeError("The login_manager is only available with --web-login.\n")

    @login_manager.setter
    def login_manager(self, value):
        self._login_manager = value

    def start(self):
        self.greenlet = gevent.spawn(self.start_server)
        self.greenlet.link_exception(greenlet_exception_handler)

    def start_server(self):
        if self.tls_cert and self.tls_key:
            self.server = pywsgi.WSGIServer(
                (self.host, self.port), self.app, log=None, keyfile=self.tls_key, certfile=self.tls_cert
            )
        else:

            class RewriteFilter(logging.Filter):
                def filter(self, record) -> bool:
                    msg = record.msg
                    if "gevent._socket3.socket at" in msg and "Invalid HTTP method: '\x16\x03" in msg:
                        record.msg = f"An https request was made against Locust's Web UI (which was expecting http). Underlying error was: {record.msg}"
                    return True

            logger.addFilter(RewriteFilter())
            self.server = pywsgi.WSGIServer((self.host, self.port), self.app, log=None, error_log=logger)

        self.server.serve_forever()

    def stop(self):
        """
        Stop the running web server
        """
        self.server.stop()

    def auth_required_if_enabled(self, view_func):
        """
        Decorator that can be used on custom route methods that will turn on Flask Login
        authentication if the ``--web-login`` flag is used. Example::

            @web_ui.app.route("/my_custom_route")
            @web_ui.auth_required_if_enabled
            def my_custom_route():
                return "custom response"
        """

        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if self.web_login:
                try:
                    session["auth_error"] = None
                    session["auth_info"] = None
                    return login_required(view_func)(*args, **kwargs)
                except Exception as e:
                    return f"Locust auth exception: {e} See https://docs.locust.io/en/stable/extending-locust.html#adding-authentication-to-the-web-ui for configuring authentication."
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

        if is_distributed := isinstance(self.environment.runner, MasterRunner):
            worker_count = self.environment.runner.worker_count
        else:
            worker_count = 0

        stats = self.environment.runner.stats
        extra_options = argument_parser.ui_extra_args_dict()

        available_user_classes = None
        users = None
        if self.environment.available_user_classes:
            available_user_classes = sorted(self.environment.available_user_classes)
            users = {
                user_class_name: user_class.json()
                for (user_class_name, user_class) in self.environment.available_user_classes.items()
            }

        available_shape_classes = ["Default"]
        if self.environment.available_shape_classes:
            available_shape_classes += sorted(self.environment.available_shape_classes.keys())

        available_user_tasks = (
            {
                user_class_name: [task.__name__ for task in user_class]
                for (user_class_name, user_class) in self.environment.available_user_tasks.items()
            }
            if self.environment.available_user_tasks
            else None
        )

        new_template_args = {
            "locustfile": self.environment.locustfile,
            "state": self.environment.runner.state,
            "is_distributed": is_distributed,
            "user_count": self.environment.runner.user_count,
            "version": version,
            "host": host if host else "",
            "history": stats.history if stats.num_requests > 0 else [],
            "override_host_warning": override_host_warning,
            "num_users": options and options.num_users,
            "spawn_rate": options and options.spawn_rate,
            "worker_count": worker_count,
            "hide_common_options": (
                self.environment.shape_class
                and not (self.userclass_picker_is_active or self.environment.shape_class.use_common_options)
            ),
            "shape_use_common_options": self.environment.shape_class
            and self.environment.shape_class.use_common_options,
            "stats_history_enabled": options and options.stats_history_enabled,
            "tasks": dumps({}),
            "extra_options": extra_options,
            "run_time": options and options.run_time,
            "show_userclass_picker": self.userclass_picker_is_active,
            "available_user_classes": available_user_classes,
            "available_shape_classes": available_shape_classes,
            "available_user_tasks": available_user_tasks,
            "users": users,
            "percentiles_to_chart": stats_module.PERCENTILES_TO_CHART,
            "percentiles_to_statistics": stats_module.PERCENTILES_TO_STATISTICS,
        }

        self.template_args = {**self.template_args, **new_template_args}

    def _update_shape_class(self, shape_class_name):
        if shape_class_name:
            shape_class = self.environment.available_shape_classes[shape_class_name]
            shape_class.runner = self.environment.runner
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
