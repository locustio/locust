import locust
from . import runners

import gevent
import sys
import os
import time #to wait for slave in CLI distributed test
import signal
import inspect
import logging
import socket
import json #for dumping/loading json into/from file
from optparse import OptionParser

from . import stats_request_web
from . import web
from .log import setup_logging, console_logger
from .stats import stats_printer, print_percentile_stats, print_error_report, print_stats
from .stats import stats_report #import for plotter in CLI
from .inspectlocust import print_task_ratio, get_task_ratio_dict
from .core import Locust, HttpLocust
from .runners import MasterLocustRunner, SlaveLocustRunner, LocalLocustRunner
from . import events

_internals = [Locust, HttpLocust]
version = locust.__version__

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

    #Username
    parser.add_option(
        '-u', '--username',
        dest="username",
        default='',
        help="Username using which test is to be done"
    )

    #Password
    parser.add_option(
        '-p', '--password',
        dest="password",
        default='',
        help="Password of the Username mentioned"
    )

    #Json Data File
    parser.add_option(
        '-d', '--data-file',
        dest="data_file",
        default='',
        help="path of data_file that contains data for Load Test"
    )

    #maximum user wait
    parser.add_option(
        '--max-wait',
        dest="max_wait",
        default='',
        help="maximum wait time of user to make request"
    )

    #minimum user wait
    parser.add_option(
        '--min-wait',
        dest="min_wait",
        default='',
        help="minimum wait time of user to make request"
    )

    #stop_timeout for locust to terminate
    parser.add_option(
        '--stop-timeout',
        dest="stop_timeout",
        default='',
        help="Time after which locust will stop"
    )

    #to get the number of expected Slaves
    parser.add_option(
        '--expected-slave-count',
        action='store',
        type='int',
        dest='num_slave',
        default=1,
        help='How many number of slaves, master should expect to connect before it can start the test (only when --no-web & --master used together)'
    )

    # Finalize
    # Return three-tuple of parser + the output from parse_args (opt obj, args)
    opts, args = parser.parse_args()
    return parser, opts, args

def load_sher_data(logger):
    sher = {}
    load = {}

    try:
        json_files = [".\\locust_JSON\\" + files for files in os.listdir('.\\locust_JSON') if files.endswith('.json')]
        for files in json_files:
            data=open(files).read()
            data = json.loads(data)
            #print data
            tool_id = data['tools_input']['tool']
            sher['' + tool_id] = {}
            sher[''+ tool_id]['tools_get'] = data['tools_get']
            sher[''+ tool_id]['tools_input'] = data['tools_input']
            sher[''+ tool_id]['sherlock'] = data['sherlock']

        load['sher'] = sher
        return load
    except Exception:
        logger.error('Data required for Sherlock not available at destination')
        sys.exit(1)


#To generate the Json File with data required for load test
def generate_json(options, logger):
    user = options.username
    passwd = options.password
    min_wait = options.min_wait
    max_wait = options.max_wait
    stop_timeout = options.stop_timeout
    login = {}
    load = {}
    data = {}
    if user=='' or passwd=='':
        logger.error("Username (-u/--username) and Password (-p/--password) are required to start the test")
        sys.exit(1)
    file_name = options.data_file
    if file_name == '':
        logger.error("file with the load test data (-d/--data-file) is required to start the test")
        sys.exit(1)
    try:
        if file_name == 'sherlock':
            data = load_sher_data(logger)
        elif not file_name.endswith('.json'):
            logger.error("Input is not a json file! ensure that file neds with ''.json'")
            sys.exit(1)
        else:
            json_data=open(file_name).read()
            data = json.loads(json_data)
        login['user'] = user
        login['password'] = passwd
        if min_wait != '':
            load['min_wait'] = min_wait
        if max_wait != '':
            load['max_wait'] = max_wait
        if stop_timeout != '':
            load['stop_timeout'] = stop_timeout
        data['load'] = load
        data['login'] = login
        with open('Tester.json', 'w') as locust:
            json.dump(data, locust)
    except IOError: #input file doesnot exist
        logger.error("File doesnot exist in the mentioned path! Ensure that the File Exist in mentioned location")
        sys.exit(1)

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

    # setup logging
    setup_logging(options.loglevel, options.logfile)
    logger = logging.getLogger(__name__)

    #get CLI data for load test --> json into a file
    generate_json(options, logger)

    if options.show_version:
        print("Locust %s" % (version,))
        sys.exit(0)

    locustfile = find_locustfile(options.locustfile)
    if not locustfile:
        logger.error("Could not find any locustfile! Ensure file ends in '.py' and see --help for available options.")
        sys.exit(1)

    docstring, locusts = load_locustfile(locustfile)

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

    # if --master is set, make sure --no-web isn't set
    #if options.master and options.no_web:
    #    logger.error("Locust can not run distributed with the web interface disabled (do not use --no-web and --master together)")
    #    sys.exit(0)

    if not options.no_web and not options.slave:
        # spawn web greenlet
        logger.info("Starting web monitor at %s:%s" % (options.web_host or "*", options.port))
        main_greenlet = gevent.spawn(web.start, locust_classes, options)

    if options.no_web and not options.slave:
        main_greenlet = gevent.spawn(stats_request_web.start, options)

    if not options.master and not options.slave:
        runners.locust_runner = LocalLocustRunner(locust_classes, options)
        # spawn client spawning/hatching greenlet
        if options.no_web:
            gevent.sleep(2) #me
            runners.locust_runner.start_hatching(wait=True)
            main_greenlet = runners.locust_runner.greenlet
    elif options.master:
        runners.locust_runner = MasterLocustRunner(locust_classes, options)
        if options.no_web: #For CLI option in Distributed Testing
            while len(runners.locust_runner.clients.ready)<options.num_slave:
                logging.info("Waiting for slaves to be ready, %s of %s connected",
                             len(runners.locust_runner.clients.ready), options.num_slave)
                time.sleep(2)

            runners.locust_runner.start_hatching(options.num_clients, options.hatch_rate)
            main_greenlet = runners.locust_runner.greenlet
    elif options.slave:
        try:
            runners.locust_runner = SlaveLocustRunner(locust_classes, options)
            main_greenlet = runners.locust_runner.greenlet
        except socket.error as e:
            logger.error("Failed to connect to the Locust master: %s", e)
            sys.exit(-1)

    if not options.only_summary and (options.print_stats or (options.no_web and not options.slave)):
        # spawn stats printing greenlet
        gevent.spawn(stats_printer)

    # for getting json for plotter in CLI
    if options.no_web and not options.slave:
        gevent.spawn(stats_report)


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
