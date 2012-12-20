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

from exception import LocustError, InterruptTaskSet, RescheduleTask, RescheduleTaskImmediately, StopLocust

logger = logging.getLogger(__name__)


def task(weight=1):
    """
    Used as a convenience decorator to be able to declare tasks for a TaskSet 
    inline in the class. Example::
    
        class ForumPage(TaskSet):
            @task(100)
            def read_thread(self):
                pass
            
            @task(7)
            def create_thread(self):
                pass
    """
    
    def decorator_func(func):
        func.locust_task_weight = weight
        return func
    
    """
    Check if task was used without parentheses (not called), like this::
    
        @task
        def my_task()
            pass
    """
    if callable(weight):
        func = weight
        weight = 1
        return decorator_func(func)
    else:
        return decorator_func


class Locust(object):
    """
    Represents a "user" which is to be hatched and attack the system that is to be load tested.
    
    The behaviour of this user is defined by the task_set attribute, which should point to a 
    :py:class:`TaskSet <locust.core.TaskSet>` class.
    
    This class creates a *client* attribute on instantiation which is an HTTP client with support 
    for keeping a user session between requests.
    """
    
    host = None
    """Base hostname to swarm. i.e: http://127.0.0.1:1234"""
    
    min_wait = 1000
    """Minimum waiting time between the execution of locust tasks"""
    
    max_wait = 1000
    """Maximum waiting time between the execution of locust tasks"""
    
    avg_wait = None
    """Average waiting time wanted between the execution of locust tasks"""
    
    client = None
    """
    Instance of HttpSession that is created upon instantiation of Locust. 
    The client support cookies, and therefore keeps the session between HTTP requests.
    """
    
    task_set = None
    """TaskSet class that defines the execution behaviour of this locust"""
    
    stop_timeout = None
    """Number of seconds after which the Locust will die. If None it won't timeout."""

    weight = 10
    """Probability of locust being chosen. The higher the weight, the greater is the chance of it being chosen."""
    
    def __init__(self):
        super(Locust, self).__init__()
        if self.host is None:
            raise LocustError("You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")
        
        self.client = HttpSession(base_url=self.host)
    
    def run(self):
        try:
            self.task_set(self).run()
        except StopLocust:
            pass
        except (RescheduleTask, RescheduleTaskImmediately), e:
            raise LocustError, LocustError("A task inside a Locust class' main TaskSet (`%s.task_set` of type `%s`) seems to have called interrupt() or raised an InterruptTaskSet exception. The interrupt() function is used to hand over execution to a parent TaskSet, and should never be called in the main TaskSet which a Locust class' task_set attribute points to." % (type(self).__name__, self.task_set.__name__)), sys.exc_info()[2]


class TaskSetMeta(type):
    """
    Meta class for the main Locust class. It's used to allow Locust classes to specify task execution 
    ratio using an {task:int} dict, or a [(task0,int), ..., (taskN,int)] list.
    """
    
    def __new__(mcs, classname, bases, classDict):
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
        
        return type.__new__(mcs, classname, bases, classDict)

class TaskSet(object):
    """
    Class defining a set of tasks that a Locust user will execute. 
    
    When a TaskSet starts running, it will pick a task from the *tasks* attribute, 
    execute it, call it's wait function which will sleep a random number between
    *min_wait* and *max_wait* milliseconds. It will then schedule another task for 
    execution and so on.
    
    TaskTests can be nested, which means that a TaskSet's *tasks* attribute can contain 
    another TaskSet. If the nested TaskSet it scheduled to be executed, it will be 
    instantiated and called from the current executing TaskSet. Execution in the the
    currently running TaskSet will then be handed over to the nested TaskSet which will 
    continue to run until it throws an InterruptTaskSet exception, which is done when 
    :py:meth:`TaskSet.interrupt() <locust.core.TaskSet.interrupt>` is called. (execution 
    will then continue in the first TaskSet).
    """
    
    tasks = []
    """
    List with python callables that represents a locust user task.

    If tasks is a list, the task to be performed will be picked randomly.

    If tasks is a *(callable,int)* list of two-tuples, or a  {callable:int} dict, 
    the task to be performed will be picked randomly, but each task will be weighted 
    according to it's corresponding int value. So in the following case *ThreadPage* will 
    be fifteen times more likely to be picked than *write_post*::

        class ForumPage(TaskSet):
            tasks = {ThreadPage:15, write_post:1}
    """
    
    min_wait = None
    """
    Minimum waiting time between the execution of locust tasks. Can be used to override 
    the min_wait defined in the root Locust class, which will be used if not set on the 
    TaskSet.
    """
    
    max_wait = None
    """
    Maximum waiting time between the execution of locust tasks. Can be used to override 
    the max_wait defined in the root Locust class, which will be used if not set on the 
    TaskSet.
    """
    
    avg_wait = None
    """Average waiting time wanted between the execution of locust tasks"""
    
    client = None
    """
    Reference to the :py:attr:`client <locust.core.Locust.client>` attribute of the root 
    Locust instance.
    """
    
    locust = None
    """Will refer to the root Locust class when the TaskSet has been instantiated"""

    parent = None
    """Will refer to the parent class when the TaskSet has been instantiated
    Useful for nested TaskSet classes
    """

    __metaclass__ = TaskSetMeta    
    
    def __init__(self, parent):
        self._avg_wait = 0
        self._avg_wait_ctr = 0
        self._task_queue = []
        self._time_start = time()
        
        if isinstance(parent, TaskSet):
            self.locust = parent.locust
        elif isinstance(parent, Locust):
            self.locust = parent
        else:
            raise LocustError("TaskSet should be called with Locust instance or TaskSet instance as first argument")

        self.parent = parent
        self.client = self.locust.client
        
        # if this class doesn't have a min_wait, max_wait or avg_wait defined, copy it from Locust
        if not self.min_wait:
            self.min_wait = self.locust.min_wait
        if not self.max_wait:
            self.max_wait = self.locust.max_wait
        if not self.avg_wait:
            self.avg_wait = self.locust.avg_wait

    def run(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
        if hasattr(self, "on_start"):
            self.on_start()
        while (True):
            try:
                if self.locust.stop_timeout is not None and time() - self._time_start > self.locust.stop_timeout:
                    return
        
                if not self._task_queue:
                    self.schedule_task(self.get_next_task())
                
                try:
                    self.execute_next_task()
                except RescheduleTaskImmediately:
                    pass
                except RescheduleTask:
                    self.wait()
                else:
                    self.wait()
            except InterruptTaskSet, e:
                if e.reschedule:
                    raise RescheduleTaskImmediately, e, sys.exc_info()[2]
                else:
                    raise RescheduleTask, e, sys.exc_info()[2]
            except StopLocust:
                raise
            except GreenletExit:
                raise
            except Exception, e:
                events.locust_error.fire(self, e, sys.exc_info()[2])
                sys.stderr.write("\n" + traceback.format_exc())
                self.wait()
    
    def execute_next_task(self):
        task = self._task_queue.pop(0)
        self.execute_task(task["callable"], *task["args"], **task["kwargs"])
    
    def execute_task(self, task, *args, **kwargs):
        # check if the function is a method bound to the current locust, and if so, don't pass self as first argument
        if hasattr(task, "im_self") and task.im_self == self:
            # task is a bound method on self
            task(*args, **kwargs)
        elif hasattr(task, "tasks") and issubclass(task, TaskSet):
            # task is another (nested) TaskSet class
            task(self).run(*args, **kwargs)
        else:
            # task is a function
            task(self, *args, **kwargs)
    
    def schedule_task(self, task_callable, args=None, kwargs=None, first=False):
        """
        Add a task to the Locust's task execution queue.
        
        *Arguments*:
        
        * task_callable: Locust task to schedule
        * args: Arguments that will be passed to the task callable
        * kwargs: Dict of keyword arguments that will be passed to the task callable.
        * first: Optional keyword argument. If True, the task will be put first in the queue.
        """
        task = {"callable":task_callable, "args":args or [], "kwargs":kwargs or {}}
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
    
    def interrupt(self, reschedule=True):
        """
        Interrupt the TaskSet and hand over execution control back to the parent TaskSet.
        
        If *reschedule* is True (default), the parent Locust will immediately re-schedule,
        and execute, a new task
        
        This method should not be called by the root TaskSet (the one that is immediately, 
        attached to the Locust class' *task_set* attribute), but rather in nested TaskSet
        classes further down the hierarchy.
        """
        raise InterruptTaskSet(reschedule)

class WebLocust(Locust):
    def __init__(self, *args, **kwargs):
        warnings.warn("WebLocust class has been, deprecated. Use Locust class instead.")
        super(WebLocust, self).__init__()


class SubLocust(object):
    """
    Class for making a sub Locust that can be included as a task inside of a normal Locust/WebLocus,
    as well as inside another sub locust.

    When the parent locust enters the sub locust, it will not
    continue executing it's tasks until a task in the sub locust has called the interrupt() function.
    """
    def __init__(self, *args, **kwargs):
        raise DeprecationWarning("The SubLocust class has been deprecated. Use TaskSet classes instead.")
