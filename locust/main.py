import inspect
import logging
import os
import signal
import socket
import sys
import time

import gevent

import locust

from . import events, runners, web
from .parser import parse_options, create_options
from .core import HttpLocust, Locust, TaskSet
from .inspectlocust import get_task_ratio_dict, print_task_ratio
from .log import console_logger, setup_logging
from .runners import LocalLocustRunner, MasterLocustRunner, SlaveLocustRunner
from .stats import (print_error_report, print_percentile_stats, print_stats,
                    stats_printer, stats_writer, write_stat_csvs)
from .util.time import parse_timespan

_internals = [Locust, HttpLocust]
version = locust.__version__


def _is_package(path):
    """
    Is the given path a Python package?
    """
    return (
        os.path.isdir(path)
        and os.path.exists(os.path.join(path, '__init__.py'))
    )


def find_locustfile(locustfile):
    """
    Attempt to locate a locustfile, either explicitly or by searching parent dirs.
    """
    if locustfile is None:
        return None
    # Obtain env value
    names = [locustfile]
    # Create .py version if necessary
    if not names[0].endswith('.py'):
        names += [names[0] + '.py']
    # Does the name contain path elements?
    if os.path.dirname(names[0]):
        # If so, expand home-directory markers and test for existence
        for name in names:
            expanded = os.path.expanduser(name)
            if os.path.exists(expanded):
                if name.endswith('.py') or _is_package(expanded):
                    return os.path.abspath(expanded)
    else:
        # Otherwise, start in cwd and work downwards towards filesystem root
        path = os.path.abspath('.')
        while True:
            for name in names:
                joined = os.path.join(path, name)
                if os.path.exists(joined):
                    if name.endswith('.py') or _is_package(joined):
                        return os.path.abspath(joined)
            parent_path = os.path.dirname(path)
            if parent_path == path:
                # we've reached the root path which has been checked this iteration
                break
            path = parent_path
    # Implicit 'return None' if nothing was found


def is_locust(tup, ignore_prefix='_'):
    """
    Takes (name, object) tuple, returns True if it's a public Locust subclass.
    """
    name, item = tup
    return bool(
        inspect.isclass(item)
        and issubclass(item, Locust)
        and hasattr(item, "task_set")
        and getattr(item, "task_set")
        and not name.startswith(ignore_prefix)
    )


def is_taskset(tup, ignore_prefix='_'):
    """Takes (name, object) tuple, returns True if it's a public TaskSet subclass."""
    name, item = tup
    return bool(
        inspect.isclass(item)
        and issubclass(item, TaskSet)
        and hasattr(item, "tasks")
        and not name.startswith(ignore_prefix)
        and name != 'TaskSet'
    )


def load_filterfile(path, filter_function):
    """
    Import given path and return (docstring, callables) of all clases that pass the test.

    Specifically, the classfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the `filter_function` test.
    """
    # Get directory and locustfile name
    directory, filterfile = os.path.split(path)
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
    # Perform the import (trimming off the .py)
    imported = __import__(os.path.splitext(filterfile)[0])
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]
    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]
    # Return our two-tuple
    classes = dict(filter(filter_function, vars(imported).items()))
    return imported.__doc__, classes


def load_locustfile(path):
    """
    Import given locustfile path and return (docstring, callables).

    Specifically, the locustfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a Locust" test.
    """
    return load_filterfile(path, is_locust)


def load_tasksetfile(path):
    """
    Import given tasksetfile path and return (docstring, callables).

    Specifically, the tasksetfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a TaskSet" test (`is_taskset`).
    """
    return load_filterfile(path, is_taskset)


def run_locust(options, arguments=[], cli_mode=False):
    """Run Locust programmatically.

    A default set of options can be acquired using the `create_options` function with no arguments.
    
    Arguments:
        options (OptionParser): OptionParser object for defining Locust options. Obtain
            by either using the `create_options` function or running `parse_options` on 
            an argv-style list using the locust command-line format. Recommended to use
            `create_options`.
        arguments (list)): List of Locust classes to include from those found.
    """
    # setup logging
    setup_logging(options.loglevel, options.logfile)
    logger = logging.getLogger(__name__)

    def locust_error(message, err_type=ValueError, exit_type=1):
        logger.error(message)
        if not cli_mode:
            raise err_type(message)
        sys.exit(exit_type)
    
    if options.show_version:
        version_text = "Locust %s" % (version,)
        print(version_text)
        if not cli_mode:
            return 0
        sys.exit(0)

    # Either there is a locustfile, there are locust_classes, or both.
    locustfile = find_locustfile(options.locustfile)

    if not hasattr(options,'locust_classes'):
        options.locust_classes=[]

    locusts = {}
    if locustfile:
        if locustfile == "locust.py":
            locust_error("The locustfile must not be named `locust.py`. Please rename the file and try again.")
        docstring, locusts = load_locustfile(locustfile)
    elif not options.locust_classes:
        locust_error("Could not find any locustfile! Ensure file ends in '.py' and see --help for available options.")
    else:
        pass

    for x in options.locust_classes:
        name = x.__name__
        if name in locusts:
            locust_error("Duplicate locust name {}.".format(name))
        locusts[name] = x

    if options.list_commands:
        console_logger.info("Available Locusts:")
        for name in locusts:
            console_logger.info("    " + name)
        if not cli_mode:
            return [name for name in locusts]
        sys.exit(0)

    if not locusts:
        locust_error("No Locust class found!")

    # make sure specified Locust exists
    if arguments:
        missing = set(arguments) - set(locusts.keys())
        if missing:
            locust_error("Unknown Locust(s): %s\n" % (", ".join(missing)))
        else:
            names = set(arguments) & set(locusts.keys())
            locust_classes = [locusts[n] for n in names]
    else:
        # list() call is needed to consume the dict_view object in Python 3
        locust_classes = list(locusts.values())
    
    if options.show_task_ratio:
        console_logger.info("\n Task ratio per locust class")
        console_logger.info( "-" * 80)
        print_task_ratio(locust_classes)
        console_logger.info("\n Total task ratio")
        console_logger.info("-" * 80)
        print_task_ratio(locust_classes, total=True)
        if not cli_mode:
            return 0
        sys.exit(0)
    if options.show_task_ratio_json:
        from json import dumps
        task_data = {
            "per_class": get_task_ratio_dict(locust_classes), 
            "total": get_task_ratio_dict(locust_classes, total=True)
        }
        console_logger.info(dumps(task_data))
        sys.exit(0)
    
    if options.run_time:
        if not options.no_web:
            locust_error("The --run-time argument can only be used together with --no-web")
        try:
            options.run_time = parse_timespan(options.run_time)
        except ValueError:
            locust_error("Valid --run-time formats are: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.")
        def spawn_run_time_limit_greenlet():
            logger.info("Run time limit set to %s seconds" % options.run_time)
            def timelimit_stop():
                logger.info("Time limit reached. Stopping Locust.")
                runners.locust_runner.quit()
            gevent.spawn_later(options.run_time, timelimit_stop)

    if not options.no_web and not options.slave:
        # spawn web greenlet
        logger.info("Starting web monitor at %s:%s" % (options.web_host or "*", options.port))
        main_greenlet = gevent.spawn(web.start, locust_classes, options)
    
    if not options.master and not options.slave:
        runners.locust_runner = LocalLocustRunner(locust_classes, options)
        # spawn client spawning/hatching greenlet
        if options.no_web:
            runners.locust_runner.start_hatching(wait=True)
            main_greenlet = runners.locust_runner.greenlet
        if options.run_time:
            spawn_run_time_limit_greenlet()
    elif options.master:
        runners.locust_runner = MasterLocustRunner(locust_classes, options)
        if options.no_web:
            while len(runners.locust_runner.clients.ready)<options.expect_slaves:
                logging.info("Waiting for slaves to be ready, %s of %s connected",
                             len(runners.locust_runner.clients.ready), options.expect_slaves)
                time.sleep(1)

            runners.locust_runner.start_hatching(options.num_clients, options.hatch_rate)
            main_greenlet = runners.locust_runner.greenlet
            if options.run_time:
                spawn_run_time_limit_greenlet()
    elif options.slave:
        if options.run_time:
            locust_error("--run-time should be specified on the master node, and not on slave nodes")
        try:
            runners.locust_runner = SlaveLocustRunner(locust_classes, options)
            main_greenlet = runners.locust_runner.greenlet
        except socket.error as e:
            socket_err = "Failed to connect to the Locust master: {}".format(e)
            locust_error(socket_err, err_type=socket.error, exit_type=-1)
    
    if not options.only_summary and (options.print_stats or (options.no_web and not options.slave)):
        # spawn stats printing greenlet
        gevent.spawn(stats_printer)

    if options.csvfilebase:
        gevent.spawn(stats_writer, options.csvfilebase)


    def shutdown(code=0):
        """
        Shut down locust by firing quitting event, printing/writing stats and exiting
        """
        logger.info("Shutting down (exit code %s), bye." % code)

        logger.info("Cleaning up runner...")
        if runners.locust_runner is not None:
            runners.locust_runner.quit()
        logger.info("Running teardowns...")
        events.quitting.fire(reverse=True)
        print_stats(runners.locust_runner.request_stats)
        print_percentile_stats(runners.locust_runner.request_stats)
        if options.csvfilebase:
            write_stat_csvs(options.csvfilebase)
        print_error_report()
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
        if len(runners.locust_runner.errors):
            code = 1
        shutdown(code=code)
    except KeyboardInterrupt as e:
        shutdown(0)


def main():
    _, options, arguments = parse_options(sys.argv)
    args = arguments[1:]
    run_locust(options=options, arguments=args, cli_mode=True)


if __name__ == '__main__':
    main()
