import logging
import logging.config
import socket

HOSTNAME = socket.gethostname()

# Global flag that we set to True if any unhandled exception occurs in a greenlet
# Used by main.py to set the process return code to non-zero
unhandled_greenlet_exception = False


def setup_logging(loglevel, logfile=None):
    loglevel = loglevel.upper()
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] {0}/%(levelname)s/%(name)s: %(message)s".format(HOSTNAME),
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
        },
        "loggers": {
            "locust": {
                "handlers": ["console"],
                "level": loglevel,
                "propagate": False,
            },
            "locust.stats_logger": {
                "handlers": ["console_plain"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
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
        LOGGING_CONFIG["loggers"]["locust"]["handlers"] = ["file"]
        LOGGING_CONFIG["root"]["handlers"] = ["file"]
    
    logging.config.dictConfig(LOGGING_CONFIG)


def greenlet_exception_logger(logger, level=logging.CRITICAL):
    """
    Return a function that can be used as argument to Greenlet.link_exception() that will log the 
    unhandled exception to the given logger.
    """
    def exception_handler(greenlet):
        logger.log(level, "Unhandled exception in greenlet: %s", greenlet, exc_info=greenlet.exc_info)
        global unhandled_greenlet_exception
        unhandled_greenlet_exception = True
    return exception_handler
