from __future__ import annotations

import locust

import atexit
import errno
import gc
import importlib.metadata
import inspect
import json
import logging
import os
import signal
import sys
import time
import traceback

import gevent

from . import log, stats
from .argument_parser import parse_locustfile_option, parse_options
from .env import Environment
from .html import get_html_report
from .input_events import input_listener
from .log import greenlet_exception_logger, setup_logging
from .stats import (
    StatsCSV,
    StatsCSVFileWriter,
    print_error_report,
    print_percentile_stats,
    print_stats,
    print_stats_json,
    stats_history,
    stats_printer,
)
from .user.inspectuser import print_task_ratio, print_task_ratio_json
from .util.load_locustfile import load_locustfile
from .util.timespan import parse_timespan

# import external plugins if  installed to allow for registering custom arguments etc
try:
    import locust_plugins  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError as e:
    if e.msg != "No module named 'locust_plugins'":
        raise
try:
    import locust_cloud  # pyright: ignore[reportMissingImports]

    locust_cloud_version = f" (locust-cloud {importlib.metadata.version('locust-cloud')})"
except ModuleNotFoundError as e:
    locust_cloud_version = ""
    if e.msg != "No module named 'locust_cloud'":
        raise

version = locust.__version__

# Options to ignore when using a custom shape class without `use_common_options=True`
# See: https://docs.locust.io/en/stable/custom-load-shape.html#use-common-options
COMMON_OPTIONS = {
    "num_users": "users",
    "spawn_rate": "spawn-rate",
    "run_time": "run-time",
}


def create_environment(
    user_classes,
    options,
    events=None,
    shape_class=None,
    locustfile=None,
    parsed_locustfiles=None,
    available_user_classes=None,
    available_shape_classes=None,
    available_user_tasks=None,
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
        parsed_locustfiles=parsed_locustfiles,
        available_user_classes=available_user_classes,
        available_shape_classes=available_shape_classes,
        available_user_tasks=available_user_tasks,
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
    user_classes: dict[str, locust.User] = {}
    available_user_classes = {}
    available_shape_classes = {}
    available_user_tasks = {}
    shape_class = None
    for _locustfile in locustfiles:
        docstring, _user_classes, shape_classes = load_locustfile(_locustfile)

        # Setting Available Shape Classes
        if shape_classes:
            shape_class = shape_classes[0]
            for shape_class in shape_classes:
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
            available_user_tasks[key] = value.tasks or {}

    if len(stats.PERCENTILES_TO_CHART) > 6:
        logging.error("stats.PERCENTILES_TO_CHART parameter should be a maximum of 6 parameters \n")
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

    for percentile in stats.PERCENTILES_TO_STATISTICS:
        if not is_valid_percentile(percentile):
            logging.error(
                "stats.PERCENTILES_TO_STATISTICS parameter need to be float and value between. 0 < percentile < 1 Eg 0.95\n"
            )
            sys.exit(1)

    # parse all command line options
    options = parse_options()

    if options.headful:
        options.headless = False

    if options.slave or options.expect_slaves:
        sys.stderr.write("The --slave/--expect-slaves parameters have been renamed --worker/--expect-workers\n")
        sys.exit(1)

    if options.web_auth:
        sys.stderr.write(
            "The --web-auth parameters has been replaced with --web-login. See https://docs.locust.io/en/stable/extending-locust.html#authentication for details\n"
        )
        sys.exit(1)

    if options.autoquit != -1 and not options.autostart:
        sys.stderr.write("--autoquit is only meaningful in combination with --autostart\n")
        sys.exit(1)

    if options.hatch_rate:
        sys.stderr.write("--hatch-rate parameter has been renamed --spawn-rate\n")
        sys.exit(1)

    if options.legacy_ui:
        sys.stderr.write("--legacy-ui is no longer supported, remove the parameter to continue\n")
        sys.exit(1)

    # setup logging
    if not options.skip_log_setup:
        if options.loglevel.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            setup_logging(options.loglevel, options.logfile)
        else:
            sys.stderr.write("Invalid --loglevel. Valid values are: DEBUG/INFO/WARNING/ERROR/CRITICAL\n")
            sys.exit(1)

    children = []
    logger = logging.getLogger(__name__)

    logger.info(f"Starting Locust {version}{locust_cloud_version}")

    if options.processes:
        if os.name == "nt":
            sys.stderr.write("--processes is not supported in Windows (except in WSL)\n")
            sys.exit(1)
        if options.processes == -1:
            options.processes = os.cpu_count()
            if not options.processes:
                sys.stderr.write("--processes failed to detect number of cpus!?\n")
                sys.exit(1)
        elif options.processes < -1:
            sys.stderr.write(f"Invalid --processes count {options.processes}\n")
            sys.exit(1)
        elif options.master:
            sys.stderr.write(
                "--master cannot be combined with --processes. Remove --master, as it is implicit as long as --worker is not set.\n"
            )
            sys.exit(1)
        # Optimize copy-on-write-behavior to save some memory (aprx 26MB -> 15MB rss) in child processes
        gc.collect()  # avoid freezing garbage
        if hasattr(gc, "freeze"):
            gc.freeze()  # move all objects to perm gen so ref counts dont get updated
        for _ in range(options.processes):
            if child_pid := gevent.fork():
                children.append(child_pid)
                logging.debug(f"Started child worker with pid #{child_pid}")
            else:
                # child is always a worker, even when it wasn't set on command line
                options.worker = True
                # remove options that dont make sense on worker
                options.run_time = None
                options.autostart = None
                options.csv_prefix = None
                options.html_file = None
                break
        else:
            # we're in the parent process
            if options.worker:
                # ignore the first sigint in parent, and wait for the children to handle sigint
                def sigint_handler(_signal, _frame):
                    if getattr(sigint_handler, "has_run", False):
                        # if parent gets repeated sigint, we kill the children hard
                        for child_pid in children:
                            try:
                                logging.debug(f"Sending SIGKILL to child with pid {child_pid}")
                                os.kill(child_pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass  # process already dead
                            except Exception:
                                logging.error(traceback.format_exc())
                        sys.exit(1)
                    sigint_handler.has_run = True

                signal.signal(signal.SIGINT, sigint_handler)
                exit_code = 0
                # nothing more to do, just wait for the children to exit
                for child_pid in children:
                    _, child_status = os.waitpid(child_pid, 0)
                    child_exit_code = os.waitstatus_to_exitcode(child_status)
                    exit_code = max(exit_code, child_exit_code)
                sys.exit(exit_code)
            else:
                options.master = True
                options.expect_workers = options.processes

                def kill_workers(children):
                    exit_code = 0
                    start_time = time.time()
                    # give children some time to finish up (in case they had an error parsing arguments etc)
                    for child_pid in children[:]:
                        while time.time() < start_time + 3:
                            try:
                                _, child_status = os.waitpid(child_pid, os.WNOHANG)
                                children.remove(child_pid)
                                child_exit_code = os.waitstatus_to_exitcode(child_status)
                                exit_code = max(exit_code, child_exit_code)
                            except OSError as e:
                                if e.errno == errno.EINTR:
                                    time.sleep(0.1)
                                else:
                                    logging.error(traceback.format_exc())
                            else:
                                break
                    for child_pid in children:
                        try:
                            logging.debug(f"Sending SIGINT to child with pid {child_pid}")
                            os.kill(child_pid, signal.SIGINT)
                        except ProcessLookupError:
                            pass  # never mind, process was already dead
                    for child_pid in children:
                        _, child_status = os.waitpid(child_pid, 0)
                        child_exit_code = os.waitstatus_to_exitcode(child_status)
                        exit_code = max(exit_code, child_exit_code)
                    if exit_code > 1:
                        logging.error(f"Bad response code from worker children: {exit_code}")
                    # ensure master doesn't finish until output from workers has arrived
                    # otherwise the terminal might look weird.
                    time.sleep(0.1)

                atexit.register(kill_workers, children)

    greenlet_exception_handler = greenlet_exception_logger(logger)

    if sys.version_info < (3, 10):
        logger.warning("Python 3.9 support is deprecated and will be removed soon")

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
        if missing := set(options.user_classes) - set(user_classes.keys()):
            logger.error(f"Unknown User(s): {', '.join(missing)}\n")
            sys.exit(1)
        else:
            names = set(options.user_classes) & set(user_classes.keys())
            user_classes = [user_classes[n] for n in names]
    else:
        # list() call is needed to consume the dict_view object in Python 3
        user_classes = list(user_classes.values())

    if not shape_class and options.num_users:
        fixed_count_total = sum([user_class.fixed_count for user_class in user_classes])
        if fixed_count_total > options.num_users:
            logger.info(
                f"Total fixed_count of User classes ({fixed_count_total}) is greater than the specified number of users ({options.num_users}), so not all will be spawned."
            )

    if os.name != "nt" and not options.master:
        try:
            import resource

            minimum_open_file_limit = 10000
            (soft_limit, hard_limit) = resource.getrlimit(resource.RLIMIT_NOFILE)

            if soft_limit < minimum_open_file_limit:
                # Increasing the limit to 10000 within a running process should work on at least MacOS.
                # It does not work on all OS:es, but we should be no worse off for trying.
                resource.setrlimit(resource.RLIMIT_NOFILE, [minimum_open_file_limit, hard_limit])
        except BaseException:
            logger.warning(
                f"""System open file limit '{soft_limit} is below minimum setting '{minimum_open_file_limit}'.
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
        parsed_locustfiles=locustfiles,
        available_user_classes=available_user_classes,
        available_shape_classes=available_shape_classes,
        available_user_tasks=available_user_tasks,
    )

    if options.config_users:
        for json_user_config in options.config_users:
            try:
                if json_user_config.endswith(".json"):
                    with open(json_user_config) as file:
                        user_config = json.load(file)
                else:
                    user_config = json.loads(json_user_config)

                def ensure_user_class_name(config):
                    if "user_class_name" not in config:
                        logger.error("The user config must specify a user_class_name")
                        sys.exit(-1)

                if isinstance(user_config, list):
                    for config in user_config:
                        ensure_user_class_name(config)

                        environment.update_user_class(config)
                else:
                    ensure_user_class_name(user_config)

                    environment.update_user_class(user_config)
            except json.decoder.JSONDecodeError as e:
                logger.error(f"The --config-users argument must be in valid JSON string or file: {e}")
                sys.exit(-1)
            except KeyError as e:
                logger.error(
                    f"Error applying user config, probably you tried to specify config for a User not present in your locustfile: {e}"
                )
                sys.exit(-1)
            except Exception as e:
                logger.exception(e)
                sys.exit(-1)

    if (
        shape_class
        and not shape_class.use_common_options
        and any(getattr(options, opt, None) for opt in COMMON_OPTIONS)
    ):
        logger.warning(
            "--run-time, --users or --spawn-rate have no impact on LoadShapes unless the shape class explicitly reads them. "
            "See: docs.locust.io/en/stable/custom-load-shape.html#use-common-options"
        )
        ignored = [f"--{arg}" for opt, arg in COMMON_OPTIONS.items() if getattr(options, opt, None)]
        logger.warning(f"The following option(s) will be ignored: {', '.join(ignored)}")

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
        if options.expect_workers < 1:
            logger.error(f"Invalid --expect-workers argument ({options.expect_workers}), must be a positive number")
            sys.exit(-1)
        runner = environment.create_master_runner(
            master_bind_host=options.master_bind_host,
            master_bind_port=options.master_bind_port,
        )
    elif options.worker:
        try:
            runner = environment.create_worker_runner(options.master_host, options.master_port)
            logger.debug(
                "Connected to locust master: %s:%s%s", options.master_host, options.master_port, options.web_base_path
            )
        except OSError as e:
            logger.error("Failed to connect to the Locust master: %s", e)
            sys.exit(-1)
    else:
        runner = environment.create_local_runner()

    # main_greenlet is pointing to runners.greenlet by default, it will point the web greenlet later if in web mode
    main_greenlet = runner.greenlet

    if options.run_time:
        if options.worker:
            logger.info("--run-time specified for a worker node will be ignored.")
        try:
            options.run_time = parse_timespan(options.run_time)
        except ValueError:
            logger.error(
                f"Invalid --run-time argument ({options.run_time}), accepted formats are for example 120, 120s, 2m, 3h, 3h30m10s."
            )
            sys.exit(1)

    if options.csv_prefix:
        base_csv_file = os.path.basename(options.csv_prefix)
        base_csv_dir = options.csv_prefix[: -len(base_csv_file)]
        if not os.path.exists(base_csv_dir) and len(base_csv_dir) != 0:
            os.makedirs(base_csv_dir)
        stats_csv_writer = StatsCSVFileWriter(
            environment, stats.PERCENTILES_TO_REPORT, options.csv_prefix, options.stats_history_enabled
        )
    else:
        stats_csv_writer = StatsCSV(environment, stats.PERCENTILES_TO_REPORT)

    # start Web UI
    if not options.headless and not options.worker:
        protocol = "https" if options.tls_cert and options.tls_key else "http"

        if options.web_base_path and options.web_base_path[0] != "/":
            logger.error(
                f"Invalid format for --web-base-path argument ({options.web_base_path}): the url path must start with a slash."
            )
            sys.exit(1)
        if options.web_host == "*":
            # special check for "*" so that we're consistent with --master-bind-host
            web_host = ""
        else:
            web_host = options.web_host
        if web_host:
            logger.info(f"Starting web interface at {protocol}://{web_host}:{options.web_port}{options.web_base_path}")
        if options.web_host_display_name:
            logger.info(f"Starting web interface at {options.web_host_display_name}")
        else:
            if os.name == "nt":
                logger.info(
                    f"Starting web interface at {protocol}://localhost:{options.web_port}{options.web_base_path} (accepting connections from all network interfaces)"
                )
            else:
                logger.info(f"Starting web interface at {protocol}://0.0.0.0:{options.web_port}{options.web_base_path}")

        web_ui = environment.create_web_ui(
            host=web_host,
            port=options.web_port,
            web_base_path=options.web_base_path,
            web_login=options.web_login,
            tls_cert=options.tls_cert,
            tls_key=options.tls_key,
            stats_csv_writer=stats_csv_writer,
            delayed_start=True,
            userclass_picker_is_active=options.class_picker,
            build_path=options.build_path,
        )
    else:
        web_ui = None

    if options.autostart and options.headless:
        logger.info("The --autostart argument is implied by --headless, no need to set both.")

    if options.autostart and options.worker:
        logger.info("The --autostart argument has no meaning on a worker.")

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
                try:
                    environment.runner.start_shape()
                    environment.runner.shape_greenlet.join()
                except KeyboardInterrupt:
                    logging.info("Exiting due to CTRL+C interruption")
                finally:
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
