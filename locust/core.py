import gevent
from gevent import monkey
monkey.patch_all(thread=False)

import random
import web
from stats import RequestStats
from clients import HTTPClient, HttpBrowser

def require_once(required_func):
    """
    @require_once decorator is used on a locust task in order to make sure another locust 
    task (the argument to require_once) is run once (per client) before the decorated 
    task.
    
    The require_once decorator respects the wait time of the Locust class, by inserting the
    locust tasks at the beginning of the task execution queue.
    
    Example::
    
        def login(l):
            l.client.post("/login", {"username":"joe_hill", "password":"organize"})
        
        @require_once(login)
        def inbox(l):
            l.client.get("/inbox")
    """
    def decorator_func(func):
        def wrapper(l):
            if not "_required_once" in l.__dict__:
                l.__dict__["_required_once"] = {}
            
            if not str(required_func) in l._required_once:
                # when the required task has not been run in the current client, we schedule it to
                # be the next task in queue, and we also reschedule the original task to be run 
                # immediately after the required task
                l._required_once[str(required_func)] = True
                l.schedule_task(func, first=True)
                l.schedule_task(required_func, first=True)                
                return
                
            return func(l)
        return wrapper
    return decorator_func

class LocustMeta(type):
    """
    Meta class for the main Locust class. It's used to allow Locust classes to specify task execution 
    ratio using an {int:task} dict.
    """
    
    def __new__(meta, classname, bases, classDict):
        if "tasks" in classDict and isinstance(classDict["tasks"], dict):
            tasks = []
            for count, task in classDict["tasks"].iteritems():
                for i in xrange(0, count):
                    tasks.append(task)
            classDict["tasks"] = tasks
        
        return type.__new__(meta, classname, bases, classDict)

class Locust(object):
    """
    Locust base class defining a locust user/client.
    """
    
    """Minimum waiting time between two execution of locust tasks"""
    min_wait = 1000
    
    """Maximum waiting time between the execution of locust tasks"""
    max_wait = 1000
    
    __metaclass__ = LocustMeta
    
    def __init__(self):
        self.client = HttpBrowser(self.host)
        self._task_queue = []
    
    def __call__(self):
        while (True):
            if not self._task_queue:
                self.schedule_task(self.get_next_task())
            self._task_queue.pop(0)(self)
            self.wait()
    
    def schedule_task(self, task, first=False):
        if first:
            self._task_queue.insert(0, task)
        else:
            self._task_queue.append(task)
    
    def get_next_task(self):
        return random.choice(self.tasks)
    
    def wait(self):
        gevent.sleep(random.randint(self.min_wait, self.max_wait) / 1000.0)


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
    gevent.spawn(web.start, locust, hatch_rate, max)
    return hatch_greenlet

def prepare_swarm_from_web(locust, hatch_rate=1, max=1):
    web.start(locust, hatch_rate, max)
    gevent.sleep(200000)


