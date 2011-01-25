import gevent
from gevent import monkey
monkey.patch_all(thread=False)

import random
import web
from stats import RequestStats
from clients import HTTPClient, HttpBrowser

def require_once(required_func):
    def decorator_func(func):
        def wrapper(l):
            if not "_required_once" in l.__dict__:
                l.__dict__["_required_once"] = {}
            
            if not str(required_func) in l._required_once:
                required_func(l)
                l._required_once[str(required_func)] = True
                
            return func(l)
        return wrapper
    return decorator_func

class Locust(object):
    def __init__(self):
        self.client = HttpBrowser(self.host)
    
    def __call__(self):
        while (True):
            self.perform_task()
            gevent.sleep(random.randint(self.min_wait, self.max_wait) / 1000.0)
    
    def perform_task(self):
        random.choice(self.tasks)(self)


locusts = []

def hatch(locust, hatch_rate, max):
    print "Hatching and swarming %i clients at the rate %i clients/s..." % (max, hatch_rate)
    while True:
        for i in range(0, hatch_rate):
            if len(locusts) >= max:
                print "All locusts hatched"
                return
            new_locust = gevent.spawn(locust())
            new_locust.link(on_death)
            locusts.append(new_locust)
        print "%i locusts hatched" % (len(locusts))
        gevent.sleep(1)

def on_death(locust):
    locusts.remove(locust)
    if len(locusts) == 0:
        print "All locusts dead"
 
def print_stats():
    while True:
        print "%20s %7s %8s %7s %7s %7s %7s" % ('Name', '# reqs', '# fails', 'Avg', 'Min', 'Max', 'req/s')
        print "-" * 80
        for r in RequestStats.requests.itervalues():
            print r
        print ""
        gevent.sleep(2)

def swarm(locust, hatch_rate=1, max=1):
    hatch_greenlet = gevent.spawn(hatch, locust, hatch_rate, max)
    gevent.spawn(print_stats)
    return hatch_greenlet

def prepare_swarm_from_web(locust, hatch_rate=1, max=1):
    web.start(locust, hatch_rate, max)
    gevent.sleep(200000)


