import locust
import core
import runners

import gevent
import sys
import os
import inspect
import time
import logging
import multiprocessing
import random
from optparse import OptionParser

import web
from log import setup_logging, console_logger
from stats import stats_printer, RequestStats, print_percentile_stats, print_error_report, print_stats
from inspectlocust import print_task_ratio, get_task_ratio_dict
from core import Locust, WebLocust
from runners import MasterLocustRunner, SlaveLocustRunner, LocalLocustRunner
import events

_internals = [Locust, WebLocust]
version = locust.version

logger = logging.getLogger(__name__)

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
        '-f', '--locustfile',
        dest='locustfile',
        default='locustfile',
        help="Python module file to import, e.g. '../other.py'. Default: locustfile"
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
    # if locust should be run in distributed mode as slave
    parser.add_option(
        '--slave-process-count',
        action='store',
        type='int',
        dest='slave_process_count',
        default=multiprocessing.cpu_count(),
        help="Set how many processes should be spawned when starting in --slave mode. Defaults to the number of CPU cores in the machine."
    )
    
    # master host options
    parser.add_option(
        '--master-host',
        action='store',
        type='str',
        dest='master_host',
        default="127.0.0.1",
        help="Host or IP adress of locust master for distributed load testing. Only used when running with --slave. Defaults to 127.0.0.1."
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

    # ramp feature enabled option
    parser.add_option(
        '--ramp',
        action='store_true',
        dest='ramp',
        default=False,
        help="Enables the auto tuning ramping feature for finding highest stable client count. NOTE having ramp enabled will add some more overhead for additional stats gathering"
    )
    
    # if the HTTP client should set gzip headers and try to use gzip decoding
    parser.add_option(
        '--gzip',
        action='store_true',
        dest='gzip',
        default=False,
        help="If present, the HTTP client will set request header Accept-Encoding: gzip, and try to gzip decode the response data."
    )
    
    # if we shgould print stats in the console
    parser.add_option(
        '--print-stats',
        action='store_true',
        dest='print_stats',
        default=False,
        help="Print stats in the console"
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
    return (
        inspect.isclass(item)
        and issubclass(item, Locust)
        and (item not in _internals)
        and not name.startswith('_')
    )


def load_locustfile(path):
    """
    Import given locustfile path and return (docstring, callables).

    Specifically, the locustfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
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
    # Return our two-tuple
    locusts = dict(filter(is_locust, vars(imported).items()))
    return imported.__doc__, locusts

def run():
    """
    Called when locust starts after any possible forking action in main()
    has taken place.
    
    Parses options and acts accordingly. I.e. start correct locust runner, 
    list available locusts and exit, etc.
    """
    parser, options, arguments = parse_options()
    
    # setup logging
    setup_logging(options.loglevel, options.logfile)
    
    if options.show_version:
        print "Locust %s" % (version)
        sys.exit(0)

    locustfile = find_locustfile(options.locustfile)
    if not locustfile:
        logger.error("Could not find any locustfile! See --help for available options.")
        sys.exit(1)

    docstring, locusts = load_locustfile(locustfile)

    if options.list_commands:
        print "Available Locusts:"
        for name in locusts:
            print "    " + name
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
    
    # if --master is set, make sure --no-web isn't set
    if options.master and options.no_web:
        logger.error("Locust can not run distributed with the web interface disabled (do not use --no-web and --master together)")
        sys.exit(0)

    if not options.no_web and not options.slave:
        # spawn web greenlet
        logger.info("Starting web monitor on port 8089")
        main_greenlet = gevent.spawn(web.start, locust_classes, options.hatch_rate, options.num_clients, options.num_requests, options.ramp)
    
    # enable/disable gzip in WebLocust's HTTP client
    WebLocust.gzip = options.gzip

    if not options.master and not options.slave:
        runners.locust_runner = LocalLocustRunner(locust_classes, options.hatch_rate, options.num_clients, options.num_requests, options.host)
        # spawn client spawning/hatching greenlet
        if options.no_web:
            runners.locust_runner.start_hatching(wait=True)
            main_greenlet = runners.locust_runner.greenlet
    elif options.master:
        runners.locust_runner = MasterLocustRunner(locust_classes, options.hatch_rate, options.num_clients, num_requests=options.num_requests, host=options.host, master_host=options.master_host)
    elif options.slave:
        runners.locust_runner = SlaveLocustRunner(locust_classes, options.hatch_rate, options.num_clients, num_requests=options.num_requests, host=options.host, master_host=options.master_host)
        main_greenlet = runners.locust_runner.greenlet
    
    if options.ramp:
        import rampstats
        from rampstats import on_request_success, on_report_to_master, on_slave_report
        if options.slave:
            events.report_to_master += on_report_to_master
        if options.master:
            events.slave_report += on_slave_report
        else:
            events.request_success += on_request_success
    
    if options.print_stats or (options.no_web and not options.slave):
        # spawn stats printing greenlet
        gevent.spawn(stats_printer)
    
    try:
        logger.info("Starting Locust %s" % version)
        main_greenlet.join()
    except KeyboardInterrupt, e:
        events.quitting.fire()
        time.sleep(0.2)
        print_stats(runners.locust_runner.request_stats)
        print_percentile_stats(runners.locust_runner.request_stats)
        print_error_report()
        logger.info("Got KeyboardInterrupt. Exiting, bye..")

    sys.exit(0)

def main():
    """
    Checks if locust was started in slave mode and if so forks the process
    in the correct number of child processes and calls run().
    
    If locust wasn't started in slave mode run() will be called.
    """
    parser, options, arguments = parse_options()
    
    if options.slave and options.slave_process_count > 1:
        children = []
        for i in xrange(options.slave_process_count):
            child = os.fork()
            if child:
                children.append(child)
            else:
                # make child processes get unique random numbers
                random.seed(os.urandom(10))
                # run child process
                run()
        
        # setup logging (to get the correct PID in the log messages
        # we must do this after we've forked)
        setup_logging(options.loglevel, options.logfile)
        
        assert len(children) == options.slave_process_count
        logger.info("Forked %i slave processes", options.slave_process_count)
        
        # wait for child processes
        for child in children:
            os.waitpid(child, 0)
        
        logger.info("All child processes dead")
    else:
        run()

if __name__ == '__main__':
    main()
