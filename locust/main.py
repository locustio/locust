import logging
import signal
import socket
import sys
import time

import gevent

import locust

from runners import MasterLocustRunner, SlaveLocustRunner
from . import events, runners, web
from .core import WebLocust, Locust
from .inspectlocust import get_task_ratio_dict, print_task_ratio
from .log import console_logger, setup_logging
from .stats import (print_error_report, print_percentile_stats, print_stats,
                    stats_printer, stats_writer, write_stat_csvs)

from . import config

from runners import MasterLocustRunner, SlaveLocustRunner

_internals = [Locust, WebLocust]
version = locust.__version__

main_greenlet = None

def launch(options, locusts):
    """
    Locust entrypoint, could be called for programmatical launch:
        * options - Any object which implements field access by attribute
                    Recommended to use extended locust.config.LocustConfig object
        * locusts - list of locust classes inherited from locust.core.Locust
    """
    logger = logging.getLogger(__name__)

    if options.show_version:
        console_logger.info("Locust %s", version)
        sys.exit(0)

    if options.list_commands:
        console_logger.info("Available Locusts:")
        for locust_class in locusts:
            console_logger.info("    " + locust_class.__name__)
        sys.exit(0)

    if options.show_task_ratio:
        console_logger.info("\n Task ratio per locust class")
        console_logger.info("-" * 80)
        print_task_ratio(locusts)
        console_logger.info("\n Total task ratio")
        console_logger.info("-" * 80)
        print_task_ratio(locusts, total=True)
        sys.exit(0)

    if options.show_task_ratio_json:
        from json import dumps
        task_data = {
            "per_class": get_task_ratio_dict(locusts),
            "total": get_task_ratio_dict(locusts, total=True)
        }
        console_logger.info(dumps(task_data))
        sys.exit(0)

    # Master / Slave init
    if options.slave:
        logger.info(
            "Starting slave node. Connecting to %s:%s",
            options.master_host,
            options.master_port
        )
        slave = SlaveLocustRunner(locusts, options)
        runners.main = slave
        main_greenlet = runners.main.greenlet
    else:
        logger.info("Starting master node")
        master = MasterLocustRunner(locusts, options)
        runners.main = master
        main_greenlet = runners.main.greenlet

    # Headful / headless init
    if options.slave:
        logger.info("Slave connected in headless mode")
    elif options.no_web and not options.slave:
        logger.info("Starting headless execution")
        runners.main.wait_for_slaves(options.expect_slaves)
        runners.main.start_hatching(options.num_clients, options.hatch_rate)
    else:
        logger.info(
            "Starting web monitor at %s:%s",
            options.web_host or "localhost",
            options.web_port
        )
        gevent.spawn(web.start, locusts, options)

    #### Stats, etc
    if options.print_stats and not options.slave:
        gevent.spawn(stats_printer)
    if options.csvfilebase and not options.slave:
        gevent.spawn(stats_writer, options.csvfilebase)

    def shutdown(code=0):
        """
        Shut down locust by firing quitting event, printing/writing stats and exiting
        """
        logger.info("Shutting down (exit code %s), bye." % code)

        events.quitting.fire()
        print_stats(runners.main.request_stats)
        print_percentile_stats(runners.main.request_stats)
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
        if len(runners.main.errors):
            code = 1
        shutdown(code=code)
    except KeyboardInterrupt:
        shutdown(0)

def main():
    options, locusts = config.process_options()
    launch(options, locusts)

if __name__ == '__main__':
    main()
