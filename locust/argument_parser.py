import os
import platform
import sys
import textwrap
from typing import Dict, List, NamedTuple

import configargparse

import locust

version = locust.__version__


DEFAULT_CONFIG_FILES = ["~/.locust.conf", "locust.conf"]


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

        Returns:
            argparse.Action: the new argparse action
        """
        include_in_web_ui = kwargs.pop("include_in_web_ui", True)
        is_secret = kwargs.pop("is_secret", False)
        action = super().add_argument(*args, **kwargs)
        action.include_in_web_ui = include_in_web_ui
        action.is_secret = is_secret
        return action

    @property
    def args_included_in_web_ui(self) -> Dict[str, configargparse.Action]:
        return {a.dest: a for a in self._actions if hasattr(a, "include_in_web_ui") and a.include_in_web_ui}

    @property
    def secret_args_included_in_web_ui(self) -> Dict[str, configargparse.Action]:
        return {
            a.dest: a
            for a in self._actions
            if a.dest in self.args_included_in_web_ui and hasattr(a, "is_secret") and a.is_secret
        }


def _is_package(path):
    """
    Is the given path a Python package?
    """
    return os.path.isdir(path) and os.path.exists(os.path.join(path, "__init__.py"))


def find_locustfile(locustfile):
    """
    Attempt to locate a locustfile, either explicitly or by searching parent dirs.
    """
    # Obtain env value
    names = [locustfile]
    # Create .py version if necessary
    if not names[0].endswith(".py"):
        names.append(names[0] + ".py")
    # Does the name contain path elements?
    if os.path.dirname(names[0]):
        # If so, expand home-directory markers and test for existence
        for name in names:
            expanded = os.path.expanduser(name)
            if os.path.exists(expanded):
                if name.endswith(".py") or _is_package(expanded):
                    return os.path.abspath(expanded)
    else:
        # Otherwise, start in cwd and work downwards towards filesystem root
        path = os.path.abspath(".")
        while True:
            for name in names:
                joined = os.path.join(path, name)
                if os.path.exists(joined):
                    if name.endswith(".py") or _is_package(joined):
                        return os.path.abspath(joined)
            parent_path = os.path.dirname(path)
            if parent_path == path:
                # we've reached the root path which has been checked this iteration
                break
            path = parent_path
    # Implicit 'return None' if nothing was found


def find_locustfiles(locustfiles: List[str], is_directory: bool) -> List[str]:
    """
    Returns a list of relative file paths for the Locustfile Picker. If is_directory is True,
    locustfiles is expected to have a single index which is a directory that will be searched for
    locustfiles.

    Ignores files that start with _
    Ignores files named locust.py
    """
    file_paths = []

    if is_directory:
        locustdir = locustfiles[0]

        if len(locustfiles) != 1:
            sys.stderr.write(f"Multiple values passed in for directory: {locustfiles}\n")
            sys.exit(1)

        if not os.path.exists(locustdir):
            sys.stderr.write(f"Could not find directory '{locustdir}'\n")
            sys.exit(1)

        if not os.path.isdir(locustdir):
            sys.stderr.write(f"'{locustdir} is not a directory\n")
            sys.exit(1)

        for root, dirs, files in os.walk(locustdir):
            for file in files:
                if not file.startswith("_") and file.lower() != "locust.py" and file.endswith(".py"):
                    file_path = f"{root}/{file}"
                    file_paths.append(file_path)
    else:
        for file_path in locustfiles:
            if not file_path.endswith(".py"):
                sys.stderr.write(f"Invalid file '{file_path}'. File should have '.py' extension\n")
                sys.exit(1)
            if file_path.endswith("locust.py"):
                sys.stderr.write("Invalid file 'locust.py'. File name cannot be 'locust.py'\n")
                sys.exit(1)

            file_paths.append(file_path)

    return file_paths


def get_empty_argument_parser(add_help=True, default_config_files=DEFAULT_CONFIG_FILES) -> LocustArgumentParser:
    parser = LocustArgumentParser(
        default_config_files=default_config_files,
        add_env_var_help=False,
        add_config_file_help=False,
        add_help=add_help,
        formatter_class=configargparse.RawDescriptionHelpFormatter,
        usage=configargparse.SUPPRESS,
        description=textwrap.dedent(
            """
            Usage: locust [OPTIONS] [UserClass ...]

        """
        ),
        # epilog="",
    )
    parser.add_argument(
        "-f",
        "--locustfile",
        default="locustfile",
        help="Python module to import, e.g. '../other_test.py'. Either a .py file, multiple comma-separated .py files or a package "
        "directory. Defaults to 'locustfile'.",
        env_var="LOCUST_LOCUSTFILE",
    )

    parser.add_argument("--config", is_config_file_arg=True, help="Config file path")

    return parser


def parse_locustfile_option(args=None) -> List[str]:
    """
    Construct a command line parser that is only used to parse the -f argument so that we can
    import the test scripts in case any of them adds additional command line arguments to the
    parser

    Returns:
        Locustfiles (List): List of locustfile paths
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

    options, _ = parser.parse_known_args(args=args)

    # Comma separated string to list
    locustfile_as_list = [locustfile.strip() for locustfile in options.locustfile.split(",")]

    # Checking if the locustfile is a single file, multiple files or a directory
    if locustfile_is_directory(locustfile_as_list):
        locustfiles = find_locustfiles(locustfile_as_list, is_directory=True)
        locustfile = None

        if not locustfiles:
            sys.stderr.write(
                f"Could not find any locustfiles in directory '{locustfile_as_list[0]}'. See --help for available options.\n"
            )
            sys.exit(1)
    else:
        if len(locustfile_as_list) > 1:
            # Is multiple files
            locustfiles = find_locustfiles(locustfile_as_list, is_directory=False)
            locustfile = None
        else:
            # Is a single file
            locustfile = find_locustfile(options.locustfile)
            locustfiles = [locustfile]

            if not locustfile:
                if options.help or options.version:
                    # if --help or --version is specified we'll call parse_options which will print the help/version message
                    parse_options(args=args)
                note_about_file_endings = ""
                user_friendly_locustfile_name = options.locustfile
                if options.locustfile == "locustfile":
                    user_friendly_locustfile_name = "locustfile.py"
                elif not options.locustfile.endswith(".py"):
                    note_about_file_endings = (
                        "Ensure your locustfile ends with '.py' or is a directory with locustfiles. "
                    )
                sys.stderr.write(
                    f"Could not find '{user_friendly_locustfile_name}'. {note_about_file_endings}See --help for available options.\n"
                )
                sys.exit(1)

            if locustfile == "locust.py":
                sys.stderr.write(
                    "The locustfile must not be named `locust.py`. Please rename the file and try again.\n"
                )
                sys.exit(1)

    return locustfiles


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
        help="Host to load test in the following format: http://10.21.32.33",
        env_var="LOCUST_HOST",
    )
    parser.add_argument(
        "-u",
        "--users",
        type=int,
        dest="num_users",
        help="Peak number of concurrent Locust users. Primarily used together with --headless or --autostart. Can be changed during a test by keyboard inputs w, W (spawn 1, 10 users) and s, S (stop 1, 10 users)",
        env_var="LOCUST_USERS",
    )
    parser.add_argument(
        "-r",
        "--spawn-rate",
        type=float,
        help="Rate to spawn users at (users per second). Primarily used together with --headless or --autostart",
        env_var="LOCUST_SPAWN_RATE",
    )
    parser.add_argument(
        "--hatch-rate",
        env_var="LOCUST_HATCH_RATE",
        type=float,
        default=0,
        help=configargparse.SUPPRESS,
    )
    parser.add_argument(
        "-t",
        "--run-time",
        help="Stop after the specified amount of time, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with --headless or --autostart. Defaults to run forever.",
        env_var="LOCUST_RUN_TIME",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        dest="list_commands",
        help="Show list of possible User classes and exit",
    )

    web_ui_group = parser.add_argument_group("Web UI options")
    web_ui_group.add_argument(
        "--web-host",
        default="",
        help="Host to bind the web interface to. Defaults to '*' (all interfaces)",
        env_var="LOCUST_WEB_HOST",
    )
    web_ui_group.add_argument(
        "--web-port",
        "-P",
        type=int,
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
        default=None,
        help="Turn on Basic Auth for the web interface. Should be supplied in the following format: username:password",
        env_var="LOCUST_WEB_AUTH",
    )
    web_ui_group.add_argument(
        "--tls-cert",
        default="",
        help="Optional path to TLS certificate to use to serve over HTTPS",
        env_var="LOCUST_TLS_CERT",
    )
    web_ui_group.add_argument(
        "--tls-key",
        default="",
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

    master_group = parser.add_argument_group(
        "Master options",
        "Options for running a Locust Master node when running Locust distributed. A Master node need Worker nodes that connect to it before it can run load tests.",
    )
    # if locust should be run in distributed mode as master
    master_group.add_argument(
        "--master",
        action="store_true",
        help="Set locust to run in distributed mode with this process as master",
        env_var="LOCUST_MODE_MASTER",
    )
    master_group.add_argument(
        "--master-bind-host",
        default="*",
        help="Interfaces (hostname, ip) that locust master should bind to. Only used when running with --master. Defaults to * (all available interfaces).",
        env_var="LOCUST_MASTER_BIND_HOST",
    )
    master_group.add_argument(
        "--master-bind-port",
        type=int,
        default=5557,
        help="Port that locust master should bind to. Only used when running with --master. Defaults to 5557.",
        env_var="LOCUST_MASTER_BIND_PORT",
    )
    master_group.add_argument(
        "--expect-workers",
        type=int,
        default=1,
        help="How many workers master should expect to connect before starting the test (only when --headless/autostart is used).",
        env_var="LOCUST_EXPECT_WORKERS",
    )
    master_group.add_argument(
        "--expect-workers-max-wait",
        type=int,
        default=0,
        help="How long should the master wait for workers to connect before giving up. Defaults to wait forever",
        env_var="LOCUST_EXPECT_WORKERS_MAX_WAIT",
    )

    master_group.add_argument(
        "--expect-slaves",
        action="store_true",
        help=configargparse.SUPPRESS,
    )

    worker_group = parser.add_argument_group(
        "Worker options",
        """Options for running a Locust Worker node when running Locust distributed.
Only the LOCUSTFILE (-f option) needs to be specified when starting a Worker, since other options such as -u, -r, -t are specified on the Master node.""",
    )
    # if locust should be run in distributed mode as worker
    worker_group.add_argument(
        "--worker",
        action="store_true",
        help="Set locust to run in distributed mode with this process as worker",
        env_var="LOCUST_MODE_WORKER",
    )
    worker_group.add_argument(
        "--slave",
        action="store_true",
        help=configargparse.SUPPRESS,
    )
    # master host options
    worker_group.add_argument(
        "--master-host",
        default="127.0.0.1",
        help="Host or IP address of locust master for distributed load testing. Only used when running with --worker. Defaults to 127.0.0.1.",
        env_var="LOCUST_MASTER_NODE_HOST",
        metavar="MASTER_NODE_HOST",
    )
    worker_group.add_argument(
        "--master-port",
        type=int,
        default=5557,
        help="The port to connect to that is used by the locust master for distributed load testing. Only used when running with --worker. Defaults to 5557.",
        env_var="LOCUST_MASTER_NODE_PORT",
        metavar="MASTER_NODE_PORT",
    )

    tag_group = parser.add_argument_group(
        "Tag options",
        "Locust tasks can be tagged using the @tag decorator. These options let specify which tasks to include or exclude during a test.",
    )
    tag_group.add_argument(
        "-T",
        "--tags",
        nargs="*",
        metavar="TAG",
        env_var="LOCUST_TAGS",
        help="List of tags to include in the test, so only tasks with any matching tags will be executed",
    )
    tag_group.add_argument(
        "-E",
        "--exclude-tags",
        nargs="*",
        metavar="TAG",
        env_var="LOCUST_EXCLUDE_TAGS",
        help="List of tags to exclude from the test, so only tasks with no matching tags will be executed",
    )

    stats_group = parser.add_argument_group("Request statistics options")
    stats_group.add_argument(
        "--csv",  # Name repeated in 'parse_options'
        dest="csv_prefix",
        help="Store current request stats to files in CSV format. Setting this option will generate three files: [CSV_PREFIX]_stats.csv, [CSV_PREFIX]_stats_history.csv and [CSV_PREFIX]_failures.csv",
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
        dest="html_file",
        help="Store HTML report to file path specified",
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
        env_var="LOCUST_LOGLEVEL",
    )
    log_group.add_argument(
        "--logfile",
        help="Path to log file. If not set, log will go to stderr",
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
        version=f"locust {version} from {os.path.dirname(__file__)} (python {platform.python_version()})",
    )
    other_group.add_argument(
        "--exit-code-on-error",
        type=int,
        default=1,
        help="Sets the process exit code to use when a test result contain any failure or error",
        env_var="LOCUST_EXIT_CODE_ON_ERROR",
    )
    other_group.add_argument(
        "-s",
        "--stop-timeout",
        action="store",
        dest="stop_timeout",
        default="0",
        help="Number of seconds to wait for a simulated user to complete any executing task before exiting. Default is to terminate immediately. This parameter only needs to be specified for the master process when running Locust distributed.",
        env_var="LOCUST_STOP_TIMEOUT",
    )
    other_group.add_argument(
        "--equal-weights",
        action="store_true",
        default=False,
        dest="equal_weights",
        help="Use equally distributed task weights, overriding the weights specified in the locustfile.",
    )
    other_group.add_argument(
        "--enable-rebalancing",
        action="store_true",
        default=False,
        dest="enable_rebalancing",
        help="Allow to automatically rebalance users if new workers are added or removed during a test run.",
    )

    user_classes_group = parser.add_argument_group("User classes")
    user_classes_group.add_argument(
        "user_classes",
        nargs="*",
        metavar="UserClass",
        help="Optionally specify which User classes that should be used (available User classes can be listed with -l or --list)",
    )


def get_parser(default_config_files=DEFAULT_CONFIG_FILES) -> LocustArgumentParser:
    # get a parser that is only able to parse the -f argument
    parser = get_empty_argument_parser(add_help=True, default_config_files=default_config_files)
    # add all the other supported arguments
    setup_parser_arguments(parser)
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
    help_text: str


def ui_extra_args_dict(args=None) -> Dict[str, UIExtraArgOptions]:
    """Get all the UI visible arguments"""
    locust_args = default_args_dict()

    parser = get_parser()
    all_args = vars(parser.parse_args(args))

    extra_args = {
        k: UIExtraArgOptions(
            default_value=v,
            is_secret=k in parser.secret_args_included_in_web_ui,
            help_text=parser.args_included_in_web_ui[k].help,
        )
        for k, v in all_args.items()
        if k not in locust_args and k in parser.args_included_in_web_ui
    }

    return extra_args


def locustfile_is_directory(locustfiles: List[str]) -> bool:
    """
    If a user passes in a locustfile without a file extension and there is a directory with the same name,
    this function defaults to using the file and will raise a warning.
    In this example, foobar.py will be used:
        ├── src/
        │   ├── foobar.py
        ├── foobar/
        │   ├── locustfile.py

        locust -f foobar
    """
    if len(locustfiles) > 1:
        return False

    locustfile = locustfiles[0]

    # Checking if the locustfile could be both a file and a directory
    if not locustfile.endswith(".py"):
        if os.path.isfile(locustfile) and os.path.isdir(locustfile):
            msg = f"WARNING: Using {locustfile}.py instead of directory {os.path.abspath(locustfile)}\n"
            sys.stderr.write(msg)

            return False

    if os.path.isdir(locustfile):
        return True

    return False
