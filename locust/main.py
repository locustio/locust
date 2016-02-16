import locust
import runners

import gevent
import sys
import os
import signal
import inspect
import logging
import socket
import time
from optparse import OptionParser
from gevent.pool import Group

import web
from log import setup_logging, console_logger
from stats import stats_printer, print_percentile_stats, print_error_report, print_stats
from inspectlocust import print_task_ratio, get_task_ratio_dict
from core import Locust, HttpLocust
from runners import MasterLocustRunner, SlaveLocustRunner, LocalLocustRunner, NoWebMasterLocustRunner
import events

import polling

_internals = [Locust, HttpLocust]
version = locust.version


def parse_options():
    """
    Handle command-line options with optparse.OptionParser.

    Return list of arguments, largely for use in `parse_arguments`.
    """

    # Initialize
    parser = OptionParser(usage="locust [options] [LocustClass [LocustClass2 ... ]]")

    parser.add_option(
        '-H', '--host',
        dest="host",
        default=None,
        help="Host to load test in the following format: http://10.21.32.33"
    )

    parser.add_option(
        '--web-host',
        dest="web_host",
        default="",
        help="Host to bind the web interface to. Defaults to '' (all interfaces)"
    )
    
    parser.add_option(
        '-P', '--port', '--web-port',
        type="int",
        dest="port",
        default=8089,
        help="Port on which to run web host"
    )
    
    parser.add_option(
        '-f', '--locustfile',
        dest='locustfile',
        default='locustfile',
        help="Python module file or directory to import, e.g. '../other.py' or 'locustfiles/'. If directory, "
             "the default locustfile will be the first valid module found in that directory. Default: locustfile"
    )

    # if locust should be run in distributed mode as master
    parser.add_option(
        '--master',
        action='store_true',
        dest='master',
        default=False,
        help="Set locust to run in distributed mode with this process as master"
    )

    # if locust should be run in distributed mode as slave
    parser.add_option(
        '--slave',
        action='store_true',
        dest='slave',
        default=False,
        help="Set locust to run in distributed mode with this process as slave"
    )
    
    # master host options
    parser.add_option(
        '--master-host',
        action='store',
        type='str',
        dest='master_host',
        default="127.0.0.1",
        help="Host or IP address of locust master for distributed load testing. Only used when running with --slave. Defaults to 127.0.0.1."
    )
    
    parser.add_option(
        '--master-port',
        action='store',
        type='int',
        dest='master_port',
        default=5557,
        help="The port to connect to that is used by the locust master for distributed load testing. Only used when running with --slave. Defaults to 5557. Note that slaves will also connect to the master node on this port + 1."
    )

    parser.add_option(
        '--master-bind-host',
        action='store',
        type='str',
        dest='master_bind_host',
        default="*",
        help="Interfaces (hostname, ip) that locust master should bind to. Only used when running with --master. Defaults to * (all available interfaces)."
    )
    
    parser.add_option(
        '--master-bind-port',
        action='store',
        type='int',
        dest='master_bind_port',
        default=5557,
        help="Port that locust master should bind to. Only used when running with --master. Defaults to 5557. Note that Locust will also use this port + 1, so by default the master node will bind to 5557 and 5558."
    )

    parser.add_option(
        '--min-slaves',
        action='store',
        type='int',
        dest='min_slaves',
        default=1,
        help="The minimum number of slaves for the master to expect before it starts swarming. Only used when running with --master and --no-web."
    )

    # if we should print stats in the console
    parser.add_option(
        '--no-web',
        action='store_true',
        dest='no_web',
        default=False,
        help="Disable the web interface, and instead start running the test immediately. Requires -c and -r to be specified."
    )

    # Number of clients
    parser.add_option(
        '-c', '--clients',
        action='store',
        type='int',
        dest='num_clients',
        default=1,
        help="Number of concurrent clients. Only used together with --no-web"
    )

    # Client hatch rate
    parser.add_option(
        '-r', '--hatch-rate',
        action='store',
        type='float',
        dest='hatch_rate',
        default=1,
        help="The rate per second in which clients are spawned. Only used together with --no-web"
    )
    
    # Number of requests
    parser.add_option(
        '-n', '--num-request',
        action='store',
        type='int',
        dest='num_requests',
        default=None,
        help="Number of requests to perform. Only used together with --no-web"
    )

    parser.add_option(
        '-t', '--timeout',
        action='store',
        type='int',
        dest='timeout',
        default=None,
        help="Maximum number of seconds to run each locustfile for. Note that there may be multiple locustfiles and this is not a global timeout."
    )

    parser.add_option(
        '--cooldown',
        action='store',
        type='int',
        dest='cooldown',
        default=0,
        help='Number of seconds to wait before running the next locustfile.'
    )
    
    # log level
    parser.add_option(
        '--loglevel', '-L',
        action='store',
        type='str',
        dest='loglevel',
        default='INFO',
        help="Choose between DEBUG/INFO/WARNING/ERROR/CRITICAL. Default is INFO.",
    )
    
    # log file
    parser.add_option(
        '--logfile',
        action='store',
        type='str',
        dest='logfile',
        default=None,
        help="Path to log file. If not set, log will go to stdout/stderr",
    )
    
    # if we should print stats in the console
    parser.add_option(
        '--print-stats',
        action='store_true',
        dest='print_stats',
        default=False,
        help="Print stats in the console"
    )

    # only print summary stats
    parser.add_option(
       '--only-summary',
       action='store_true',
       dest='only_summary',
       default=False,
       help='Only print the summary stats'
    )
    
    # List locust commands found in loaded locust files/source files
    parser.add_option(
        '-l', '--list',
        action='store_true',
        dest='list_commands',
        default=False,
        help="Show list of possible locust classes and exit"
    )
    
    # Display ratio table of all tasks
    parser.add_option(
        '--show-task-ratio',
        action='store_true',
        dest='show_task_ratio',
        default=False,
        help="print table of the locust classes' task execution ratio"
    )
    # Display ratio table of all tasks in JSON format
    parser.add_option(
        '--show-task-ratio-json',
        action='store_true',
        dest='show_task_ratio_json',
        default=False,
        help="print json data of the locust classes' task execution ratio"
    )
    
    # Version number (optparse gives you --version but we have to do it
    # ourselves to get -V too. sigh)
    parser.add_option(
        '-V', '--version',
        action='store_true',
        dest='show_version',
        default=False,
        help="show program's version number and exit"
    )

    # Finalize
    # Return three-tuple of parser + the output from parse_args (opt obj, args)
    opts, args = parser.parse_args()
    return parser, opts, args


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
        path = '.'
        # Stop before falling off root of filesystem (should be platform
        # agnostic)
        while os.path.split(os.path.abspath(path))[1]:
            for name in names:
                joined = os.path.join(path, name)
                if os.path.exists(joined):
                    if name.endswith('.py') or _is_package(joined):
                        return os.path.abspath(joined)
            path = os.path.join('..', path)
    # Implicit 'return None' if nothing was found


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
    Import given locustfile path and return {module: (callables)}.

    <module> -- the name of the module in which the locusts are contained
    <callables> -- a dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a Locust" test.
    """
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
    # Perform the import (trimming off the .py)
    imported = __import__(os.path.splitext(locustfile)[0])
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]
    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]

    locusts = dict(filter(is_locust, vars(imported).items()))
    return {os.path.splitext(locustfile)[0]: locusts}


def getmodule(path, suffixes=('.py',)):
    """
    Get the relative module name of a file path; return None if not a module or is the __init__ of a package.
    """
    if path.endswith('__init__.py') or path.endswith('__init__.pyc') or path.endswith('__init__.pyo'):
        # This is a package, not a module
        return None

    module = os.path.split(path)[-1]
    for s in suffixes:
        if module.endswith(s):
            return module.strip(s)

    return None


def collect_locustfiles(path):
    """
    On a given directory path, recursively import and load all locustfiles in that directory.
    """
    # Locustfiles will typically import assuming the working path is on the PYTHONPATH. To avoid having to do
    # PYTHONPATH=. locust ...
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

    files = os.listdir(path)
    collected = dict()
    for file_ in files:
        fullpath = os.path.abspath(os.path.join(path, file_))
        if os.path.isfile(fullpath):
            if getmodule(file_):
                loaded = load_locustfile(fullpath)
                if loaded:
                    collected.update(loaded)
        elif os.path.isdir(fullpath):
            # Recurse subdirectories for other locustfiles
            collected.update(collect_locustfiles(os.path.join(path, file_)))

    return collected


def main():
    parser, options, arguments = parse_options()

    # setup logging
    setup_logging(options.loglevel, options.logfile)
    logger = logging.getLogger(__name__)
    
    if options.show_version:
        print "Locust %s" % (version,)
        sys.exit(0)

    if os.path.isdir(options.locustfile):
        all_locustfiles = collect_locustfiles(options.locustfile)
    else:
        locustfile = find_locustfile(options.locustfile)
        if not locustfile:
            logger.error("Could not find any locustfile! Ensure file ends in '.py' and see --help for available options.")
            sys.exit(1)

        all_locustfiles = load_locustfile(locustfile)

    logger.info("All available locustfiles: {}".format(all_locustfiles))

    # Use the first locustfile for the default locusts
    locusts = all_locustfiles.values()[0]

    if options.list_commands:
        console_logger.info("Available Locusts:")
        for name in locusts:
            console_logger.info("    " + name)
        sys.exit(0)

    if not locusts:
        logger.error("No Locust class found!")
        sys.exit(1)

    # make sure specified Locust exists
    if arguments:
        missing = set(arguments) - set(locusts.keys())
        if missing:
            logger.error("Unknown Locust(s): %s\n" % (", ".join(missing)))
            sys.exit(1)
        else:
            names = set(arguments) & set(locusts.keys())
            locust_classes = [locusts[n] for n in names]
    else:
        locust_classes = locusts.values()
    
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

    if options.master and options.no_web and not options.min_slaves:
        logger.error("When running --master and --no-web, you must specify --min-slaves to be available before starting to swarm")
        sys.exit(1)

    if options.master and options.no_web and not (options.timeout or options.num_requests):
        logger.error("When running --master and --no-web, you must specify either --num-request or --timeout to tell the slaves when to stop running each locustfile")
        sys.exit(1)

    if not options.no_web and not options.slave:
        # spawn web greenlet
        logger.info("Starting web monitor at %s:%s" % (options.web_host or "*", options.port))
        main_greenlet = gevent.spawn(web.start, locust_classes, options)

    if options.slave:
        logger.info("Waiting for master to become available")
        try:
            runners.locust_runner = polling.poll(
                lambda: SlaveLocustRunner(locust_classes, options, available_locustfiles=all_locustfiles),
                timeout=60,
                step=1,
                ignore_exceptions=(socket.error,))

        except polling.TimeoutException, e:
            logger.error("Failed to connect to the Locust master: %s", e.last)
            sys.exit(-1)

        main_greenlet = runners.locust_runner.greenlet

    elif options.master:

        if options.no_web:
            # Just start running the suites as soon as the minimum number of slaves come online
            runners.locust_runner = NoWebMasterLocustRunner(locust_classes, options, available_locustfiles=all_locustfiles)

            logger.info("Waiting for {} slaves to become available before swarming".format(options.min_slaves))
            try:
                runners.locust_runner.wait_for_slaves(options.min_slaves, timeout=60)
            except polling.TimeoutException, e:
                logger.error("Minimum expected slaves were never available. Expected {} ({} available)".format(options.min_slaves, e.last))
                sys.exit(1)

            runners.locust_runner.slaves_start_swarming(
                max_num_requests=options.num_requests,
                max_seconds_elapsed=options.timeout)

        else:
            runners.locust_runner = MasterLocustRunner(locust_classes, options, available_locustfiles=all_locustfiles)

        main_greenlet = runners.locust_runner.greenlet
    
    if not options.only_summary and (options.print_stats or (options.no_web and not options.slave)):
        # spawn stats printing greenlet
        gevent.spawn(stats_printer)
    
    def shutdown(code=0):
        """
        Shut down locust by firing quitting event, printing stats and exiting
        """
        logger.info("Shutting down (exit code %s), bye." % code)

        events.quitting.fire()
        print_stats(runners.locust_runner.request_stats)
        print_percentile_stats(runners.locust_runner.request_stats)

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

if __name__ == '__main__':
    main()
