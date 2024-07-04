import logging
import logging.config
import re
import socket
from collections import deque

HOSTNAME = re.sub(r"\..*", "", socket.gethostname())

# Global flag that we set to True if any unhandled exception occurs in a greenlet
# Used by main.py to set the process return code to non-zero
unhandled_greenlet_exception = False


class LogReader(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = deque(maxlen=500)

    def emit(self, record):
        self.logs.append(self.format(record))


def setup_logging(loglevel, logfile=None):
    loglevel = loglevel.upper()

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": f"[%(asctime)s] {HOSTNAME}/%(levelname)s/%(name)s: %(message)s",
            },
            "plain": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "console_plain": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
            },
            "log_reader": {"class": "locust.log.LogReader", "formatter": "default"},
        },
        "loggers": {
            "locust": {
                "handlers": ["console", "log_reader"],
                "level": loglevel,
                "propagate": False,
            },
            "locust.stats_logger": {
                "handlers": ["console_plain", "log_reader"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console", "log_reader"],
            "level": loglevel,
        },
    }
    if logfile:
        # if a file has been specified add a file logging handler and set
        # the locust and root loggers to use it
        LOGGING_CONFIG["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "filename": logfile,
            "formatter": "default",
        }
        LOGGING_CONFIG["loggers"]["locust"]["handlers"] = ["file", "log_reader"]
        LOGGING_CONFIG["root"]["handlers"] = ["file", "log_reader"]

    logging.config.dictConfig(LOGGING_CONFIG)


def get_logs():
    log_reader_handler = [handler for handler in logging.getLogger("root").handlers if handler.name == "log_reader"]

    if log_reader_handler:
        return list(log_reader_handler[0].logs)

    return []


def greenlet_exception_logger(logger, level=logging.CRITICAL):
    """
    Return a function that can be used as argument to Greenlet.link_exception() that will log the
    unhandled exception to the given logger.
    """

    def exception_handler(greenlet):
        if greenlet.exc_info[0] == SystemExit:
            logger.log(
                min(logging.INFO, level),  # dont use higher than INFO for this, because it sounds way to urgent
                "sys.exit(%s) called (use log level DEBUG for callstack)" % greenlet.exc_info[1],
            )
            logger.log(logging.DEBUG, "Unhandled exception in greenlet: %s", greenlet, exc_info=greenlet.exc_info)
        else:
            logger.log(level, "Unhandled exception in greenlet: %s", greenlet, exc_info=greenlet.exc_info)
        global unhandled_greenlet_exception
        unhandled_greenlet_exception = True

    return exception_handler
