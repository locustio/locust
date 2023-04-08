import logging
import os
import signal
import sys
import time
import atexit
import inspect
import gevent
import locust
from typing import Dict
from . import log
from .argument_parser import parse_locustfile_option, parse_options
from .env import Environment
from .log import setup_logging, greenlet_exception_logger
from . import stats
from .stats import (
    print_error_report,
    print_percentile_stats,
    print_stats,
    print_stats_json,
    stats_printer,
    stats_history,
)
from .stats import StatsCSV, StatsCSVFileWriter
from .user.inspectuser import print_task_ratio, print_task_ratio_json
from .util.timespan import parse_timespan
from .exception import AuthCredentialsError
from .input_events import input_listener
from .html import get_html_report
from .util.load_locustfile import load_locustfile

version = locust.__version__


def create_environment(
    user_classes,
    options,
    events=None,
    shape_class=None,
    locustfile=None,
    available_user_classes=None,
    available_shape_classes=None,
):
    """
    Create an Environment instance from options
    """
    return Environment(
        locustfile=locustfile,
        user_classes=user_classes,
        shape_class=shape_class,
        events=events,
        host=options.host,
        reset_stats=options.reset_stats,
        parsed_options=options,
        available_user_classes=available_user_classes,
        available_shape_classes=available_shape_classes,
    )


def main():
    # find specified locustfile(s) and make sure it exists, using a very simplified
    # command line parser that is only used to parse the -f option.
    locustfiles = parse_locustfile_option()
    locustfiles_length = len(locustfiles)

    # Grabbing the Locustfile if only one was provided. Otherwise, allowing users to select the locustfile in the UI
    # If --headless or --autostart and multiple locustfiles, all provided UserClasses will be ran
    locustfile = locustfiles[0] if locustfiles_length == 1 else None

    # Importing Locustfile(s) - setting available UserClasses and ShapeClasses to choose from in UI
    user_classes: Dict[str, locust.User] = {}
    available_user_classes = {}
    available_shape_classes = {}
    for _locustfile in locustfiles:
        docstring, _user_classes, shape_class = load_locustfile(_locustfile)

        # Setting Available Shape Classes
        if shape_class:
            shape_class_name = type(shape_class).__name__
            if shape_class_name in available_shape_classes.keys():
                sys.stderr.write(f"Duplicate shape classes: {shape_class_name}\n")
                sys.exit(1)

            available_shape_classes[shape_class_name] = shape_class

        # Setting Available User Classes
        for key, value in _user_classes.items():
            if key in available_user_classes.keys():
                previous_path = inspect.getfile(user_classes[key])
                new_path = inspect.getfile(value)
                if previous_path == new_path:
                    # The same User class was defined in two locustfiles but one probably imported the other, so we just ignore it
                    continue
                else:
                    sys.stderr.write(
                        f"Duplicate user class names: {key} is defined in both {previous_path} and {new_path}\n"
                    )
                    sys.exit(1)

            user_classes[key] = value
            available_user_classes[key] = value

    if len(stats.PERCENTILES_TO_CHART) != 2:
        logging.error("stats.PERCENTILES_TO_CHART parameter should be 2 parameters \n")
        sys.exit(1)

    def is_valid_percentile(parameter):
        try:
            if 0 < float(parameter) < 1:
                return True
            return False
        except ValueError:
            return False

    for percentile in stats.PERCENTILES_TO_CHART:
        if not is_valid_percentile(percentile):
            logging.error(
                "stats.PERCENTILES_TO_CHART parameter need to be float and value between. 0 < percentile < 1 Eg 0.95\n"
            )
            sys.exit(1)
    # parse all command line options
    options = parse_options()

    if options.headful:
        options.headless = False

    if options.slave or options.expect_slaves:
        sys.stderr.write("The --slave/--expect-slaves parameters have been renamed --worker/--expect-workers\n")
        sys.exit(1)

    if options.autoquit != -1 and not options.autostart:
        sys.stderr.write("--autoquit is only meaningful in combination with --autostart\n")
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

    if options.stop_timeout:
        try:
            options.stop_timeout = parse_timespan(options.stop_timeout)
        except ValueError:
            logger.error("Valid --stop-timeout formats are: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.")
            sys.exit(1)

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
            logger.error(f"Unknown User(s): {', '.join(missing)}\n")
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
                f"""System open file limit '{current_open_file_limit}' is below minimum setting '{minimum_open_file_limit}'.
It's not high enough for load testing, and the OS didn't allow locust to increase it by itself.
See https://github.com/locustio/locust/wiki/Installation#increasing-maximum-number-of-open-files-limit for more info."""
            )

    # create locust Environment
    locustfile_path = None if not locustfile else os.path.basename(locustfile)

    environment = create_environment(
        user_classes,
        options,
        events=locust.events,
        shape_class=shape_class,
        locustfile=locustfile_path,
        available_user_classes=available_user_classes,
        available_shape_classes=available_shape_classes,
    )

    if shape_class and (options.num_users or options.spawn_rate):
        logger.warning(
            "The specified locustfile contains a shape class but a conflicting argument was specified: users or spawn-rate. Ignoring arguments"
        )

    if options.show_task_ratio:
        print("\n Task ratio per User class")
        print("-" * 80)
        print_task_ratio(user_classes, options.num_users, False)
        print("\n Total task ratio")
        print("-" * 80)
        print_task_ratio(user_classes, options.num_users, True)
        sys.exit(0)
    if options.show_task_ratio_json:
        print_task_ratio_json(user_classes, options.num_users)
        sys.exit(0)

    if options.master:
        if options.worker:
            logger.error("The --master argument cannot be combined with --worker")
            sys.exit(-1)
        if options.expect_workers_max_wait and not options.expect_workers:
            logger.error("The --expect-workers-max-wait argument only makes sense when combined with --expect-workers")
            sys.exit(-1)
        runner = environment.create_master_runner(
            master_bind_host=options.master_bind_host,
            master_bind_port=options.master_bind_port,
        )
    elif options.worker:
        try:
            runner = environment.create_worker_runner(options.master_host, options.master_port)
            logger.debug("Connected to locust master: %s:%s", options.master_host, options.master_port)
        except OSError as e:
            logger.error("Failed to connect to the Locust master: %s", e)
            sys.exit(-1)
    else:
        runner = environment.create_local_runner()

    # main_greenlet is pointing to runners.greenlet by default, it will point the web greenlet later if in web mode
    main_greenlet = runner.greenlet

    if options.run_time:
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
                logger.info(f"Starting web interface at {protocol}://{web_host}:{options.web_port}")
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
                userclass_picker_is_active=options.class_picker,
            )
        except AuthCredentialsError:
            logger.error("Credentials supplied with --web-auth should have the format: username:password")
            sys.exit(1)
    else:
        web_ui = None

    if options.autostart and options.headless:
        logger.warning("The --autostart argument is implied by --headless, no need to set both.")

    if options.autostart and options.worker:
        logger.warning("The --autostart argument has no meaning on a worker.")

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

    def stop_and_optionally_quit():
        if options.autostart and not options.headless:
            logger.info("--run-time limit reached, stopping test")
            runner.stop()
            if options.autoquit != -1:
                logger.debug("Autoquit time limit set to %s seconds" % options.autoquit)
                time.sleep(options.autoquit)
                logger.info("--autoquit time reached, shutting down")
                runner.quit()
                if web_ui:
                    web_ui.stop()
            else:
                logger.info("--autoquit not specified, leaving web ui running indefinitely")
        else:  # --headless run
            logger.info("--run-time limit reached, shutting down")
            runner.quit()

    def spawn_run_time_quit_greenlet():
        gevent.spawn_later(options.run_time, stop_and_optionally_quit).link_exception(greenlet_exception_handler)

    headless_master_greenlet = None
    stats_printer_greenlet = None
    if not options.only_summary and (options.print_stats or (options.headless and not options.worker)):
        # spawn stats printing greenlet
        stats_printer_greenlet = gevent.spawn(stats_printer(runner.stats))
        stats_printer_greenlet.link_exception(greenlet_exception_handler)

    gevent.spawn(stats_history, runner)

    def start_automatic_run():
        if options.master:
            # wait for worker nodes to connect
            start_time = time.monotonic()
            while len(runner.clients.ready) < options.expect_workers:
                if options.expect_workers_max_wait and options.expect_workers_max_wait < time.monotonic() - start_time:
                    logger.error("Gave up waiting for workers to connect")
                    runner.quit()
                    sys.exit(1)
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
                if options.run_time:
                    sys.stderr.write("It makes no sense to combine --run-time and LoadShapes. Bailing out.\n")
                    sys.exit(1)
                environment.runner.start_shape()
                environment.runner.shape_greenlet.join()
                stop_and_optionally_quit()
            else:
                headless_master_greenlet = gevent.spawn(runner.start, options.num_users, options.spawn_rate)
                headless_master_greenlet.link_exception(greenlet_exception_handler)

        if options.run_time:
            logger.info(f"Run time limit set to {options.run_time} seconds")
            spawn_run_time_quit_greenlet()
        elif not options.worker and not environment.shape_class:
            logger.info("No run time limit set, use CTRL+C to interrupt")

    if options.csv_prefix:
        gevent.spawn(stats_csv_writer.stats_writer).link_exception(greenlet_exception_handler)

    if options.headless:
        start_automatic_run()

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
        # ensure terminal is reset, even if there is an unhandled exception in locust or someone
        # does something wild, like calling sys.exit() in the locustfile
        atexit.register(input_listener_greenlet.kill, block=True)

    def shutdown():
        """
        Shut down locust by firing quitting event, printing/writing stats and exiting
        """
        logger.debug("Running teardowns...")

        if input_listener_greenlet is not None:
            input_listener_greenlet.kill(block=False)

        environment.events.quitting.fire(environment=environment, reverse=True)

        # determine the process exit code
        if environment.process_exit_code is not None:
            code = environment.process_exit_code
        elif len(runner.errors) or len(runner.exceptions):
            code = options.exit_code_on_error
        elif log.unhandled_greenlet_exception:
            code = 2
        else:
            code = 0

        logger.info(f"Shutting down (exit code {code})")

        if stats_printer_greenlet is not None:
            stats_printer_greenlet.kill(block=False)
        if headless_master_greenlet is not None:
            headless_master_greenlet.kill(block=False)
        logger.debug("Cleaning up runner...")
        if runner is not None:
            runner.quit()
        if options.json:
            print_stats_json(runner.stats)
        elif not isinstance(runner, locust.runners.WorkerRunner):
            print_stats(runner.stats, current=False)
            print_percentile_stats(runner.stats)
            print_error_report(runner.stats)

        environment.events.quit.fire(exit_code=code)
        sys.exit(code)

    # install SIGTERM handler
    def sig_term_handler():
        logger.info("Got SIGTERM signal")
        shutdown()

    def save_html_report():
        html_report = get_html_report(environment, show_download_link=False)
        logger.info("writing html report to file: %s", options.html_file)
        with open(options.html_file, "w", encoding="utf-8") as file:
            file.write(html_report)

    gevent.signal_handler(signal.SIGTERM, sig_term_handler)

    try:
        logger.info(f"Starting Locust {version}")
        if options.class_picker:
            logger.info("Locust is running with the UserClass Picker Enabled")
        if options.autostart and not options.headless:
            start_automatic_run()

        main_greenlet.join()
        if options.html_file:
            save_html_report()
    except KeyboardInterrupt:
        if options.html_file:
            save_html_report()
    except Exception:
        raise
    shutdown()
