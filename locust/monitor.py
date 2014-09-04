import gevent
import sys
import logging
import time

from subprocess import Popen

logger = logging.getLogger("locust.monitor")
handler = logging.FileHandler("/home/ubuntu/log/locust/monitor.csv")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

SLEEP=0.5

def start(master_locust=None):

    logger.info("Time,Users,200,503,Current Response Time,Total Requests per Seconds")
        
    while master_locust:

        if len(master_locust.stats.entries) > 0:
            s = master_locust.stats.aggregated_stats().serialize()
            nl = master_locust.user_count # number of users
            nr = s['num_requests']        # number of successful requests
            nf = s['num_failures']        # number of failed requests
            crt = 0                       # current response time
            if nr > 0:
                crt = float(s['total_response_time'] / nr)
            crps = master_locust.stats.aggregated_stats().current_rps  # current requests per/sec

            logger.info("%s,%s,%s,%s,%s,%s", time.strftime("%H:%M:%S"), nl, nr, nf, crt, crps)
        
        gevent.sleep(SLEEP)
