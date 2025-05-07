from __future__ import annotations

import locust
from locust import runners
from locust.rpc import Message, zmqrpc

import ast
import atexit
import json
import os
import platform
import socket
import sys
import tempfile
import textwrap
from collections import OrderedDict
from typing import Any, NamedTuple
from urllib.parse import urlparse
from uuid import uuid4

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import configargparse
import gevent
import requests

from .util.directory import get_abspaths_in
from .util.timespan import parse_timespan
from .util.url import is_url

version = locust.__version__


DEFAULT_CONFIG_FILES = ("~/.locust.conf", "locust.conf", "pyproject.toml")

try:
    from locust_cloud.args import add_locust_cloud_argparse
except ModuleNotFoundError as e:
    add_locust_cloud_argparse = lambda _: None
    if e.msg != "No module named 'locust_cloud'":
        raise


# Clean up downloaded locustfile on exit
def exit_handler(filename) -> None:
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass  # when multiple workers are running on the same machine, another one may already have deleted it
    except PermissionError:
        pass  # this happens occasionally on windows on GH, maybe for the same reason?


class LocustArgumentParser(configargparse.ArgumentParser):
    """Drop-in replacement for `configargparse.ArgumentParser` that adds support for
    optionally exclude arguments from the UI.
    """

    def add_argument(self, *args, **kwargs) -> configargparse.Action:
        """
        This method supports the same args as ArgumentParser.add_argument(..)
        as well as the additional args below.

        Arguments:
            include_in_web_ui: If True (default), the argument will show in the UI.
            is_secret: If True (default is False) and include_in_web_ui is True, the argument will show in the UI with a password masked text input.
            is_required: If True (default is False) and include_in_web_ui is True, the argument will show in the UI as a required form field.

        Returns:
            argparse.Action: the new argparse action
        """
        include_in_web_ui = kwargs.pop("include_in_web_ui", True)
        is_secret = kwargs.pop("is_secret", False)
        is_required = kwargs.pop("is_required", False)
        action = super().add_argument(*args, **kwargs)
        action.include_in_web_ui = include_in_web_ui
        action.is_secret = is_secret
        action.is_required = is_required
        return action

    @property
    def args_included_in_web_ui(self) -> dict[str, configargparse.Action]:
        return {a.dest: a for a in self._actions if hasattr(a, "include_in_web_ui") and a.include_in_web_ui}

    @property
    def secret_args_included_in_web_ui(self) -> dict[str, configargparse.Action]:
        return {
            a.dest: a
            for a in self._actions
            if a.dest in self.args_included_in_web_ui and hasattr(a, "is_secret") and a.is_secret
        }

    @property
    def required_args_included_in_web_ui(self) -> dict[str, configargparse.Action]:
        return {
            a.dest: a
            for a in self._actions
            if a.dest in self.args_included_in_web_ui and hasattr(a, "is_required") and a.is_required
        }


class LocustTomlConfigParser(configargparse.TomlConfigParser):
    def parse(self, stream):
        try:
            config = tomllib.loads(stream.read())
        except Exception as e:
            raise configargparse.ConfigFileParserException(f"Couldn't parse TOML file: {e}")

        # convert to dict and filter based on section names
        result = OrderedDict()

        for section in self.sections:
            if data := configargparse.get_toml_section(config, section):
                for key, value in data.items():
                    if isinstance(value, list):
                        result[key] = value
                    elif value is None:
                        pass
                    else:
                        result[key] = str(value)
                break

        return result


def parse_locustfile_paths(paths: list[str]) -> list[str]:
    """
    Returns a list of relative file paths.

    Args:
        paths (list[str]): paths taken from the -f command

    Returns:
        list[str]: Parsed locust file paths
    """
    # Parse each path and unpack the returned lists as a single list
    return [parsed for path in paths for parsed in _parse_locustfile_path(path)]


def _parse_locustfile_path(path: str) -> list[str]:
    parsed_paths = []
    if is_url(path):
        # Download the file and use the new path as locustfile
        parsed_paths.append(download_locustfile_from_url(path))
    elif os.path.isdir(path):
        # Find all .py files in directory tree
        parsed_paths.extend(get_abspaths_in(path, extension=".py"))
        if not parsed_paths:
            sys.stderr.write(f"Could not find any locustfiles in directory '{path}'")
            sys.exit(1)
    else:
        # If file exists add the abspath
        if os.path.exists(path) and path.endswith(".py"):
            parsed_paths.append(os.path.abspath(path))
        else:
            note_about_file_endings = "Ensure your locustfile ends with '.py' or is a directory with locustfiles. "
            sys.stderr.write(f"Could not find '{path}'. {note_about_file_endings}See --help for available options.\n")
            sys.exit(1)

    return parsed_paths


def download_locustfile_from_url(url: str) -> str:
    """
    Attempt to download and save locustfile from url.
    Returns path to downloaded file.
    """
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"Failed to get locustfile from: {url}. Exception: {e}")
        sys.exit(1)
    else:
        try:
            # Check if response is valid python code
            ast.parse(response.text)
        except SyntaxError:
            sys.stderr.write(
                f"Failed to get locustfile from: {url}. Response was not valid python code: '{response.text[:100]}'"
            )
            sys.exit(1)

    with open(os.path.join(tempfile.gettempdir(), urlparse(url).path.split("/")[-1]), "w") as locustfile:
        locustfile.write(response.text)

    atexit.register(exit_handler, locustfile.name)
    return locustfile.name


def get_empty_argument_parser(add_help=True, default_config_files=DEFAULT_CONFIG_FILES) -> LocustArgumentParser:
    parser = LocustArgumentParser(
        default_config_files=default_config_files,
        config_file_parser_class=configargparse.CompositeConfigParser(
            [
                LocustTomlConfigParser(["tool.locust"]),
                configargparse.DefaultConfigFileParser,
            ]
        ),
        add_env_var_help=False,
        add_config_file_help=False,
        add_help=add_help,
        formatter_class=configargparse.RawDescriptionHelpFormatter,
        usage=configargparse.SUPPRESS,
        description=textwrap.dedent(
            """
Usage: locust [options] [UserClass ...]
        """
        ),
        epilog="""Examples:

    locust -f my_test.py -H https://www.example.com

    locust --headless -u 100 -t 20m --processes 4 MyHttpUser AnotherUser

    locust --headless -u 100 -r 10 -t 50 --print-stats --html "test_report_{u}_{r}_{t}.html" -H https://www.example.com
    (The above run would generate an html file with the name "test_report_100_10_50.html")

See documentation for more details, including how to set options using a file or environment variables: https://docs.locust.io/en/stable/configuration.html""",
    )
    parser.add_argument(
        "-f",
        "--locustfile",
        metavar="<filename>",
        default="locustfile.py",
        help="The Python file or module that contains your test, e.g. 'my_test.py'. Accepts multiple comma-separated .py files, a package name/directory or a url to a remote locustfile. Defaults to 'locustfile'.",
        env_var="LOCUST_LOCUSTFILE",
    )

    parser.add_argument(
        "--config",
        is_config_file_arg=True,
        help="File to read additional configuration from. See https://docs.locust.io/en/stable/configuration.html#configuration-file",
        metavar="<filename>",
    )

    return parser


def download_locustfile_from_master(master_host: str, master_port: int) -> str:
    client_id = socket.gethostname() + "_download_locustfile_" + uuid4().hex
    tempclient = zmqrpc.Client(master_host, master_port, client_id)
    got_reply = False

    def ask_for_locustfile():
        while not got_reply:
            tempclient.send(Message("locustfile", {"version": version}, client_id))
            gevent.sleep(1)

    def log_warning():
        gevent.sleep(10)
        while not got_reply:
            sys.stderr.write("Waiting to connect to master to receive locustfile...\n")
            gevent.sleep(60)

    def wait_for_reply():
        return tempclient.recv()

    gevent.spawn(ask_for_locustfile)
    gevent.spawn(log_warning)

    try:
        # wait same time as for client_ready ack. not that it is really relevant...
        msg = gevent.spawn(wait_for_reply).get(timeout=runners.CONNECT_TIMEOUT * runners.CONNECT_RETRY_COUNT)
        got_reply = True
    except gevent.Timeout:
        sys.stderr.write(
            f"Got no locustfile response from master, gave up after {runners.CONNECT_TIMEOUT * runners.CONNECT_RETRY_COUNT}s\n"
        )
        sys.exit(1)

    if msg.type != "locustfile":
        sys.stderr.write(f"Got wrong message type from master {msg.type}\n")
        sys.exit(1)

    if "error" in msg.data:
        sys.stderr.write(f"Got error from master: {msg.data['error']}\n")
        sys.exit(1)

    tempclient.close()
    return msg.data.get("locustfiles", [])


def parse_locustfiles_from_master(locustfile_sources) -> list[str]:
    locustfiles = []

    for source in locustfile_sources:
        if "contents" in source:
            filename = source["filename"]
            file_contents = source["contents"]

            with open(os.path.join(tempfile.gettempdir(), filename), "w", encoding="utf-8") as locustfile:
                locustfile.write(file_contents)

            locustfiles.append(locustfile.name)
        else:
            locustfiles.append(source)

    return locustfiles


def parse_locustfile_option(args=None) -> list[str]:
    """
    Construct a command line parser that is only used to parse the -f argument so that we can
    import the test scripts in case any of them adds additional command line arguments to the
    parser

    Returns:
        parsed_paths (List): List of locustfile paths
    """
    parser = get_empty_argument_parser(add_help=False)
    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--version",
        "-V",
        action="store_true",
        default=False,
    )
    # the following arguments are only used for downloading the locustfile from master
    parser.add_argument(
        "--worker",
        action="store_true",
        env_var="LOCUST_MODE_WORKER",
    )
    parser.add_argument(
        "--master",  # this is just here to prevent argparse from giving the dreaded "ambiguous option: --master could match --master-host, --master-port"
        action="store_true",
        env_var="LOCUST_MODE_MASTER",
    )
    parser.add_argument(
        "--master-host",
        default="127.0.0.1",
        env_var="LOCUST_MASTER_NODE_HOST",
    )
    parser.add_argument(
        "--master-port",
        type=int,
        default=5557,
        env_var="LOCUST_MASTER_NODE_PORT",
    )

    options, _ = parser.parse_known_args(args=args)

    if options.help or options.version:
        # if --help or --version is specified we'll call parse_options which will print the help/version message
        parse_options(args=args)

    if options.locustfile == "-":
        if not options.worker:
            sys.stderr.write(
                "locustfile was set to '-' (meaning to download from master) but --worker was not specified.\n"
            )
            sys.exit(1)
        # having this in argument_parser module is a bit weird, but it needs to be done early
        locustfile_sources = download_locustfile_from_master(options.master_host, options.master_port)
        locustfile_list = parse_locustfiles_from_master(locustfile_sources)
    else:
        locustfile_list = [f.strip() for f in options.locustfile.split(",")]

    parsed_paths = parse_locustfile_paths(locustfile_list)

    if not parsed_paths:
        note_about_file_endings = ""
        user_friendly_locustfile_name = options.locustfile

        if not options.locustfile.endswith(".py"):
            note_about_file_endings = "Ensure your locustfile ends with '.py' or is a directory with parsed_paths. "
        sys.stderr.write(
            f"Could not find '{user_friendly_locustfile_name}'. {note_about_file_endings}See --help for available options.\n"
        )
        sys.exit(1)

    return parsed_paths


# A hack for setting up an action that raises ArgumentError with configurable error messages.
# This is meant to be used to immediately block use of deprecated arguments with some helpful messaging.


def raise_argument_type_error(err_msg):
    class ErrorRaisingAction(configargparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            raise configargparse.ArgumentError(self, err_msg)

    return ErrorRaisingAction


# Definitions for some "types" to use with the arguments


def timespan(time_str) -> int:
    try:
        return parse_timespan(time_str)
    except ValueError as e:
        raise configargparse.ArgumentTypeError(str(e))


def positive_integer(string) -> int:
    try:
        value = int(string)
    except ValueError:
        raise configargparse.ArgumentTypeError(f"invalid int value: '{string}'")

    if value < 1:
        raise configargparse.ArgumentTypeError(
            f"Invalid --expect-workers argument ({value}), must be a positive number"
        )

    return value


def json_user_config(string):
    try:
        if string.endswith(".json"):
            with open(string) as file:
                user_config = json.load(file)
        else:
            user_config = json.loads(string)

        if not isinstance(user_config, list):
            user_config = [user_config]

        for config in user_config:
            if "user_class_name" not in config:
                raise configargparse.ArgumentTypeError("The user config must specify a user_class_name")

        return user_config

    except json.decoder.JSONDecodeError as e:
        raise configargparse.ArgumentTypeError(f"The --config-users argument must be a valid JSON string or file: {e}")

    except FileNotFoundError as e:
        raise configargparse.ArgumentTypeError(str(e))


def setup_parser_arguments(parser):
    """
    Setup command-line options

    Takes a configargparse.ArgumentParser as argument and calls it's add_argument
    for each of the supported arguments
    """
    parser._optionals.title = "Common options"
    parser.add_argument(
        "-H",
        "--host",
        metavar="<base url>",
        help="Host to load test, in the following format: https://www.example.com",
        env_var="LOCUST_HOST",
    )
    parser.add_argument(
        "-u",
        "--users",
        type=int,
        metavar="<int>",
        dest="num_users",
        help="Peak number of concurrent Locust users. Primarily used together with --headless or --autostart. Can be changed during a test by keyboard inputs w, W (spawn 1, 10 users) and s, S (stop 1, 10 users)",
        env_var="LOCUST_USERS",
    )
    parser.add_argument(
        "-r",
        "--spawn-rate",
        type=float,
        metavar="<float>",
        help="Rate to spawn users at (users per second). Primarily used together with --headless or --autostart",
        env_var="LOCUST_SPAWN_RATE",
    )
    parser.add_argument(
        "-t",
        "--run-time",
        metavar="<time string>",
        help="Stop after the specified amount of time, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with --headless or --autostart. Defaults to run forever.",
        env_var="LOCUST_RUN_TIME",
        type=timespan,
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        dest="list_commands",
        help="Show list of possible User classes and exit",
    )
    parser.add_argument(
        "--config-users",
        type=json_user_config,
        nargs="*",
        help="User configuration as a JSON string or file. A list of arguments or an Array of JSON configuration may be provided",
        env_var="LOCUST_CONFIG_USERS",
    )

    web_ui_group = parser.add_argument_group("Web UI options")
    web_ui_group.add_argument(
        "--web-host",
        default="",
        metavar="<ip>",
        help="Host to bind the web interface to. Defaults to '*' (all interfaces)",
        env_var="LOCUST_WEB_HOST",
    )
    web_ui_group.add_argument(
        "--web-host-display-name",
        type=str,
        help=configargparse.SUPPRESS,
        env_var="LOCUST_WEB_HOST_DISPLAY_NAME",
    )
    web_ui_group.add_argument(
        "--web-port",
        "-P",
        type=int,
        metavar="<port number>",
        default=8089,
        help="Port on which to run web host",
        env_var="LOCUST_WEB_PORT",
    )
    web_ui_group.add_argument(
        "--headless",
        action="store_true",
        help="Disable the web interface, and start the test immediately. Use -u and -t to control user count and run time",
        env_var="LOCUST_HEADLESS",
    )
    web_ui_group.add_argument(
        "--autostart",
        action="store_true",
        help="Starts the test immediately (like --headless, but without disabling the web UI)",
        env_var="LOCUST_AUTOSTART",
    )
    web_ui_group.add_argument(
        "--autoquit",
        type=int,
        metavar="<seconds>",
        default=-1,
        help="Quits Locust entirely, X seconds after the run is finished. Only used together with --autostart. The default is to keep Locust running until you shut it down using CTRL+C",
        env_var="LOCUST_AUTOQUIT",
    )
    # Override --headless parameter (useful because you can't disable a store_true-parameter like headless once it has been set in a config file)
    web_ui_group.add_argument(
        "--headful",
        action="store_true",
        help=configargparse.SUPPRESS,
        env_var="LOCUST_HEADFUL",
    )
    web_ui_group.add_argument(
        "--web-auth",
        type=str,
        dest="web_auth",
        metavar="<username:password>",
        default=None,
        help=configargparse.SUPPRESS,
        env_var="LOCUST_WEB_AUTH",
        action=raise_argument_type_error(
            "The --web-auth parameters has been replaced with --web-login. See https://docs.locust.io/en/stable/extending-locust.html#authentication for details"
        ),
    )
    web_ui_group.add_argument(
        "--web-login",
        default=False,
        action="store_true",
        help="Protects the web interface with a login page. See https://docs.locust.io/en/stable/extending-locust.html#authentication",
        env_var="LOCUST_WEB_LOGIN",
    )
    web_ui_group.add_argument(
        "--tls-cert",
        default="",
        metavar="<filename>",
        help="Optional path to TLS certificate to use to serve over HTTPS",
        env_var="LOCUST_TLS_CERT",
    )
    web_ui_group.add_argument(
        "--tls-key",
        default="",
        metavar="<filename>",
        help="Optional path to TLS private key to use to serve over HTTPS",
        env_var="LOCUST_TLS_KEY",
    )
    web_ui_group.add_argument(
        "--class-picker",
        default=False,
        action="store_true",
        help="Enable select boxes in the web interface to choose from all available User classes and Shape classes",
        env_var="LOCUST_USERCLASS_PICKER",
    )
    web_ui_group.add_argument(
        "--build-path",
        type=str,
        default="",
        help=configargparse.SUPPRESS,
        env_var="LOCUST_BUILD_PATH",
    )
    web_ui_group.add_argument(
        "--legacy-ui",
        default=False,
        action=raise_argument_type_error("--legacy-ui is no longer supported, remove the parameter to continue"),
        nargs=0,
        help=configargparse.SUPPRESS,
        env_var="LOCUST_LEGACY_UI",
    )

    master_group = parser.add_argument_group(
        "Master options",
        "Options for running a Locust Master node when running Locust distributed. A Master node need Worker nodes that connect to it before it can run load tests.",
    )
    # if locust should be run in distributed mode as master
    master_group.add_argument(
        "--master",
        action="store_true",
        help="Launch locust as a master node, to which worker nodes connect.",
        env_var="LOCUST_MODE_MASTER",
    )
    master_group.add_argument(
        "--master-bind-host",
        default="*",
        metavar="<ip>",
        help="IP address for the master to listen on, e.g '192.168.1.1'. Defaults to * (all available interfaces).",
        env_var="LOCUST_MASTER_BIND_HOST",
    )
    master_group.add_argument(
        "--master-bind-port",
        type=int,
        metavar="<port number>",
        default=5557,
        help="Port for the master to listen on. Defaults to 5557.",
        env_var="LOCUST_MASTER_BIND_PORT",
    )
    master_group.add_argument(
        "--expect-workers",
        type=positive_integer,
        metavar="<int>",
        default=1,
        help="Delay starting the test until this number of workers have connected (only used in combination with --headless/--autostart).",
        env_var="LOCUST_EXPECT_WORKERS",
    )
    master_group.add_argument(
        "--expect-workers-max-wait",
        type=int,
        metavar="<int>",
        default=0,
        help="How long should the master wait for workers to connect before giving up. Defaults to wait forever",
        env_var="LOCUST_EXPECT_WORKERS_MAX_WAIT",
    )
    master_group.add_argument(
        "--enable-rebalancing",
        action="store_true",
        default=False,
        dest="enable_rebalancing",
        help="Re-distribute users if new workers are added or removed during a test run. Experimental.",
    )
    master_group.add_argument(
        "--expect-slaves",
        action=raise_argument_type_error("The --expect-slaves parameter has been renamed --expect-workers"),
        nargs=0,
        help=configargparse.SUPPRESS,
    )

    worker_group = parser.add_argument_group(
        "Worker options",
        """Options for running a Locust Worker node when running Locust distributed.
Typically ONLY these options (and --locustfile) need to be specified on workers, since other options (-u, -r, -t, ...) are controlled by the master node.""",
    )
    worker_group.add_argument(
        "--worker",
        action="store_true",
        help="Set locust to run in distributed mode with this process as worker. Can be combined with setting --locustfile to '-' to download it from master.",
        env_var="LOCUST_MODE_WORKER",
    )
    worker_group.add_argument(
        "--processes",
        type=int,
        metavar="<int>",
        help="Number of times to fork the locust process, to enable using system. Combine with --worker flag or let it automatically set --worker and --master flags for an all-in-one-solution. Not available on Windows. Experimental.",
        env_var="LOCUST_PROCESSES",
    )
    worker_group.add_argument(
        "--slave",
        action=raise_argument_type_error("The --slave parameter has been renamed --worker"),
        nargs=0,
        help=configargparse.SUPPRESS,
    )
    worker_group.add_argument(
        "--master-host",
        default="127.0.0.1",
        help="Hostname of locust master node to connect to. Defaults to 127.0.0.1.",
        env_var="LOCUST_MASTER_NODE_HOST",
        metavar="<hostname>",
    )
    worker_group.add_argument(
        "--master-port",
        type=int,
        metavar="<port number>",
        default=5557,
        help="Port to connect to on master node. Defaults to 5557.",
        env_var="LOCUST_MASTER_NODE_PORT",
    )

    web_ui_group.add_argument(
        "--web-base-path",
        type=str,
        default="",
        help="Base path for the web interface (e.g., '/locust'). Default is empty (root path).",
        env_var="LOCUST_WEB_BASE_PATH",
    )

    tag_group = parser.add_argument_group(
        "Tag options",
        "Locust tasks can be tagged using the @tag decorator. These options let specify which tasks to include or exclude during a test.",
    )
    tag_group.add_argument(
        "-T",
        "--tags",
        nargs="*",
        metavar="<tag>",
        env_var="LOCUST_TAGS",
        help="List of tags to include in the test, so only tasks with at least one matching tag will be executed",
    )
    tag_group.add_argument(
        "-E",
        "--exclude-tags",
        nargs="*",
        metavar="<tag>",
        env_var="LOCUST_EXCLUDE_TAGS",
        help="List of tags to exclude from the test, so only tasks with no matching tags will be executed",
    )

    stats_group = parser.add_argument_group("Request statistics options")
    stats_group.add_argument(
        "--csv",  # Name repeated in 'parse_options'
        dest="csv_prefix",
        metavar="<filename>",
        help="Store request stats to files in CSV format. Setting this option will generate three files: <filename>_stats.csv, <filename>_stats_history.csv and <filename>_failures.csv. Any folders part of the prefix will be automatically created",
        env_var="LOCUST_CSV",
    )
    stats_group.add_argument(
        "--csv-full-history",  # Name repeated in 'parse_options'
        action="store_true",
        default=False,
        dest="stats_history_enabled",
        help="Store each stats entry in CSV format to _stats_history.csv file. You must also specify the '--csv' argument to enable this.",
        env_var="LOCUST_CSV_FULL_HISTORY",
    )
    stats_group.add_argument(
        "--print-stats",
        action="store_true",
        help="Enable periodic printing of request stats in UI runs",
        env_var="LOCUST_PRINT_STATS",
    )
    stats_group.add_argument(
        "--only-summary",
        action="store_true",
        help="Disable periodic printing of request stats during --headless run",
        env_var="LOCUST_ONLY_SUMMARY",
    )
    stats_group.add_argument(
        "--reset-stats",
        action="store_true",
        help="Reset statistics once spawning has been completed. Should be set on both master and workers when running in distributed mode",
        env_var="LOCUST_RESET_STATS",
    )
    stats_group.add_argument(
        "--html",
        metavar="<filename>",
        dest="html_file",
        help="Store HTML report to file path specified. Able to parse certain tags - {u}, {r}, {t} and convert them to number of users, spawn rate and run time respectively.",
        env_var="LOCUST_HTML",
    )
    stats_group.add_argument(
        "--json",
        default=False,
        action="store_true",
        help="Prints the final stats in JSON format to stdout. Useful for parsing the results in other programs/scripts. Use together with --headless and --skip-log for an output only with the json data.",
    )

    log_group = parser.add_argument_group("Logging options")
    log_group.add_argument(
        "--skip-log-setup",
        action="store_true",
        dest="skip_log_setup",
        default=False,
        help="Disable Locust's logging setup. Instead, the configuration is provided by the Locust test or Python defaults.",
        env_var="LOCUST_SKIP_LOG_SETUP",
    )
    log_group.add_argument(
        "--loglevel",
        "-L",
        default="INFO",
        help="Choose between DEBUG/INFO/WARNING/ERROR/CRITICAL. Default is INFO.",
        metavar="<level>",
        env_var="LOCUST_LOGLEVEL",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        type=str.upper,
    )
    log_group.add_argument(
        "--logfile",
        help="Path to log file. If not set, log will go to stderr",
        metavar="<filename>",
        env_var="LOCUST_LOGFILE",
    )

    other_group = parser.add_argument_group("Other options")
    other_group.add_argument(
        "--show-task-ratio",
        action="store_true",
        help="Print table of the User classes' task execution ratio. Use this with non-zero --user option if some classes define non-zero fixed_count attribute.",
    )
    other_group.add_argument(
        "--show-task-ratio-json",
        action="store_true",
        help="Print json data of the User classes' task execution ratio. Use this with non-zero --user option if some classes define non-zero fixed_count attribute.",
    )
    # optparse gives you --version but we have to do it ourselves to get -V too
    other_group.add_argument(
        "--version",
        "-V",
        action="version",
        help="Show program's version number and exit",
        version=f"locust {version} from {os.path.dirname(__file__)} (Python {platform.python_version()})",
    )
    other_group.add_argument(
        "--exit-code-on-error",
        type=int,
        metavar="<int>",
        default=1,
        help="Sets the process exit code to use when a test result contain any failure or error. Defaults to 1.",
        env_var="LOCUST_EXIT_CODE_ON_ERROR",
    )
    other_group.add_argument(
        "-s",
        "--stop-timeout",
        action="store",
        dest="stop_timeout",
        metavar="<number>",
        default="0",
        help="Number of seconds to wait for a simulated user to complete any executing task before exiting. Default is to terminate immediately. When running distributed, this only needs to be specified on the master.",
        env_var="LOCUST_STOP_TIMEOUT",
        type=timespan,
    )
    other_group.add_argument(
        "--equal-weights",
        action="store_true",
        default=False,
        dest="equal_weights",
        help="Use equally distributed task weights, overriding the weights specified in the locustfile.",
    )
    other_group.add_argument(
        "--profile",
        type=str,
        help="Set a profile to group the testruns together",
    )

    user_classes_group = parser.add_argument_group("User classes")
    user_classes_group.add_argument(
        "user_classes",
        nargs="*",
        metavar="<UserClass1 UserClass2>",
        help="At the end of the command line, you can list User classes to be used (available User classes can be listed with --list). LOCUST_USER_CLASSES environment variable can also be used to specify User classes. Default is to use all available User classes",
        default=os.environ.get("LOCUST_USER_CLASSES", "").split(),
    )


def get_parser(default_config_files=DEFAULT_CONFIG_FILES) -> LocustArgumentParser:
    # get a parser that is only able to parse the -f argument
    parser = get_empty_argument_parser(add_help=True, default_config_files=default_config_files)
    # add all the other supported arguments
    setup_parser_arguments(parser)
    add_locust_cloud_argparse(parser)
    # fire event to provide a hook for locustscripts and plugins to add command line arguments
    locust.events.init_command_line_parser.fire(parser=parser)
    return parser


def parse_options(args=None) -> configargparse.Namespace:
    parser = get_parser()
    parsed_opts = parser.parse_args(args=args)
    if parsed_opts.stats_history_enabled and (parsed_opts.csv_prefix is None):
        parser.error("'--csv-full-history' requires '--csv'.")
    return parsed_opts


def default_args_dict() -> dict:
    # returns a dict containing the default arguments (before any custom arguments are added)
    default_parser = get_empty_argument_parser()
    setup_parser_arguments(default_parser)
    # Dont read config files because they may contain custom arguments, which would fail parsing in the next step
    default_parser._default_config_files = {}
    return vars(default_parser.parse([]))


class UIExtraArgOptions(NamedTuple):
    default_value: str
    is_secret: bool
    is_required: bool
    help_text: str
    choices: list[str] | None = None


def ui_extra_args_dict(args=None) -> dict[str, dict[str, Any]]:
    """Get all the UI visible arguments"""
    locust_args = default_args_dict()

    parser = get_parser()
    all_args = vars(parser.parse_args(args))

    extra_args = {
        k: UIExtraArgOptions(
            default_value=v,
            is_secret=k in parser.secret_args_included_in_web_ui,
            is_required=k in parser.required_args_included_in_web_ui,
            help_text=parser.args_included_in_web_ui[k].help,
            choices=parser.args_included_in_web_ui[k].choices,
        )._asdict()
        for k, v in all_args.items()
        if k not in locust_args and k in parser.args_included_in_web_ui
    }

    return extra_args
