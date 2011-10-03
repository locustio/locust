import logging
import sys

def setup_logging(loglevel, logfile):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if numeric_level is None:
        raise ValueError("Invalid log level: %s" % loglevel)
    
    log_format = "[%(asctime)s] %(levelname)s/%(name)s: %(message)s"
    logging.basicConfig(level=numeric_level, filename=logfile, format=log_format)
    
    sys.stderr = StdErrWrapper()
    sys.stdout = StdOutWrapper()

stdout_logger = logging.getLogger("stdout")
stderr_logger = logging.getLogger("stderr")

class StdOutWrapper(object):
    """
    Wrapper for stdout
    """
    def write(self, s):
        stdout_logger.info(s.strip())

class StdErrWrapper(object):
    """
    Wrapper for stderr
    """
    def write(self, s):
        stderr_logger.error(s.strip())
