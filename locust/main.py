import locust
import core

import gevent
import sys
import os
import inspect
import time
import logging
from optparse import OptionParser

import web
import inspectlocust
from log import setup_logging
from locust.stats import stats_printer, RequestStats, print_percentile_stats, print_error_report, print_stats
from core import Locust, WebLocust, MasterLocustRunner, SlaveLocustRunner, LocalLocustRunner

_internals = [Locust, WebLocust]
version = locust.version

def parse_options():
    """
    Handle command-line options with optparse.OptionParser.

    Return list of arguments, largely for use in `parse_arguments`.
    """

    # Initialize
    parser = OptionParser(usage="locust [options] [LocustClass [LocustClassN]] ...")

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

    # Version number (optparse gives you --version but we have to do it
    # ourselves to get -V too. sigh)
    parser.add_option(
        '-V', '--version',
        action='store_true',
        dest='show_version',
        default=False,
        help="show program's version number and exit"
    )

    # List locust commands found in loaded locust files/source files
    parser.add_option(
        '-l', '--list',
        action='store_true',
        dest='list_commands',
        default=False,
        help="print list of possible commands and exit"
    )
    
    # Display ratio table of all tasks
    parser.add_option(
        '--show-task-ratio',
        action='store_true',
        dest='show_task_ratio',
        default=False,
        help="print table of the locust classes' task execution ratio"
    )
    parser.add_option(
        '--show-task-ratio-confluence',
        action='store_true',
        dest='show_task_ratio_confluence',
        default=False,
        help="print the locust classes' task execution ratio in confluence list markup"
    )

    # if we shgould print stats in the console
    parser.add_option(
        '--print-stats',
        action='store_true',
        dest='print_stats',
        default=False,
        help="Print stats in the console"
    )

    # if we should print stats in the console
    parser.add_option(
        '--web',
        action='store_true',
        dest='web',
        default=False,
        help="Enable the web monitor (port 8089)"
    )
    
    # if the HTTP client should set gzip headers and try to use gzip decoding
    parser.add_option(
        '--gzip',
        action='store_true',
        dest='gzip',
        default=False,
        help="If present, the HTTP client will set request header Accept-Encoding: gzip, and try to gzip decode the response data."
    )

    # if locust should be run in distributed mode as master
    parser.add_option(
        '--master',
        action='store_true',
        dest='master',
        default=False,
        help="Set locust to run in distributed mode with this process as master. This option will implicitly activate the --web option."
    )

    # if locust should be run in distributed mode as slave
    parser.add_option(
        '--slave',
        action='store_true',
        dest='slave',
        default=False,
        help="Set locust to run in distributed mode with this process as slave"
    )

    # Number of requests
    parser.add_option(
        '-n', '--num-request',
        action='store',
        type='int',
        dest='num_requests',
        default=None,
        help="Number of requests to perform"
    )

    # Number of clients
    parser.add_option(
        '-c', '--clients',
        action='store',
        type='int',
        dest='num_clients',
        default=1,
        help="Number of concurrent clients"
    )

    # Client hatch rate
    parser.add_option(
        '-r', '--hatch-rate',
        action='store',
        type='float',
        dest='hatch_rate',
        default=1,
        help="The rate per second in which clients are spawned"
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

def main():
    parser, options, arguments = parse_options()
    #print "Options:", options, dir(options)
    #print "Arguments:", arguments
    #print "largs:", parser.largs
    #print "rargs:", parser.rargs
    
    # setup logging
    setup_logging(options.loglevel, options.logfile)
    logger = logging.getLogger(__name__)
    
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
        print "\n Task ratio per locust class"
        print "-" * 80
        inspectlocust.print_task_ratio(locust_classes)
        print "\n Total task ratio"
        print "-" * 80
        inspectlocust.print_task_ratio(locust_classes, total=True)
        sys.exit(0)
    
    if options.show_task_ratio_confluence:
        print "\nh1. Task ratio per locust class"
        print
        inspectlocust.print_task_ratio_confluence(locust_classes)
        print "\nh1. Total task ratio"
        print
        inspectlocust.print_task_ratio_confluence(locust_classes, total=True)
        sys.exit(0)
    
    # if --master is set, implicitly set --web
    if options.master:
        options.web = True

    if options.web and not options.slave:
        # spawn web greenlet
        logger.info("Starting web monitor on port 8089")
        main_greenlet = gevent.spawn(web.start, locust_classes, options.hatch_rate, options.num_clients, options.num_requests, options.ramp)
    
    # enable/disable gzip in WebLocust's HTTP client
    WebLocust.gzip = options.gzip

    if not options.master and not options.slave:
        core.locust_runner = LocalLocustRunner(locust_classes, options.hatch_rate, options.num_clients, options.num_requests, options.host)
        # spawn client spawning/hatching greenlet
        if not options.web:
            core.locust_runner.start_hatching(wait=True)
            main_greenlet = core.locust_runner.greenlet
    elif options.master:
        core.locust_runner = MasterLocustRunner(locust_classes, options.hatch_rate, options.num_clients, num_requests=options.num_requests, host=options.host, master_host=options.master_host)
    elif options.slave:
        core.locust_runner = SlaveLocustRunner(locust_classes, options.hatch_rate, options.num_clients, num_requests=options.num_requests, host=options.host, master_host=options.master_host)
        main_greenlet = core.locust_runner.greenlet
    
    if options.ramp:
        import rampstats
        from rampstats import on_request_success, on_report_to_master, on_slave_report
        import events
        if options.slave:
            events.report_to_master += on_report_to_master
        if options.master:
            events.slave_report += on_slave_report
        else:
            events.request_success += on_request_success
    
    if options.print_stats or (not options.web and not options.slave):
        # spawn stats printing greenlet
        gevent.spawn(stats_printer)
    
    try:
        logger.info("Starting Locust %s" % version)
        main_greenlet.join()
    except KeyboardInterrupt, e:
        time.sleep(0.2)
        print_stats(core.locust_runner.request_stats)
        print_percentile_stats(core.locust_runner.request_stats)
        print_error_report()
        logger.info("Got KeyboardInterrupt. Exiting, bye..")

    sys.exit(0)

if __name__ == '__main__':
    main()
