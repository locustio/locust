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

from .event import Events
from .argument_parser import parse_locustfile_option, parse_options
from .core import HttpLocust, Locust
from .env import Environment
from .inspectlocust import get_task_ratio_dict, print_task_ratio
from .log import console_logger, setup_logging
from .runners import LocalLocustRunner, MasterLocustRunner, WorkerLocustRunner
from .stats import (print_error_report, print_percentile_stats, print_stats,
                    stats_printer, stats_writer, write_stat_csvs)
from .util.timespan import parse_timespan
from .web import WebUI

_internals = [Locust, HttpLocust]
version = locust.__version__


def is_locust(tup):
    """
    Takes (name, object) tuple, returns True if it's a public Locust subclass.
    """
    name, item = tup
    return bool(
        inspect.isclass(item)
        and issubclass(item, Locust)
        and hasattr(item, "task_set")
        and getattr(item, "task_set")
        and not name.startswith('_')
    )


def load_locustfile(path):
    """
    Import given locustfile path and return (docstring, callables).

    Specifically, the locustfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a Locust" test.
    """

    def __import_locustfile__(filename, path):
        """
        Loads the locust file as a module, similar to performing `import`
        """
        source = importlib.machinery.SourceFileLoader(os.path.splitext(locustfile)[0], path)
        return  source.load_module()

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
    imported = __import_locustfile__(locustfile, path)
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]
    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]
    # Return our two-tuple
    locusts = dict(filter(is_locust, vars(imported).items()))
    return imported.__doc__, locusts


def create_environment(options, events=None):
    """
    Create an Environment instance from options
    """
    return Environment(
        events=events,
        host=options.host,
        options=options,
        reset_stats=options.reset_stats,
        step_load=options.step_load,
        stop_timeout=options.stop_timeout,
    )


def main():
    # find specified locustfile and make sure it exists, using a very simplified
    # command line parser that is only used to parse the -f option
    locustfile = parse_locustfile_option()
    
    # import the locustfile
    docstring, locusts = load_locustfile(locustfile)
    
    # parse all command line options
    options = parse_options()

    if options.slave or options.expect_slaves:
        sys.stderr.write("[DEPRECATED] Usage of slave has been deprecated, use --worker or --expect-workers\n")
        sys.exit(1)
    
    # setup logging
    if not options.skip_log_setup:
        setup_logging(options.loglevel, options.logfile)

    logger = logging.getLogger(__name__)

    if options.list_commands:
        console_logger.info("Available Locusts:")
        for name in locusts:
            console_logger.info("    " + name)
        sys.exit(0)

    if not locusts:
        logger.error("No Locust class found!")
        sys.exit(1)

    # make sure specified Locust exists
    if options.locust_classes:
        missing = set(options.locust_classes) - set(locusts.keys())
        if missing:
            logger.error("Unknown Locust(s): %s\n" % (", ".join(missing)))
            sys.exit(1)
        else:
            names = set(options.locust_classes) & set(locusts.keys())
            locust_classes = [locusts[n] for n in names]
    else:
        # list() call is needed to consume the dict_view object in Python 3
        locust_classes = list(locusts.values())
    
    # create locust Environment
    environment = create_environment(options, events=locust.events)
    
    if options.show_task_ratio:
        console_logger.info("\n Task ratio per locust class")
        console_logger.info( "-" * 80)
        print_task_ratio(locust_classes)
        console_logger.info("\n Total task ratio")
        console_logger.info("-" * 80)
        print_task_ratio(locust_classes, total=True)
        sys.exit(0)
    if options.show_task_ratio_json:
        from json import dumps
        task_data = {
            "per_class": get_task_ratio_dict(locust_classes), 
            "total": get_task_ratio_dict(locust_classes, total=True)
        }
        console_logger.info(dumps(task_data))
        sys.exit(0)

    if options.step_time:
        if not options.step_load:
            logger.error("The --step-time argument can only be used together with --step-load")
            sys.exit(1)
        if options.worker:
            logger.error("--step-time should be specified on the master node, and not on worker nodes")
            sys.exit(1)
        try:
            options.step_time = parse_timespan(options.step_time)
        except ValueError:
            logger.error("Valid --step-time formats are: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.")
            sys.exit(1)
    
    if options.master:
        runner = MasterLocustRunner(
            environment, 
            locust_classes,
            master_bind_host=options.master_bind_host,
            master_bind_port=options.master_bind_port,
        )
    elif options.worker:
        try:
            runner = WorkerLocustRunner(
                environment, 
                locust_classes,
                master_host=options.master_host,
                master_port=options.master_port,
            )
        except socket.error as e:
            logger.error("Failed to connect to the Locust master: %s", e)
            sys.exit(-1)
    else:
        runner = LocalLocustRunner(environment, locust_classes)
    
    # main_greenlet is pointing to runners.greenlet by default, it will point the web greenlet later if in web mode
    main_greenlet = runner.greenlet
    
    if options.run_time:
        if not options.no_web:
            logger.error("The --run-time argument can only be used together with --no-web")
            sys.exit(1)
        if options.worker:
            logger.error("--run-time should be specified on the master node, and not on worker nodes")
            sys.exit(1)
        try:
            options.run_time = parse_timespan(options.run_time)
        except ValueError:
            logger.error("Valid --run-time formats are: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.")
            sys.exit(1)
        def spawn_run_time_limit_greenlet():
            logger.info("Run time limit set to %s seconds" % options.run_time)
            def timelimit_stop():
                logger.info("Time limit reached. Stopping Locust.")
                runner.quit()
            gevent.spawn_later(options.run_time, timelimit_stop)
    
    # start Web UI
    if not options.no_web and not options.worker:
        # spawn web greenlet
        logger.info("Starting web monitor at http://%s:%s" % (options.web_host or "*", options.web_port))
        web_ui = WebUI(environment=environment)
        main_greenlet = gevent.spawn(web_ui.start, host=options.web_host, port=options.web_port)
    else:
        web_ui = None
    
    # Fire locust init event which can be used by end-users' code to run setup code that
    # need access to the Environment, Runner or WebUI
    environment.events.init.fire(environment=environment, runner=runner, web_ui=web_ui)    
    
    if options.no_web:
        # headless mode
        if options.master:
            # what for worker nodes to connect
            while len(runner.clients.ready) < options.expect_workers:
                logging.info("Waiting for workers to be ready, %s of %s connected",
                             len(runner.clients.ready), options.expect_workers)
                time.sleep(1)
        if not options.worker:
            # start the test
            if options.step_time:
                runner.start_stepload(options.num_clients, options.hatch_rate, options.step_clients, options.step_time)
            else:
                runner.start(options.num_clients, options.hatch_rate)
    
    if options.run_time:
        spawn_run_time_limit_greenlet()

    stats_printer_greenlet = None
    if not options.only_summary and (options.print_stats or (options.no_web and not options.worker)):
        # spawn stats printing greenlet
        stats_printer_greenlet = gevent.spawn(stats_printer(runner.stats))

    if options.csvfilebase:
        gevent.spawn(stats_writer, runner.stats, options.csvfilebase, options.stats_history_enabled)

    
    def shutdown(code=0):
        """
        Shut down locust by firing quitting event, printing/writing stats and exiting
        """
        logger.info("Shutting down (exit code %s), bye." % code)
        if stats_printer_greenlet is not None:
            stats_printer_greenlet.kill(block=False)
        logger.info("Cleaning up runner...")
        if runner is not None:
            runner.quit()
        logger.info("Running teardowns...")
        environment.events.quitting.fire(reverse=True)
        print_stats(runner.stats, current=False)
        print_percentile_stats(runner.stats)
        if options.csvfilebase:
            write_stat_csvs(runner.stats, options.csvfilebase, options.stats_history_enabled)
        print_error_report(runner.stats)
        sys.exit(code)
    
    # install SIGTERM handler
    def sig_term_handler():
        logger.info("Got SIGTERM signal")
        shutdown(0)
    gevent.signal(signal.SIGTERM, sig_term_handler)
    
    try:
        logger.info("Starting Locust %s" % version)
        main_greenlet.join()
        code = 0
        if len(runner.errors) or len(runner.exceptions):
            code = options.exit_code_on_error
        shutdown(code=code)
    except KeyboardInterrupt as e:
        shutdown(0)
