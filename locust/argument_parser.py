import argparse
import os
import sys
import textwrap

import configargparse

import locust

version = locust.__version__


DEFAULT_CONFIG_FILES = ['~/.locust.conf','locust.conf']


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
        names.append(names[0] + '.py')
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


def get_empty_argument_parser(add_help=True, default_config_files=DEFAULT_CONFIG_FILES):
    parser = configargparse.ArgumentParser(
        default_config_files=default_config_files, 
        auto_env_var_prefix="LOCUST_", 
        add_env_var_help=False,
        add_config_file_help=False,
        add_help=add_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage=argparse.SUPPRESS,
        description=textwrap.dedent("""
            Usage: locust [OPTIONS] [LocustClass ...]
            
        """),
        #epilog="",
    )
    parser.add_argument(
        '-f', '--locustfile',
        default='locustfile',
        help="Python module file to import, e.g. '../other.py'. Default: locustfile"
    )
    return parser


def parse_locustfile_option(args=None):
    """
    Construct a command line parser that is only used to parse the -f argument so that we can 
    import the test scripts in case any of them adds additional command line arguments to the 
    parser
    """    
    parser = get_empty_argument_parser(add_help=False)
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--version', '-V',
        action='store_true',
        default=False,
    )
    
    options, _ = parser.parse_known_args(args=args)
    
    locustfile = find_locustfile(options.locustfile)
    
    if not locustfile:
        if options.help or options.version:
            # if --help or --version is specified we'll call parse_options which will print the help/version message
            parse_options(args=args)
        sys.stderr.write("Could not find any locustfile! Ensure file ends in '.py' and see --help for available options.\n")
        sys.exit(1)
    
    if locustfile == "locust.py":
        sys.stderr.write("The locustfile must not be named `locust.py`. Please rename the file and try again.\n")
        sys.exit(1)
        
    return locustfile


def setup_parser_arguments(parser):
    """
    Setup command-line options
    
    Takes a configargparse.ArgumentParser as argument and calls it's add_argument 
    for each of the supported arguments
    """
    parser._optionals.title = "Common options"
    parser.add_argument(
        '-H', '--host',
        help="Host to load test in the following format: http://10.21.32.33"
    )
    # Number of Locust users
    parser.add_argument(
        '-c', '--clients',
        type=int,
        dest='num_clients',
        default=1,
        help="Number of concurrent Locust users. Only used together with --headless"
    )
    # User hatch rate
    parser.add_argument(
        '-r', '--hatch-rate',
        type=float,
        default=1,
        help="The rate per second in which clients are spawned. Only used together with --headless"
    )
    # Time limit of the test run
    parser.add_argument(
        '-t', '--run-time',
        help="Stop after the specified amount of time, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with --headless"
    )
    # List locust commands found in loaded locust files/source files
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        dest='list_commands',
        help="Show list of possible locust classes and exit"
    )
    
    web_ui_group = parser.add_argument_group("Web UI options")
    web_ui_group.add_argument(
        '--web-host',
        default="",
        help="Host to bind the web interface to. Defaults to '' (all interfaces)"
    )
    web_ui_group.add_argument(
        '--web-port', '-P',
        type=int,
        default=8089,
        help="Port on which to run web host"
    )
    # if we should print stats in the console
    web_ui_group.add_argument(
        '--headless',
        action='store_true',
        help="Disable the web interface, and instead start the load test immediately. Requires -c and -t to be specified."
    )
    web_ui_group.add_argument(
        '--web-auth',
        type=str,
        dest='web_auth',
        default=None,
        help='Turn on Basic Auth for the web interface. Should be supplied in the following format: username:password'
    )
    
    master_group = parser.add_argument_group(
        "Master options", 
        "Options for running a Locust Master node when running Locust distributed. A Master node need Worker nodes that connect to it before it can run load tests.",
    )
    # if locust should be run in distributed mode as master
    master_group.add_argument(
        '--master',
        action='store_true',
        help="Set locust to run in distributed mode with this process as master"
    )
    master_group.add_argument(
        '--master-bind-host',
        default="*",
        help="Interfaces (hostname, ip) that locust master should bind to. Only used when running with --master. Defaults to * (all available interfaces)."
    )
    master_group.add_argument(
        '--master-bind-port',
        type=int,
        default=5557,
        help="Port that locust master should bind to. Only used when running with --master. Defaults to 5557."
    )
    master_group.add_argument(
        '--expect-workers',
        type=int,
        default=1,
        help="How many workers master should expect to connect before starting the test (only when --headless used)."
    )
    master_group.add_argument(
        '--expect-slaves',
        action='store_true',
        help=configargparse.SUPPRESS
    )
    
    worker_group = parser.add_argument_group(
        "Worker options", 
        textwrap.dedent("""
            Options for running a Locust Worker node when running Locust distributed. 
            Only the LOCUSTFILE (-f option) need to be specified when starting a Worker, since other options such as -c, -r, -t are specified on the Master node.
        """),
    )
    # if locust should be run in distributed mode as worker
    worker_group.add_argument(
        '--worker',
        action='store_true',
        help="Set locust to run in distributed mode with this process as worker"
    )
    worker_group.add_argument(
        '--slave',
        action='store_true',
        help=configargparse.SUPPRESS
    )
    # master host options
    worker_group.add_argument(
        '--master-host',
        default="127.0.0.1",
        help="Host or IP address of locust master for distributed load testing. Only used when running with --worker. Defaults to 127.0.0.1."
    )
    worker_group.add_argument(
        '--master-port',
        type=int,
        default=5557,
        help="The port to connect to that is used by the locust master for distributed load testing. Only used when running with --worker. Defaults to 5557."
    )
    
    stats_group = parser.add_argument_group("Request statistics options")
    # A file that contains the current request stats.
    stats_group.add_argument(
        '--csv', '--csv-base-name',
        dest='csvfilebase',
        help="Store current request stats to files in CSV format.",
    )
    # Adds each stats entry at every iteration to the _stats_history.csv file.
    stats_group.add_argument(
        '--csv-full-history',
        action='store_true',
        default=False,
        dest='stats_history_enabled',
        help="Store each stats entry in CSV format to _stats_history.csv file",
    )    
    # if we should print stats in the console
    stats_group.add_argument(
        '--print-stats',
        action='store_true',
        help="Print stats in the console"
    )
    # only print summary stats
    stats_group.add_argument(
       '--only-summary',
       action='store_true',
       help='Only print the summary stats'
    )
    stats_group.add_argument(
        '--reset-stats',
        action='store_true',
        help="Reset statistics once hatching has been completed. Should be set on both master and workers when running in distributed mode",
    )
    
    log_group = parser.add_argument_group("Logging options")
    # skip logging setup
    log_group.add_argument(
        '--skip-log-setup',
        action='store_true',
        dest='skip_log_setup',
        default=False,
        help="Disable Locust's logging setup. Instead, the configuration is provided by the Locust test or Python defaults."
    )
    # log level
    log_group.add_argument(
        '--loglevel', '-L',
        default='INFO',
        help="Choose between DEBUG/INFO/WARNING/ERROR/CRITICAL. Default is INFO.",
    )
    # log file
    log_group.add_argument(
        '--logfile',
        help="Path to log file. If not set, log will go to stdout/stderr",
    )
    
    step_load_group = parser.add_argument_group("Step load options")
    # Enable Step Load mode
    step_load_group.add_argument(
        '--step-load',
        action='store_true',
        help="Enable Step Load mode to monitor how performance metrics varies when user load increases. Requires --step-clients and --step-time to be specified."
    )
    # Number of clients to incease by Step
    step_load_group.add_argument(
        '--step-clients',
        type=int,
        default=1,
        help="Client count to increase by step in Step Load mode. Only used together with --step-load"
    )
    # Time limit of each step
    step_load_group.add_argument(
        '--step-time',
        help="Step duration in Step Load mode, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with --step-load"
    )
    
    
    other_group = parser.add_argument_group("Other options")
    # Display ratio table of all tasks
    other_group.add_argument(
        '--show-task-ratio',
        action='store_true',
        help="Print table of the locust classes' task execution ratio"
    )
    # Display ratio table of all tasks in JSON format
    other_group.add_argument(
        '--show-task-ratio-json',
        action='store_true',
        help="Print json data of the locust classes' task execution ratio"
    )
    # Version number (optparse gives you --version but we have to do it
    # ourselves to get -V too. sigh)
    other_group.add_argument(
        '--version', '-V',
        action='version',
        help="Show program's version number and exit",
        version='%(prog)s {}'.format(version),
    )
    # set the exit code to post on errors
    other_group.add_argument(
        '--exit-code-on-error',
        type=int,
        default=1,
        help="Sets the process exit code to use when a test result contain any failure or error"
    )
    other_group.add_argument(
        '-s', '--stop-timeout',
        action='store',
        type=int,
        dest='stop_timeout',
        default=None,
        help="Number of seconds to wait for a simulated user to complete any executing task before exiting. Default is to terminate immediately. This parameter only needs to be specified for the master process when running Locust distributed."
    )
    
    locust_classes_group = parser.add_argument_group("Locust user classes")
    locust_classes_group.add_argument(
        'locust_classes',
        nargs='*',
        metavar='LocustClass',
        help="Optionally specify which Locust classes that should be used (available Locust classes can be listed with -l or --list)",
    )

def get_parser(default_config_files=DEFAULT_CONFIG_FILES):
    # get a parser that is only able to parse the -f argument
    parser = get_empty_argument_parser(add_help=True, default_config_files=default_config_files)
    # add all the other supported arguments
    setup_parser_arguments(parser)
    # fire event to provide a hook for locustscripts and plugins to add command line arguments
    locust.events.init_command_line_parser.fire(parser=parser)
    return parser


def parse_options(args=None):
    parser = get_parser()
    # parse command line and return options
    options = parser.parse_args(args=args)
    return options
