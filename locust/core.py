import gevent
from gevent import monkey
from gevent.pool import Group
from locust.stats import print_percentile_stats

monkey.patch_all(thread=False)

from time import time
import random
import socket
from hashlib import md5
from hotqueue import HotQueue

from clients import HTTPClient, HttpBrowser
from stats import RequestStats, print_stats

from exception import LocustError, InterruptLocust

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
                required_func(l)
                return
                
            return func(l)
        return wrapper
    return decorator_func

class LocustMeta(type):
    """
    Meta class for the main Locust class. It's used to allow Locust classes to specify task execution 
    ratio using an {task:int} dict, or a [(task0,int), ..., (taskN,int)] list.
    """
    
    def __new__(meta, classname, bases, classDict):
        if "tasks" in classDict and classDict["tasks"] is not None:
            tasks = classDict["tasks"]
            if isinstance(tasks, dict):
                tasks = list(tasks.iteritems())
            
            if len(tasks) > 0 and isinstance(tasks[0], tuple):
                new_tasks = []
                for task, count in tasks:
                    for i in xrange(0, count):
                        new_tasks.append(task)
                classDict["tasks"] = new_tasks
        
        return type.__new__(meta, classname, bases, classDict)

class Locust(object):
    """
    Locust base class defining a locust user/client.
    """
    
    tasks = None
    """
    List with python callables that represents a locust user task.

    If tasks is a list, the task to be performed will be picked randomly.

    If tasks is a *(callable,int)* list of two-tuples, the task to be performed will be picked randomly, but each task will be
    weighted according to it's corresponding int value. So in the following case *task1* will be three times more
    likely to be picked than *task2*::

        class User(Locust):
            tasks = [(task1, 3), (task2, 1)]
    """
    
    host = None
    """Base hostname to swarm. i.e: http://127.0.0.1:1234"""

    min_wait = 1000
    """Minimum waiting time between two execution of locust tasks"""
    
    max_wait = 1000
    """Maximum waiting time between the execution of locust tasks"""
    
    stop_timeout = None
    """Number of seconds after which the Locust will die. If None it won't timeout."""

    weight = 10
    """Probability of locust beeing choosen. The higher the weight, the greater is the chance of it beeing chosen."""
    
    __metaclass__ = LocustMeta
    
    def __init__(self):
        self._task_queue = []
        self._time_start = time()

    def __call__(self):
        try:
            while (True):
                if self.stop_timeout is not None and time() - self._time_start > self.stop_timeout:
                    return
        
                if not self._task_queue:
                    self.schedule_task(self.get_next_task())
                self.execute_next_task()
                self.wait()
        except InterruptLocust:
            pass
    
    def execute_next_task(self):
        task = self._task_queue.pop(0)
        self.execute_task(task["callable"], *task["args"])
    
    def execute_task(self, task, *args):
        task(self, *args)
    
    def schedule_task(self, task_callable, *args, **kwargs):
        """
        Add a task to the Locust's task execution queue.
        
        Arguments:
        * task_callable: Locust task to schedule
        * first: Optional keyword argument. If True, the task will be put first in the queue.
        * All other non keyword arguments will be passed to the task callable.
        """
        task = {"callable":task_callable, "args":args}
        if "first" in kwargs:
            self._task_queue.insert(0, task)
        else:
            self._task_queue.append(task)
    
    def get_next_task(self):
        return random.choice(self.tasks)
    
    def wait(self):
        gevent.sleep(random.randint(self.min_wait, self.max_wait) / 1000.0)

class WebLocust(Locust):
    """
    Locust class that inherits from Locust and creates a *client* attribute on instantiation. 
    
    The *client* attribute is a simple HTTP client with support for keeping a user session between requests.
    """
    
    client = None
    """
    Instance of HttpBrowser that is created upon instantiation of WebLocust. 
    The client support cookies, and therefore keeps the session between HTTP requests.
    """
    
    def __init__(self):
        super(WebLocust, self).__init__()
        if self.host is None:
            raise LocustError("You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")

        self.client = HttpBrowser(self.host)


locusts = Group()
locust_runner = None

class LocustRunner(object):
    def __init__(self, locust_classes, hatch_rate, num_clients, num_requests=None, host=None):
        self.locust_classes = locust_classes
        self.hatch_rate = hatch_rate
        self.num_clients = num_clients
        self.num_requests = num_requests
        self.host = host
        self.locusts = Group()

    @property
    def request_stats(self):
        return RequestStats.requests
    
    def hatch(self, stop_timeout=None):
        if self.num_requests is not None:
            RequestStats.global_max_requests = self.num_requests
        
        bucket = []
        weight_sum = sum((locust.weight for locust in self.locust_classes))
        for locust in self.locust_classes:
            if not locust.tasks:
                print "Notice: Found locust (%s) got no tasks. Skipping..." % locust.__name__
                continue
    
            if self.host is not None:
                locust.host = self.host
            if stop_timeout is not None:
                locust.stop_timeout = stop_timeout

            # create locusts depending on weight
            percent = locust.weight / float(weight_sum)
            num_locusts = int(round(self.num_clients * percent))
            bucket.extend([locust for x in xrange(0, num_locusts)])

        print "\nHatching and swarming %i clients at the rate %i clients/s...\n" % (self.num_clients, self.hatch_rate)
        occurence_count = dict([(l.__name__, 0) for l in self.locust_classes])
        
        def spawn_locusts():
            while True:
                for i in range(0, self.hatch_rate):
                    if not bucket:
                        print "All locusts hatched: %s" % ", ".join(["%s: %d" % (name, count) for name, count in occurence_count.iteritems()])
                        print "Resetting stats\n"
                        RequestStats.reset_all()
                        return

                    locust = bucket.pop()
                    occurence_count[locust.__name__] += 1
                    new_locust = self.locusts.spawn(locust())
                print "%i locusts hatched" % len(self.locusts)
                gevent.sleep(1)
        
        spawn_locusts()
        self.locusts.join()
        print "All locusts dead\n"
        print_percentile_stats(self.request_stats) #TODO use an event listener, or such, for this?

    def log_request(self, *args, **kwargs):
        self.current_num_requests += 1
        if self.num_requests and self.current_num_requests >= self.num_requests:
            print "%d requests performed, killing all locusts..." % self.current_num_requests
            locusts.kill()
            print_stats(RequestStats.requests)
            self.kill()
        elif self.current_num_requests % 10 == 0:
            print "%d requests performed" % self.current_num_requests

    def reset(self, stats=True):
        self.current_num_requests = 0
        self.is_alive = True
        if stats:
            RequestStats.requests = {}

    def kill(self):
        self.is_alive = False

class LocalLocustRunner(LocustRunner):
    def start_hatching(self):
        self.greenlet = gevent.spawn(self.hatch, self)

class DistributedLocustRunner(LocustRunner):
    def __init__(self, locust_classes, hatch_rate, num_clients, num_requests, host=None, redis_host="localhost", redis_port=6379):
        super(DistributedLocustRunner, self).__init__(locust_classes, hatch_rate, num_clients, num_requests, host)
        
        # set up the redis queus that will be used to communicate between master and slaves
        self.work_queue = HotQueue("locust_work_queue", host=redis_host, port=redis_port, db=0)
        self.client_report_queue = HotQueue("locust_client_report_queue", host=redis_host, port=redis_port, db=0)
        self.stats_report_queue = HotQueue("locust_stats_report_queue", host=redis_host, port=redis_port, db=0)

class MasterLocustRunner(DistributedLocustRunner):
    def __init__(self, *args, **kwargs):
        super(MasterLocustRunner, self).__init__(*args, **kwargs)
        self.ready_clients = []
        self.client_stats = {}
        self.greenlet = Group()
        self.greenlet.spawn(self.client_tracker).link_exception()
        self.greenlet.spawn(self.stats_aggregator).link_exception()
    
    def start_hatching(self):
        print "Sending hatch jobs to %i ready clients" % len(self.ready_clients)
        for client in self.ready_clients:
            self.work_queue.put({"hatch_rate":self.hatch_rate, "num_clients":self.num_clients, "num_requests": self.num_requests, "host":self.host, "stop_timeout":60})
    
    def client_tracker(self):
        for client in self.client_report_queue.consume():
            self.ready_clients.append(client)
            print "Client %r reported as ready. Currently %i clients ready to swarm." % (client, len(self.ready_clients))
    
    def stats_aggregator(self):
        for report in self.stats_report_queue.consume():
            if not report["stats"]:
                continue
            #print "stats report recieved from %s:" % report["client_id"], report["stats"]
            self.client_stats[report["client_id"]] = report["stats"]
    
    @property
    def request_stats(self):
        stats = {}
        for client_id, client_stats in self.client_stats.iteritems():
            for entry_name, entry in client_stats.iteritems():
                stats[entry_name] = stats.setdefault(entry_name, RequestStats(entry_name)) + entry
        return stats

class SlaveLocustRunner(DistributedLocustRunner):
    def __init__(self, *args, **kwargs):
        super(SlaveLocustRunner, self).__init__(*args, **kwargs)
        self.client_id = socket.gethostname() + "_" + md5(str(time() + random.randint(0,10000))).hexdigest()
        self.client_report_queue.put(self.client_id)
        self.greenlet = Group()
        self.greenlet.spawn(self.worker).link_exception()
        self.greenlet.spawn(self.stats_reporter).link_exception()
    
    def start_hatching(self):
        raise LocustError("start_hatching should never be called for a slave process")
    
    def worker(self):
        for job in self.work_queue.consume():
            print "job recieved: %r" % job
            self.hatch_rate = job["hatch_rate"]
            self.num_clients = job["num_clients"]
            self.num_requests = job["num_requests"]
            self.host = job["host"]
            self.hatch(stop_timeout=job["stop_timeout"])
    
    def stats_reporter(self):
        while True:
            self.stats_report_queue.put({
                "client_id": self.client_id,
                "stats": self.request_stats,
            })
            gevent.sleep(3)

