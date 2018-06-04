from optparse import OptionParser
import sys

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
        help="Python module file to import, e.g. '../other.py'. Default: locustfilePython module file to import, e.g. '../other.py'. Default: locustfile"
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
        run_time (str): Stop after the specified amount of time, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with --no-web (default: None)
        num_clients (int): Number of concurrent Locust users. Only used together with no_web (default: 1)
        hatch_rate (int): The rate per second in which clients are spawned. Only used together with --no-web (default: 1)
        master (bool): Set locust to run in distributed mode with this process as master (default: False)
        expect_slaves (int): How many slaves master should expect to connect before starting the test (only when no_web used). (default: 1)
        master_bind_host (str): Interfaces (hostname, ip) that locust master should bind to. Only used when running with master. Defaults all available interfaces. (default: '*')
        master_bind_port (int): Port that locust master should bind to. Only used when running with --master. Note that Locust will also use this port + 1, so by default the master node will bind to 5557 and 5558. (default: 5557)
        slave (bool): Set locust to run in distributed mode with this process as slave (default: False)
        master_host (str): Host or IP address of locust master for distributed load testing. Only used when running with slave. (default: '127.0.0.1')
        master_port (int): The port to connect to that is used by the locust master for distributed load testing. Only used when running with --slave. Note that slaves will also connect to the master node on this port + 1. (default: 5557)
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