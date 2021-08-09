import inspect
import logging
import os
import importlib
import signal
import socket
import sys
import time

import gevent

import locust

from . import log
from .argument_parser import parse_locustfile_option, parse_options
from .env import Environment
from .log import setup_logging, greenlet_exception_logger
from . import stats
from .stats import print_error_report, print_percentile_stats, print_stats, stats_printer, stats_history
from .stats import StatsCSV, StatsCSVFileWriter
from .user import User
from .user.inspectuser import get_task_ratio_dict, print_task_ratio
from .util.timespan import parse_timespan
from .exception import AuthCredentialsError
from .shape import LoadTestShape
from .input_events import input_listener
from .html import get_html_report


version = locust.__version__


def is_user_class(item):
    """
    Check if a variable is a runnable (non-abstract) User class
    """
    return bool(inspect.isclass(item) and issubclass(item, User) and item.abstract is False)


def is_shape_class(item):
    """
    Check if a class is a LoadTestShape
    """
    return bool(
        inspect.isclass(item) and issubclass(item, LoadTestShape) and item.__dict__["__module__"] != "locust.shape"
    )


def load_locustfile(path):
    """
    Import given locustfile path and return (docstring, callables).

    Specifically, the locustfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a Locust" test.
    """

    # Start with making sure the current working dir is in the sys.path
    sys.path.insert(0, os.getcwd())
    # Get directory and locustfile name
    directory, locustfile = os.path.split(path)
    # If the directory isn't in the PYTHONPATH, add it so our import will work
    added_to_path = False
    index = None
    if directory not in sys.path:
        sys.path.insert(0, directory)
        added_to_path = True
    # If the directory IS in the PYTHONPATH, move it to the front temporarily,
    # otherwise other locustfiles -- like Locusts's own -- may scoop the intended
    # one.
    else:
        i = sys.path.index(directory)
        if i != 0:
            # Store index for later restoration
            index = i
            # Add to front, then remove from original position
            sys.path.insert(0, directory)
            del sys.path[i + 1]
    # Perform the import
    source = importlib.machinery.SourceFileLoader(os.path.splitext(locustfile)[0], path)
    imported = source.load_module()
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]
    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]
    # Return our two-tuple
    user_classes = {name: value for name, value in vars(imported).items() if is_user_class(value)}

    # Find shape class, if any, return it
    shape_classes = [value for name, value in vars(imported).items() if is_shape_class(value)]
    if shape_classes:
        shape_class = shape_classes[0]()
    else:
        shape_class = None

    return imported.__doc__, user_classes, shape_class


def create_environment(user_classes, options, events=None, shape_class=None):
    """
    Create an Environment instance from options
    """
    return Environment(
        user_classes=user_classes,
        shape_class=shape_class,
        tags=options.tags,
        exclude_tags=options.exclude_tags,
        events=events,
        host=options.host,
        reset_stats=options.reset_stats,
        stop_timeout=options.stop_timeout,
        parsed_options=options,
    )


def main():
    # find specified locustfile and make sure it exists, using a very simplified
    # command line parser that is only used to parse the -f option
    locustfile = parse_locustfile_option()

    # import the locustfile
    docstring, user_classes, shape_class = load_locustfile(locustfile)

    # parse all command line options
    options = parse_options()

    if options.headful:
        options.headless = False

    if options.slave or options.expect_slaves:
        sys.stderr.write("The --slave/--expect-slaves parameters have been renamed --worker/--expect-workers\n")
        sys.exit(1)

    if options.step_time or options.step_load or options.step_users or options.step_clients:
        sys.stderr.write(
            "The step load feature was removed in Locust 1.3. You can achieve similar results using a LoadTestShape class. See https://docs.locust.io/en/stable/custom-load-shape.html\n"
        )
        sys.exit(1)

    if options.hatch_rate:
        sys.stderr.write("[DEPRECATED] The --hatch-rate parameter has been renamed --spawn-rate\n")
        options.spawn_rate = options.hatch_rate

    # setup logging
    if not options.skip_log_setup:
        if options.loglevel.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            setup_logging(options.loglevel, options.logfile)
        else:
            sys.stderr.write("Invalid --loglevel. Valid values are: DEBUG/INFO/WARNING/ERROR/CRITICAL\n")
            sys.exit(1)

    logger = logging.getLogger(__name__)
    greenlet_exception_handler = greenlet_exception_logger(logger)

    if options.list_commands:
        print("Available Users:")
        for name in user_classes:
            print("    " + name)
        sys.exit(0)

    if not user_classes:
        logger.error("No User class found!")
        sys.exit(1)

    # make sure specified User exists
    if options.user_classes:
        missing = set(options.user_classes) - set(user_classes.keys())
        if missing:
            logger.error("Unknown User(s): %s\n" % (", ".join(missing)))
            sys.exit(1)
        else:
            names = set(options.user_classes) & set(user_classes.keys())
            user_classes = [user_classes[n] for n in names]
    else:
        # list() call is needed to consume the dict_view object in Python 3
        user_classes = list(user_classes.values())

    if os.name != "nt" and not options.master:

        try:
            import resource

            minimum_open_file_limit = 10000
            current_open_file_limit = resource.getrlimit(resource.RLIMIT_NOFILE)[0]

            if current_open_file_limit < minimum_open_file_limit:
                # Increasing the limit to 10000 within a running process should work on at least MacOS.
                # It does not work on all OS:es, but we should be no worse off for trying.
                resource.setrlimit(resource.RLIMIT_NOFILE, [minimum_open_file_limit, resource.RLIM_INFINITY])
        except BaseException:
            logger.warning(
                (
                    f"System open file limit '{current_open_file_limit}' is below minimum setting '{minimum_open_file_limit}'. "
                    "It's not high enough for load testing, and the OS didn't allow locust to increase it by itself. "
                    "See https://github.com/locustio/locust/wiki/Installation#increasing-maximum-number-of-open-files-limit for more info."
                )
            )

    # create locust Environment
    environment = create_environment(user_classes, options, events=locust.events, shape_class=shape_class)

    if shape_class and (options.num_users or options.spawn_rate):
        logger.warning(
            "The specified locustfile contains a shape class but a conflicting argument was specified: users or spawn-rate. Ignoring arguments"
        )

    if options.show_task_ratio:
        print("\n Task ratio per User class")
        print("-" * 80)
        print_task_ratio(user_classes)
        print("\n Total task ratio")
        print("-" * 80)
        print_task_ratio(user_classes, total=True)
        sys.exit(0)
    if options.show_task_ratio_json:
        from json import dumps

        task_data = {
            "per_class": get_task_ratio_dict(user_classes),
            "total": get_task_ratio_dict(user_classes, total=True),
        }
        print(dumps(task_data))
        sys.exit(0)

    if options.master:
        if options.worker:
            logger.error("The --master argument cannot be combined with --worker")
            sys.exit(-1)
        runner = environment.create_master_runner(
            master_bind_host=options.master_bind_host,
            master_bind_port=options.master_bind_port,
        )
    elif options.worker:
        try:
            runner = environment.create_worker_runner(options.master_host, options.master_port)
            logger.debug("Connected to locust master: %s:%s", options.master_host, options.master_port)
        except socket.error as e:
            logger.error("Failed to connect to the Locust master: %s", e)
            sys.exit(-1)
    else:
        runner = environment.create_local_runner()

    # main_greenlet is pointing to runners.greenlet by default, it will point the web greenlet later if in web mode
    main_greenlet = runner.greenlet

    if options.run_time:
        if not options.headless:
            logger.error("The --run-time argument can only be used together with --headless")
            sys.exit(1)
        if options.worker:
            logger.error("--run-time should be specified on the master node, and not on worker nodes")
            sys.exit(1)
        try:
            options.run_time = parse_timespan(options.run_time)
        except ValueError:
            logger.error("Valid --run-time formats are: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.")
            sys.exit(1)

    if options.csv_prefix:
        stats_csv_writer = StatsCSVFileWriter(
            environment, stats.PERCENTILES_TO_REPORT, options.csv_prefix, options.stats_history_enabled
        )
    else:
        stats_csv_writer = StatsCSV(environment, stats.PERCENTILES_TO_REPORT)

    # start Web UI
    if not options.headless and not options.worker:
        # spawn web greenlet
        protocol = "https" if options.tls_cert and options.tls_key else "http"
        try:
            if options.web_host == "*":
                # special check for "*" so that we're consistent with --master-bind-host
                web_host = ""
            else:
                web_host = options.web_host
            if web_host:
                logger.info("Starting web interface at %s://%s:%s" % (protocol, web_host, options.web_port))
            else:
                logger.info(
                    "Starting web interface at %s://0.0.0.0:%s (accepting connections from all network interfaces)"
                    % (protocol, options.web_port)
                )
            web_ui = environment.create_web_ui(
                host=web_host,
                port=options.web_port,
                auth_credentials=options.web_auth,
                tls_cert=options.tls_cert,
                tls_key=options.tls_key,
                stats_csv_writer=stats_csv_writer,
                delayed_start=True,
            )
        except AuthCredentialsError:
            logger.error("Credentials supplied with --web-auth should have the format: username:password")
            sys.exit(1)
    else:
        web_ui = None

    def assign_equal_weights(environment, **kwargs):
        environment.assign_equal_weights()

    if options.equal_weights:
        environment.events.init.add_listener(assign_equal_weights)

    # Fire locust init event which can be used by end-users' code to run setup code that
    # need access to the Environment, Runner or WebUI.
    environment.events.init.fire(environment=environment, runner=runner, web_ui=web_ui)

    if web_ui:
        web_ui.start()
        main_greenlet = web_ui.greenlet

    headless_master_greenlet = None
    if options.headless:
        # headless mode
        if options.master:
            # wait for worker nodes to connect
            while len(runner.clients.ready) < options.expect_workers:
                logging.info(
                    "Waiting for workers to be ready, %s of %s connected",
                    len(runner.clients.ready),
                    options.expect_workers,
                )
                # TODO: Handle KeyboardInterrupt and send quit signal to workers that are started.
                #       Right now, if the user sends a ctrl+c, the master will not gracefully
                #       shutdown resulting in all the already started workers to stay active.
                time.sleep(1)
        if not options.worker:
            # apply headless mode defaults
            if options.num_users is None:
                options.num_users = 1
            if options.spawn_rate is None:
                options.spawn_rate = 1

            # start the test
            if environment.shape_class:
                environment.runner.start_shape()
            else:
                headless_master_greenlet = gevent.spawn(runner.start, options.num_users, options.spawn_rate)
                headless_master_greenlet.link_exception(greenlet_exception_handler)

    def spawn_run_time_limit_greenlet():
        def timelimit_stop():
            logger.info("Time limit reached. Stopping Locust.")
            runner.quit()

        gevent.spawn_later(options.run_time, timelimit_stop).link_exception(greenlet_exception_handler)

    if options.run_time:
        logger.info("Run time limit set to %s seconds" % options.run_time)
        spawn_run_time_limit_greenlet()
    elif options.headless and not options.worker and not environment.shape_class:
        logger.info("No run time limit set, use CTRL+C to interrupt.")
    else:
        pass  # dont log anything - not having a time limit is normal when not running headless

    input_listener_greenlet = None
    if not options.worker:
        # spawn input listener greenlet
        input_listener_greenlet = gevent.spawn(
            input_listener(
                {
                    "w": lambda: runner.start(runner.user_count + 1, 100)
                    if runner.state != "spawning"
                    else logging.warning("Already spawning users, can't spawn more right now"),
                    "W": lambda: runner.start(runner.user_count + 10, 100)
                    if runner.state != "spawning"
                    else logging.warning("Already spawning users, can't spawn more right now"),
                    "s": lambda: runner.start(max(0, runner.user_count - 1), 100)
                    if runner.state != "spawning"
                    else logging.warning("Spawning users, can't stop right now"),
                    "S": lambda: runner.start(max(0, runner.user_count - 10), 100)
                    if runner.state != "spawning"
                    else logging.warning("Spawning users, can't stop right now"),
                },
            )
        )
        input_listener_greenlet.link_exception(greenlet_exception_handler)

    stats_printer_greenlet = None
    if not options.only_summary and (options.print_stats or (options.headless and not options.worker)):
        # spawn stats printing greenlet
        stats_printer_greenlet = gevent.spawn(stats_printer(runner.stats))
        stats_printer_greenlet.link_exception(greenlet_exception_handler)

    if options.csv_prefix:
        gevent.spawn(stats_csv_writer.stats_writer).link_exception(greenlet_exception_handler)

    gevent.spawn(stats_history, runner)

    def shutdown():
        """
        Shut down locust by firing quitting event, printing/writing stats and exiting
        """
        logger.info("Running teardowns...")

        if input_listener_greenlet is not None:
            input_listener_greenlet.kill(block=False)

        environment.events.quitting.fire(environment=environment, reverse=True)

        # determine the process exit code
        if log.unhandled_greenlet_exception:
            code = 2
        elif environment.process_exit_code is not None:
            code = environment.process_exit_code
        elif len(runner.errors) or len(runner.exceptions):
            code = options.exit_code_on_error
        else:
            code = 0

        logger.info("Shutting down (exit code %s), bye." % code)
        if stats_printer_greenlet is not None:
            stats_printer_greenlet.kill(block=False)
        if headless_master_greenlet is not None:
            headless_master_greenlet.kill(block=False)
        logger.info("Cleaning up runner...")
        if runner is not None:
            runner.quit()

        if not isinstance(runner, locust.runners.WorkerRunner):
            print_stats(runner.stats, current=False)
            print_percentile_stats(runner.stats)
            print_error_report(runner.stats)

        sys.exit(code)

    # install SIGTERM handler
    def sig_term_handler():
        logger.info("Got SIGTERM signal")
        shutdown()

    gevent.signal_handler(signal.SIGTERM, sig_term_handler)

    try:
        logger.info("Starting Locust %s" % version)
        main_greenlet.join()
        if options.html_file:
            html_report = get_html_report(environment, show_download_link=False)
            with open(options.html_file, "w", encoding="utf-8") as file:
                file.write(html_report)
        shutdown()
    except KeyboardInterrupt:
        shutdown()
