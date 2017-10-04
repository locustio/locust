"""Default locust configuration"""
import logging
import os
import inspect
import sys
from contextlib import contextmanager
from optparse import OptionParser
from urlparse import urlparse

from .core import Locust
from .log import setup_logging

__all__ = ['configure', 'locust_config', 'process_options', 'register_config']

logger = logging.getLogger(__name__)

class LocustConfig(object):
    """Config object"""

    LOGGER_MAP = {
        'locust_logging': 'locust',
        'zmq_logging': 'locust.clients.zmq_client',
        'socketio_logging': 'locust.clients.socketio',
        'http_logging': 'locust.clients.http',
    }

    STATIC_PARAMS = [
        'web_host',
        'web_port',
        'no_web',
        'master_host',
        'master_port',
        'master_bind_host',
        'master_bind_port',
    ]

    DEFAULT = {
        # Endpoints
        'host': None,
        'scheme': 'http',
        'port': None,
        'socket_io_resource': 'socket.io',
        'socket_io_service': '',

        # Execution related config
        'min_wait': 1,
        'max_wait': 1,
        'stop_timeout': None,
        'num_clients': 1,
        'hatch_rate': 1,
        'num_requests': None,

        # FE config
        'web_host': '',
        'web_port': 8089,
        'no_web': False,

        # Master-node config
        'master_host': '127.0.0.1',
        'master_port': 5557,
        'master_bind_host': '*',
        'master_bind_port': 5557,

        # Logging
        'http_logging': 'ERROR',
        'socketio_logging': 'ERROR',
        'zmq_logging': 'ERROR',
        'locust_logging': 'ERROR',
        'logfile': None
    }

    def __init__(self):
        self._config = self.DEFAULT.copy()

    def _apply(self):
        """Apply config values"""
        for k, v in self.LOGGER_MAP.items():
            log = logging.getLogger(v)
            log.setLevel(self._config[k])

    def _validate(self):
        """Validate settings"""
        if not self._config['host']:
            logger.error(
                "No target host were provided." +\
                "Please provide target host via cli or setup contextmanager"
            )
            sys.exit(1)

    def to_dict(self):
        """Return config object as raw dict"""
        return self._config.copy()

    def update_config(self, config_dict):
        """Update config object with raw dict"""
        for k, v in config_dict.items():
            if k not in self.STATIC_PARAMS:
                self._config[k] = v

    @property
    def host(self):
        config = self._config
        port = ":{}".format(config['port']) if config['port'] else ''
        return '{}://{}{}'.format(config['scheme'], config['host'], port)

    @property
    def socket_io(self):
        return self.host

    def __getattr__(self, attr):
        return self._config.get(attr, None)

    def __setattr__(self, attr, value):
        if attr == '_config':
            super(LocustConfig, self).__setattr__(attr, value)
        else:
            self._config[attr] = value

# global locust config singleton
_locust_config = LocustConfig()

def locust_config():
    return _locust_config

def register_config(config):
    global _locust_config
    """
    Update default locust configuration object with custom instance
    config argument should be instance of LocustConfig or inherited class
    """
    if not isinstance(config, LocustConfig):
        raise AttributeError('Config object sgould be instance of LocustConfig')
    _locust_config = config

@contextmanager
def configure():
    """locust configuration context manager"""
    yield _locust_config

def process_options():
    _parser, opts, args = parse_options()
    setup_logging(opts.loglevel, opts.logfile)
    with configure() as config:
        loglevel = opts.__dict__.pop('loglevel')
        config.http_logging = loglevel
        config.socketio_logging = loglevel
        config.zmq_logging = loglevel
        config.locust_logging = loglevel
        host = opts.__dict__.pop('host')
        if host:
            parsed_host = urlparse(host)
            config.host = parsed_host.netloc
            config.scheme = parsed_host.scheme
            config.port = parsed_host.port
        for attr, value in opts.__dict__.items():
            setattr(config, attr, value)

    locusts = load_locusts(opts, args)
    _locust_config._apply()
    _locust_config._validate()

    return _locust_config, locusts

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
        default=LocustConfig.DEFAULT['host'],
        help="Host to load test in the following format: http://10.21.32.33"
    )

    parser.add_option(
        '--web-host',
        dest="web_host",
        default=LocustConfig.DEFAULT['web_host'],
        help="Host to bind the web interface to. Defaults to '' (all interfaces)"
    )

    parser.add_option(
        '--web-port',
        type="int",
        dest="web_port",
        default=LocustConfig.DEFAULT['web_port'],
        help="Port on which to run web host"
    )

    parser.add_option(
        '-f', '--locustfile',
        dest='locustfile',
        default='locustfile',
        help="Python module file to import, e.g. '../other.py'. Default: locustfile"
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
        default=LocustConfig.DEFAULT['master_host'],
        help="Host or IP address of locust master for distributed load testing. Only used when running with --slave. Defaults to 127.0.0.1."
    )

    parser.add_option(
        '--master-port',
        action='store',
        type='int',
        dest='master_port',
        default=LocustConfig.DEFAULT['master_port'],
        help="The port to connect to that is used by the locust master for distributed load testing. Only used when running with --slave. Defaults to 5557. Note that slaves will also connect to the master node on this port + 1."
    )

    parser.add_option(
        '--master-bind-host',
        action='store',
        type='str',
        dest='master_bind_host',
        default=LocustConfig.DEFAULT['master_bind_host'],
        help="Interfaces (hostname, ip) that locust master should bind to. Only used when running with --master. Defaults to * (all available interfaces)."
    )

    parser.add_option(
        '--master-bind-port',
        action='store',
        type='int',
        dest='master_bind_port',
        default=LocustConfig.DEFAULT['master_bind_port'],
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
        default=LocustConfig.DEFAULT['no_web'],
        help="Disable the web interface, and instead start running the test immediately. Requires -c and -r to be specified."
    )

    # Number of clients
    parser.add_option(
        '-c', '--clients',
        action='store',
        type='int',
        dest='num_clients',
        default=LocustConfig.DEFAULT['num_clients'],
        help="Number of concurrent clients. Only used together with --no-web"
    )

    # Client hatch rate
    parser.add_option(
        '-r', '--hatch-rate',
        action='store',
        type='float',
        dest='hatch_rate',
        default=LocustConfig.DEFAULT['hatch_rate'],
        help="The rate per second in which clients are spawned. Only used together with --no-web"
    )

    # Number of requests
    parser.add_option(
        '-n', '--num-request',
        action='store',
        type='int',
        dest='num_requests',
        default=LocustConfig.DEFAULT['num_requests'],
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
        default=LocustConfig.DEFAULT['logfile'],
        help="Path to log file. If not set, log will go to stdout/stderr",
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

    # Display ratio table of all tasks in JSON format
    parser.add_option(
        '--print-stats',
        action='store_true',
        dest='print_stats',
        default=False,
        help="print testrun statistics to console"
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

def load_locusts(options, args):
    locustfile = find_locustfile(options.locustfile)

    if not locustfile:
        logger.error("Could not find any locustfile! Ensure file ends in '.py' and see --help for available options.")
        sys.exit(1)

    if locustfile == "locust.py":
        logger.error("The locustfile must not be named `locust.py`. Please rename the file and try again.")
        sys.exit(1)

    _docstring, locusts = load_locustfile(locustfile)

    if not locusts:
        logger.error("No Locust class found!")
        sys.exit(1)
    
    # make sure specified Locust exists
    if args:
        missing = set(args) - set(locusts.keys())
        if missing:
            logger.error("Unknown Locust(s): %s\n" % (", ".join(missing)))
            sys.exit(1)
        else:
            names = set(args) & set(locusts.keys())
            locust_classes = [locusts[n] for n in names]
    else:
        # list() call is needed to consume the dict_view object in Python 3
        locust_classes = list(locusts.values())

    return locust_classes

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
