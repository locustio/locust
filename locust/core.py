import gevent
from gevent import monkey, GreenletExit

monkey.patch_all(thread=False)

from time import time
import sys
import random
import warnings
import traceback
import logging

from clients import HttpSession
import events

from exception import LocustError, InterruptLocust, RescheduleTaskImmediately

logger = logging.getLogger(__name__)

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

def task(weight_or_func=1):
    def decorator_func(func):
        func.locust_task_weight = weight_or_func
        return func
    
    """
    Check if task was used without parentheses (not called), like this::
    
        @task
        def my_task()
            pass
    """
    if callable(weight_or_func):
        func = weight_or_func
        weight_or_func = 1
        return decorator_func(func)
    else:
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

class LocustBase(object):
    """
    Locust base class defining a locust user/client.
    """
    
    tasks = []
    """
    List with python callables that represents a locust user task.

    If tasks is a list, the task to be performed will be picked randomly.

    If tasks is a *(callable,int)* list of two-tuples, or a  {callable:int} dict, 
    the task to be performed will be picked randomly, but each task will be weighted 
    according to it's corresponding int value. So in the following case *task1* will 
    be three times more likely to be picked than *task2*::

        class User(Locust):
            tasks = [(task1, 3), (task2, 1)]
    """
    
    host = None
    """Base hostname to swarm. i.e: http://127.0.0.1:1234"""

    min_wait = 1000
    """Minimum waiting time between the execution of locust tasks"""
    
    max_wait = 1000
    """Maximum waiting time between the execution of locust tasks"""

    avg_wait = None
    """Average waiting time wanted between the execution of locust tasks"""
    
    stop_timeout = None
    """Number of seconds after which the Locust will die. If None it won't timeout."""

    weight = 10
    """Probability of locust beeing choosen. The higher the weight, the greater is the chance of it beeing chosen."""
    
    __metaclass__ = LocustMeta
    
    def __init__(self):
        self._avg_wait = 0
        self._avg_wait_ctr = 0
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
            except GreenletExit:
                raise
            except Exception, e:
                events.locust_error.fire(self, e, sys.exc_info()[2])
                sys.stderr.write("\n" + traceback.format_exc())
    
    def execute_next_task(self):
        task = self._task_queue.pop(0)
        self.execute_task(task["callable"], *task["args"], **task["kwargs"])
    
    def execute_task(self, task, *args, **kwargs):
        # check if the function is a method bound to the current locust, and if so, don't pass self as first argument
        if hasattr(task, "im_self") and task.im_self == self:
            task(*args, **kwargs)
        else:
            task(self, *args, **kwargs)
    
    def schedule_task(self, task_callable, args=[], kwargs={}, first=False):
        """
        Add a task to the Locust's task execution queue.
        
        *Arguments*:
        
        * task_callable: Locust task to schedule
        * args: Arguments that will be passed to the task callable
        * kwargs: Dict of keyword arguments that will be passed to the task callable.
        * first: Optional keyword argument. If True, the task will be put first in the queue.
        """
        task = {"callable":task_callable, "args":args, "kwargs":kwargs}
        if first:
            self._task_queue.insert(0, task)
        else:
            self._task_queue.append(task)
    
    def get_next_task(self):
        return random.choice(self.tasks)
    
    def wait(self):
        if self.avg_wait:
            # Handle (strive for) average wait time
            if self._avg_wait:
                if self._avg_wait >= self.avg_wait:
                    # Want shorter wait
                    millis = random.randint(self.min_wait, self.avg_wait)
                else:
                    # Want longer wait
                    millis = random.randint(self.avg_wait, self.max_wait)
                self._avg_wait = ((self._avg_wait * self._avg_wait_ctr) + millis) / (self._avg_wait_ctr + 1.0)
            else:
                # Average specified but is first run
                radius = min(self.avg_wait - self.min_wait, self.max_wait - self.avg_wait)
                millis = random.randint(self.avg_wait - radius, self.avg_wait + radius)
                self._avg_wait = millis
            self._avg_wait_ctr += 1
        else:
            # Ignore average wait
            millis = random.randint(self.min_wait, self.max_wait)

        seconds = millis / 1000.0
        self._sleep(seconds)

    def _sleep(self, seconds):
        gevent.sleep(seconds)


class Locust(LocustBase):
    """
    Locust class that inherits from LocustBase and creates a *client* attribute on instantiation. 
    
    The *client* attribute is a simple HTTP client with support for keeping a user session between requests.
    """
    
    client = None
    """
    Instance of HttpSession that is created upon instantiation of Locust. 
    The client support cookies, and therefore keeps the session between HTTP requests.
    """
    
    def __init__(self):
        super(Locust, self).__init__()
        if self.host is None:
            raise LocustError("You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")
        
        self.client = HttpSession(base_url=self.host)

class WebLocust(Locust):
    def __init__(self, *args, **kwargs):
        warnings.warn("WebLocust class has been, deprecated. Use Locust class instead.")
        super(WebLocust, self).__init__(*args, **kwargs)

class SubLocust(LocustBase):
    """
    Class for making a sub Locust that can be included as a task inside of a normal Locust/WebLocus,
    as well as inside another sub locust. 
    
    When the parent locust enters the sub locust, it will not
    continue executing it's tasks until a task in the sub locust has called the interrupt() function.
    """
    
    def __init__(self, parent, *args, **kwargs):
        super(SubLocust, self).__init__()
        
        self.parent = parent
        if isinstance(parent, LocustBase):
            self.client = parent.client
        
        self.args = args
        self.kwargs = kwargs
        
        self()
    
    def interrupt(self, reschedule=True):
        """
        Interrupt the SubLocust and hand over execution control back to the parent Locust.
        
        If *reschedule* is True (default), the parent Locust will immediately re-schedule,
        and execute, a new task
        """
        raise InterruptLocust(reschedule)
