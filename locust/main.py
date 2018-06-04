import inspect
import logging
import os
import signal
import socket
import sys
import time
from optparse import OptionParser

import gevent

import locust

from . import events, runners, web
from .core import HttpLocust, Locust
from .inspectlocust import get_task_ratio_dict, print_task_ratio
from .log import console_logger, setup_logging
from .runners import LocalLocustRunner, MasterLocustRunner, SlaveLocustRunner
from .stats import (print_error_report, print_percentile_stats, print_stats,
                    stats_printer, stats_writer, write_stat_csvs)
from .util.time import parse_timespan

_internals = [Locust, HttpLocust]
version = locust.__version__

def create_parser():
    """Create parser object used for defining all options for Locust.
    
    Returns:
        OptionParser: OptionParser object used in *parse_options*.
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
        help="Python module file to import, e.g. '../other.py'. Default: locustfile"
    )

    # A file that contains the current request stats.
    parser.add_option(
        '--csv', '--csv-base-name',
        action='store',
        type='str',
        dest='csvfilebase',
        default=None,
        help="Store current request stats to files in CSV format.",
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
        '--expect-slaves',
        action='store',
        type='int',
        dest='expect_slaves',
        default=1,
        help="How many slaves master should expect to connect before starting the test (only when --no-web used)."
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
        help="Number of concurrent Locust users. Only used together with --no-web"
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
    
    # Time limit of the test run
    parser.add_option(
        '-t', '--run-time',
        action='store',
        type='str',
        dest='run_time',
        default=None,
        help="Stop after the specified amount of time, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with --no-web"
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
       help="Only print the summary stats"
    )

    parser.add_option(
        '--no-reset-stats',
        action='store_true',
        help="[DEPRECATED] Do not reset statistics once hatching has been completed. This is now the default behavior. See --reset-stats to disable",
    )

    parser.add_option(
        '--reset-stats',
        action='store_true',
        dest='reset_stats',
        default=False,
        help="Reset statistics once hatching has been completed. Should be set on both master and slaves when running in distributed mode",
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
    return parser


def create_options(
        locustfile='locustfile',
        host=None,
        locust_classes=[], 
        port=8089,
        web_host='',
        no_reset_stats=None,
        reset_stats=False,
        no_web=False,
        run_time=None,
        num_clients=1,
        hatch_rate=1,
        master=False,
        expect_slaves=1,
        master_bind_host='*',
        master_bind_port=5557,
        slave=False,
        master_host='127.0.0.1',
        master_port=5557,
        csvfilebase=None,
        print_stats=False,
        only_summary=False,
        show_task_ratio=False,
        show_task_ratio_json=False,
        logfile=None,
        loglevel='INFO',
        show_version=False,
        list_commands=False):
    """Create options objects for passing to `run_locust` when running Locust programmatically.
    
    Keyword Arguments:
        locustfile (str): Python module file to import, e.g. '../other.py'. (default 'locustfile')
        host (str): Host to load test in the following format: http://10.21.32.33 (default: None)
        locust_classes (list): Locust class callables if not importing from file (default: [])
        port (int): Port on which to run web host (default: 8089)
        web_host (str): Host to bind the web interface to. (default: '' (all interfaces))
        reset_stats (bool): Reset statistics once hatching has been completed. Should be set on both master and slaves when running in distributed mode (default: False)
        no_web (bool): Disable the web interface, and instead start running the test immediately. Requires num_clients and hatch_rate to be specified. (default: False)
        run_time (str): Stop after the specified amount of time, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with:no-web (default: None)
        num_clients (int): Number of concurrent Locust users. Only used together with no_web (default: 1)
        hatch_rate (int): The rate per second in which clients are spawned. Only used together with:no-web (default: 1)
        master (bool): Set locust to run in distributed mode with this process as master (default: False)
        expect_slaves (int): How many slaves master should expect to connect before starting the test (only when no_web used). (default: 1)
        master_bind_host (str): Interfaces (hostname, ip) that locust master should bind to. Only used when running with master. Defaults all available interfaces. (default: '*')
        master_bind_port (int): Port that locust master should bind to. Only used when running with:master. Note that Locust will also use this port + 1, so by default the master node will bind to 5557 and 5558. (default: 5557)
        slave (bool): Set locust to run in distributed mode with this process as slave (default: False)
        master_host (str): Host or IP address of locust master for distributed load testing. Only used when running with slave. (default: '127.0.0.1')
        master_port (int): The port to connect to that is used by the locust master for distributed load testing. Only used when running with:slave. Note that slaves will also connect to the master node on this port + 1. (default: 5557)
        csvfilebase (str): Store current request stats to files in CSV format. (default: None)
        print_stats (bool): Print stats in the console (default: False)
        only_summary (bool): Only print the summary stats (default: False)
        show_task_ratio (bool): print table of the locust classes' task execution ratio (default: False)
        show_task_ratio_json (bool): print json data of the locust classes' task execution ratio (default: False)
        logfile (str): Path to log file. If not set, log will go to stdout/stderr (default: None)
        loglevel (str): Choose between DEBUG/INFO/WARNING/ERROR/CRITICAL. (default: 'INFO')
        show_version (bool): show program's version number and exit (default: False)
        list_commands (bool): Return list of possible locust classes and exit (default: False)
    
    """


    opts,_ = create_parser().parse_args([])
    opts.locustfile = locustfile
    opts.host=host
    opts.locust_classes=locust_classes # Locust class {name:callables, ...} if not loading from file path

    # web interface
    opts.port=port
    opts.web_host=web_host

    # No web
    opts.no_web=no_web
    opts.run_time=run_time
    opts.num_clients=num_clients
    opts.hatch_rate=hatch_rate

    # Distributed settings
    # Master settings
    opts.master=master
    opts.expect_slaves=expect_slaves
    opts.master_bind_host=master_bind_host
    opts.master_bind_port=master_bind_port
    # Slave settings
    opts.slave=slave
    opts.master_host=master_host
    opts.master_port=master_port

    # Output settings
    opts.reset_stats=reset_stats
    opts.csvfilebase=csvfilebase
    opts.print_stats=print_stats
    opts.only_summary=only_summary
    opts.show_task_ratio=show_task_ratio
    opts.show_task_ratio_json=show_task_ratio_json
    opts.logfile=logfile
    opts.loglevel=loglevel

    # Miscellaneous
    opts.show_version=show_version
    opts.list_commands=list_commands

    return opts


def parse_options(args=sys.argv):
    """
    Handle command-line options with optparse.OptionParser.

    Return list of arguments, largely for use in `parse_arguments`.
    """
    parser = create_parser()
    # Return three-tuple of parser + the output from parse_args (opt obj, args)
    opts, args = parser.parse_args(args)
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
