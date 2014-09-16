import gevent
import sys
import logging
import time
import os

from subprocess import Popen

class Monitor(object):

    def __init__(self, log_file, sleep):
        self.log_file = log_file
        self.sleep = sleep
        
        self.prepare_log_file()
        self.prepare_logger()

    def prepare_log_file(self):
        d = os.path.dirname(self.log_file)
        if not os.path.exists(d):
            os.makedirs(d)
        open(self.log_file, 'w').close()

    def prepare_logger(self):
        self.logger = logging.getLogger("locust.monitor")
        self.handler = logging.FileHandler(self.log_file)
        self.formatter = logging.Formatter("%(message)s")
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)


    def start(self, master_locust=None):

        h = "Time,Users,Ok,Fail,RT,RPS"
        self.logger.info(h)
        
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

                self.logger.info("%s,%s,%s,%s,%s,%s", time.strftime("%H:%M:%S"), nl, nr, nf, crt, crps)
        
            gevent.sleep(self.sleep)


