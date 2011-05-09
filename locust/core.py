import gevent
from gevent import monkey
from gevent.pool import Group

monkey.patch_all(thread=False)

from time import time
import sys
import random
import socket
import warnings
import traceback
from hashlib import md5
from hotqueue import HotQueue

from locust.stats import print_percentile_stats
from clients import HTTPClient, HttpBrowser
from stats import RequestStats, print_stats
import events

from exception import LocustError, InterruptLocust, RescheduleTaskImmediately

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

def task(weight=1):
    def decorator_func(func):
        func.locust_task_weight = weight
        return func
    return decorator_func

class LocustMeta(type):
    """
    Meta class for the main Locust class. It's used to allow Locust classes to specify task execution 
    ratio using an {task:int} dict, or a [(task0,int), ..., (taskN,int)] list.
    """
    
    def __new__(meta, classname, bases, classDict):
        new_tasks = []
        for base in bases:
            if hasattr(base, "tasks") and base.tasks:
                new_tasks += base.tasks
        
        if "tasks" in classDict and classDict["tasks"] is not None:
            tasks = classDict["tasks"]
            if isinstance(tasks, dict):
                tasks = list(tasks.iteritems())
            
            for task in tasks:
                if isinstance(task, tuple):
                    task, count = task
                    for i in xrange(0, count):
                        new_tasks.append(task)
                else:
                    new_tasks.append(task)
        
        for item in classDict.itervalues():
            if hasattr(item, "locust_task_weight"):
                for i in xrange(0, item.locust_task_weight):
                    new_tasks.append(item)
        
        classDict["tasks"] = new_tasks
        
        return type.__new__(meta, classname, bases, classDict)

class Locust(object):
    """
    Locust base class defining a locust user/client.
    """
    
    tasks = []
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
        if hasattr(self, "on_start"):
            self.on_start()
        while (True):
            try:
                if self.stop_timeout is not None and time() - self._time_start > self.stop_timeout:
                    return
        
                if not self._task_queue:
                    self.schedule_task(self.get_next_task())
                
                try:
                    self.execute_next_task()
                except RescheduleTaskImmediately:
                    pass
                else:
                    self.wait()
            except InterruptLocust, e:
                if e.reschedule:
                    raise RescheduleTaskImmediately()
                return
            except Exception, e:
                events.locust_error.fire(self, e)
                sys.stderr.write("\n" + traceback.format_exc())
    
    def execute_next_task(self):
        task = self._task_queue.pop(0)
        self.execute_task(task["callable"], *task["args"])
    
    def execute_task(self, task, *args):
        # check if the function is a method bound to the current locust, and if so, don't pass self as first argument
        if hasattr(task, "im_self") and task.im_self == self:
            task(*args)
        else:
            task(self, *args)
    
    def schedule_task(self, task_callable, *args, **kwargs):
        """
        Add a task to the Locust's task execution queue.
        
        *Arguments*:
        
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
    
    gzip = False
    """
    If set to True the HTTP client will set headers for accepting gzip, and decode gzip data
    that is sent back from the server. This attribute is set from the command line.
    """
    
    def __init__(self):
        super(WebLocust, self).__init__()
        if self.host is None:
            raise LocustError("You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")

        self.client = HttpBrowser(self.host, self.gzip)

class SubLocust(Locust):
    """
    Class for making a sub Locust that can be included as a task inside of a normal Locust/WebLocus,
    as well as inside another sub locust. 
    
    When the parent locust enters the sub locust, it will not
    continue executing it's tasks until a task in the sub locust has called the interrupt() function.
    """
    
    def __init__(self, parent):
        super(SubLocust, self).__init__()
        
        self.parent = parent
        if isinstance(parent, WebLocust):
            self.client = parent.client
        
        self()
    
    def interrupt(self, reschedule=True):
        """
        Interrupt the SubLocust and hand over execution control back to the parent Locust.
        
        If *reschedule* is True (default), the parent Locust will immediately re-schedule,
        and execute, a new task
        """
        raise InterruptLocust(reschedule)


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
    
    @property
    def errors(self):
        return RequestStats.errors
    
    def hatch(self, stop_timeout=None):
        if self.num_requests is not None:
            RequestStats.global_max_requests = self.num_requests
        
        bucket = []
        weight_sum = sum((locust.weight for locust in self.locust_classes))
        for locust in self.locust_classes:
            if not locust.tasks:
                warnings.warn("Notice: Found locust (%s) got no tasks. Skipping..." % locust.__name__)
                continue
    
            if self.host is not None:
                locust.host = self.host
            if stop_timeout is not None:
                locust.stop_timeout = stop_timeout

            # create locusts depending on weight
            percent = locust.weight / float(weight_sum)
            num_locusts = int(round(self.num_clients * percent))
            bucket.extend([locust for x in xrange(0, num_locusts)])

        print "\nHatching and swarming %i clients at the rate %g clients/s...\n" % (self.num_clients, self.hatch_rate)
        occurence_count = dict([(l.__name__, 0) for l in self.locust_classes])
        
        def spawn_locusts():
            sleep_time = 1.0 / self.hatch_rate
            while True:
                if not bucket:
                    print "All locusts hatched: %s" % ", ".join(["%s: %d" % (name, count) for name, count in occurence_count.iteritems()])
                    print "Resetting stats\n"
                    RequestStats.reset_all()
                    return

                locust = bucket.pop(random.randint(0, len(bucket)-1))
                occurence_count[locust.__name__] += 1
                def start_locust():
                    try:
                        locust()()
                    except RescheduleTaskImmediately:
                        pass
                new_locust = self.locusts.spawn(start_locust)
                if len(self.locusts) % 10 == 0:
                    print "%i locusts hatched" % len(self.locusts)
                gevent.sleep(sleep_time)
        
        spawn_locusts()
        self.locusts.join()
        print "All locusts dead\n"
        print_stats(self.request_stats)
        print_percentile_stats(self.request_stats) #TODO use an event listener, or such, for this?

class LocalLocustRunner(LocustRunner):
    def start_hatching(self, locust_count=None, hatch_rate=None):
        if locust_count:
            self.num_clients = locust_count
        if hatch_rate:
            self.hatch_rate = hatch_rate
        
        RequestStats.global_start_time = time()
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
        self.client_errors = {}
        self.greenlet = Group()
        self.greenlet.spawn(self.client_tracker).link_exception()
        self.greenlet.spawn(self.stats_aggregator).link_exception()
        self._request_stats = {}
    
    def start_hatching(self, locust_count=None, hatch_rate=None):
        if locust_count:
            self.num_clients = locust_count / len(self.ready_clients)
        if hatch_rate:
            self.hatch_rate = float(hatch_rate) / len(self.ready_clients)
        
        print "Sending hatch jobs to %i ready clients" % len(self.ready_clients)
        while self.ready_clients:
            client = self.ready_clients.pop()
            self.work_queue.put({"hatch_rate":self.hatch_rate, "num_clients":self.num_clients, "num_requests": self.num_requests, "host":self.host, "stop_timeout":None})
        
        RequestStats.global_start_time = time()
    
    def client_tracker(self):
        for client in self.client_report_queue.consume():
            self.ready_clients.append(client)
            print "Client %r reported as ready. Currently %i clients ready to swarm." % (client, len(self.ready_clients))
    
    def stats_aggregator(self):
        for report in self.stats_report_queue.consume():
            events.slave_report.fire(report["client_id"], report["data"])

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
            self.client_report_queue.put(self.client_id)
    
    def stats_reporter(self):
        while True:
            data = {}
            events.report_to_master.fire(self.client_id, data)
            
            self.stats_report_queue.put({
                "client_id": self.client_id,
                "data": data,
            })
            gevent.sleep(3)
