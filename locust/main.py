# import inspect
import logging
# import os
import signal
import socket
import sys
import time
# from optparse import OptionParser

import gevent

import locust

from runners import MasterLocustRunner, SlaveLocustRunner
from . import events, runners, web
from .core import HttpLocust, Locust
from .inspectlocust import get_task_ratio_dict, print_task_ratio
from .log import console_logger, setup_logging
from .stats import (print_error_report, print_percentile_stats, print_stats,
                    stats_printer, stats_writer, write_stat_csvs)

from . import config

from runners import MasterLocustRunner, SlaveLocustRunner

_internals = [Locust, HttpLocust]
version = locust.__version__

main_greenlet = None

def main():

    options, locusts = config.process_options()
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

    
    master = MasterLocustRunner(locusts, options)
    runners.main = master
    main_greenlet = gevent.spawn(web.start, locusts, options)
    main_greenlet.join()



    # master = MasterLocustRunner(locusts, options)
    # runners.locust_runner = master
    # master.greenlet.join()

    # Master / Slave init
    if options.slave:
        slave = MasterLocustRunner(locusts, options)
        runners.main = slave
        main_greenlet = runners.main.greenlet
        logger.info(
            "Starting slave node. Connecting to %s:%s",
            options.master_host,
            options.master_port
        )
    else:
        master = MasterLocustRunner(locusts, options)
        runners.main = master
        main_greenlet = runners.main.greenlet
        logger.info("Starting master node")

    # Headful / headless init
    if options.no_web or options.slave:
        logger.info("Slave connected in headless mode")
    elif options.no_web and not options.slave:
        logger.info("Starting headless execution")
        runners.main.wait_for_slaves(options.expect_slaves)
        runners.main.start_hatching(options.num_clients, options.hatch_rate)
    else:
        gevent.spawn(web.start, locusts, options)
        logger.info("Starting web monitor at %s:%s", options.web_host or "*", options.port)


    #### Stats, etc

    main_greenlet.join()


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
    elif options.master:
        runners.locust_runner = MasterLocustRunner(locust_classes, options)
        if options.no_web:
            while len(runners.locust_runner.clients.ready)<options.expect_slaves:
                logging.info("Waiting for slaves to be ready, %s of %s connected",
                             len(runners.locust_runner.clients.ready), options.expect_slaves)
                time.sleep(1)

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

    # if options.csvfilebase:
    #     gevent.spawn(stats_writer, options.csvfilebase)

    
    def shutdown(code=0):
        """
        Shut down locust by firing quitting event, printing/writing stats and exiting
        """
        logger.info("Shutting down (exit code %s), bye." % code)

        events.quitting.fire()
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

if __name__ == '__main__':
    main()
