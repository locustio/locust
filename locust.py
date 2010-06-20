import gevent
from gevent import monkey
monkey.patch_all()

import web
from stats import RequestStats


locusts = []

def hatch(locust, hatch_rate, max):
    print "Hatching and swarming..."
    while True:
        for i in range(0, hatch_rate):
            if len(locusts) >= max:
                print "All locusts hatched"
                return
            new_locust = gevent.spawn(locust, 'Default name')
            new_locust.link(on_death)
            locusts.append(new_locust)
        gevent.sleep(1)

def on_death(locust):
    locusts.remove(locust)
    if len(locusts) == 0:
        print "All locusts dead"
 
def print_stats():
    while True:
        print "%20s %7s %7s %7s %7s %7s" % ('Name', '# reqs', 'Avg', 'Min', 'Max', 'req/s')
        print "-" * 80
        for r in RequestStats.requests.itervalues():
            print r
        print ""
        gevent.sleep(1)

def swarm(locust, hatch_rate=1, max=1): 
    gevent.spawn(hatch, locust, hatch_rate, max)
    gevent.spawn(print_stats)

def prepare_swarm_from_web(locust, hatch_rate=1, max=1):
    web.start(locust, hatch_rate, max)
    gevent.sleep(200000)

