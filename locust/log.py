import logging
import socket
import sys

def setup_logging(loglevel, logfile):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if numeric_level is None:
        raise ValueError("Invalid log level: %s" % loglevel)
    
    log_format = "[%(asctime)s] {0}/%(levelname)s/%(name)s: %(message)s".format(socket.gethostname())
    logging.basicConfig(level=numeric_level, filename=logfile, format=log_format)
    
    sys.stderr = StdErrWrapper()
    sys.stdout = StdOutWrapper()

class StdOutWrapper(object):
    """
    Wrapper for stdout
    """
    def __init__(self):
        self.logger = logging.getLogger("stdout")

    def write(self, s):
        self.logger.info(s.strip())

    def flush(self, *args, **kwargs):
        """No-op for wrapper"""
        pass

class StdErrWrapper(object):
    """
    Wrapper for stderr
    """
    def __init__(self):
        self.logger = logging.getLogger("stderr")

    def write(self, s):
        self.logger.error(s.strip())

    def flush(self, *args, **kwargs):
        """No-op for wrapper"""
        pass

# set up logger for the statistics tables
console_logger = logging.getLogger("console_logger")
# create console handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
# formatter that doesn't include anything but the message
sh.setFormatter(logging.Formatter('%(message)s'))
console_logger.addHandler(sh)
console_logger.propagate = False

# configure python-requests log level
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
