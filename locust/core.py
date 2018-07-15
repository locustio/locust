import logging
import random
import sys
import traceback
from time import time

import gevent
import gevent.lock
import six

from gevent import GreenletExit, monkey
from six.moves import xrange

# The monkey patching must run before requests is imported, or else 
# we'll get an infinite recursion when doing SSL/HTTPS requests.
# See: https://github.com/requests/requests/issues/3752#issuecomment-294608002
monkey.patch_all()

from . import events
from .clients import HttpSession
from .exception import (InterruptTaskSet, LocustError, RescheduleTask,
                        RescheduleTaskImmediately, StopLocust)
from .runners import STATE_CLEANUP
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


def seq_task(order):
    """
    Used as a convenience decorator to be able to declare tasks for a TaskSequence
    inline in the class. Example::

        class NormalUser(TaskSequence):
            @seq_task(1)
            def login_first(self):
                pass

            @seq_task(2)
            @task(25) # You can also set the weight in order to execute the task for `weight` times one after another.
            def then_read_thread(self):
                pass

            @seq_task(3)
            def then_logout(self):
                pass
    """

    def decorator_func(func):
        func.locust_task_order = order
        if not hasattr(func, 'locust_task_weight'):
            func.locust_task_weight = 1
        return func

    return decorator_func


class NoClientWarningRaiser(object):
    """
    The purpose of this class is to emit a sensible error message for old test scripts that 
    inherits from Locust, and expects there to be an HTTP client under the client attribute.
    """
    def __getattr__(self, _):
        raise LocustError("No client instantiated. Did you intend to inherit from HttpLocust?")


class Locust(object):
    """
    Represents a "user" which is to be hatched and attack the system that is to be load tested.
    
    The behaviour of this user is defined by the task_set attribute, which should point to a 
    :py:class:`TaskSet <locust.core.TaskSet>` class.
    
    This class should usually be subclassed by a class that defines some kind of client. For 
    example when load testing an HTTP system, you probably want to use the 
    :py:class:`HttpLocust <locust.core.HttpLocust>` class.
    """
    
    host = None
    """Base hostname to swarm. i.e: http://127.0.0.1:1234"""
    
    min_wait = 1000
    """Minimum waiting time between the execution of locust tasks"""
    
    max_wait = 1000
    """Maximum waiting time between the execution of locust tasks"""

    wait_function = lambda self: random.randint(self.min_wait,self.max_wait) 
    """Function used to calculate waiting time between the execution of locust tasks in milliseconds"""
    
    task_set = None
    """TaskSet class that defines the execution behaviour of this locust"""
    
    stop_timeout = None
    """Number of seconds after which the Locust will die. If None it won't timeout."""

    weight = 10
    """Probability of locust being chosen. The higher the weight, the greater is the chance of it being chosen."""
        
    client = NoClientWarningRaiser()
    _catch_exceptions = True
    _setup_has_run = False  # Internal state to see if we have already run
    _teardown_is_set = False  # Internal state to see if we have already run
    _lock = gevent.lock.Semaphore()  # Lock to make sure setup is only run once
    
    def __init__(self):
        super(Locust, self).__init__()
        self._lock.acquire()
        if hasattr(self, "setup") and self._setup_has_run is False:
            self._set_setup_flag()
            self.setup()
        if hasattr(self, "teardown") and self._teardown_is_set is False:
            self._set_teardown_flag()
            events.quitting += self.teardown
        self._lock.release()

    @classmethod
    def _set_setup_flag(cls):
        cls._setup_has_run = True

    @classmethod
    def _set_teardown_flag(cls):
        cls._teardown_is_set = True
    
    def run(self, runner=None):
        task_set_instance = self.task_set(self)
        try:
            task_set_instance.run()
        except StopLocust:
            pass
        except (RescheduleTask, RescheduleTaskImmediately) as e:
            six.reraise(LocustError, LocustError("A task inside a Locust class' main TaskSet (`%s.task_set` of type `%s`) seems to have called interrupt() or raised an InterruptTaskSet exception. The interrupt() function is used to hand over execution to a parent TaskSet, and should never be called in the main TaskSet which a Locust class' task_set attribute points to." % (type(self).__name__, self.task_set.__name__)), sys.exc_info()[2])
        except GreenletExit as e:
            if runner:
                runner.state = STATE_CLEANUP
            # Run the task_set on_stop method, if it has one
            if hasattr(task_set_instance, "on_stop"):
                task_set_instance.on_stop()
            raise  # Maybe something relies on this except being raised?


class HttpLocust(Locust):
    """
    Represents an HTTP "user" which is to be hatched and attack the system that is to be load tested.
    
    The behaviour of this user is defined by the task_set attribute, which should point to a 
    :py:class:`TaskSet <locust.core.TaskSet>` class.
    
    This class creates a *client* attribute on instantiation which is an HTTP client with support 
    for keeping a user session between requests.
    """
    
    client = None
    """
    Instance of HttpSession that is created upon instantiation of Locust. 
    The client support cookies, and therefore keeps the session between HTTP requests.
    """
    
    def __init__(self):
        super(HttpLocust, self).__init__()
        if self.host is None:
            raise LocustError("You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")
        
        self.client = HttpSession(base_url=self.host)


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
                tasks = six.iteritems(tasks)
            
            for task in tasks:
                if isinstance(task, tuple):
                    task, count = task
                    for i in xrange(0, count):
                        new_tasks.append(task)
                else:
                    new_tasks.append(task)
        
        for item in six.itervalues(classDict):
            if hasattr(item, "locust_task_weight"):
                for i in xrange(0, item.locust_task_weight):
                    new_tasks.append(item)
        
        classDict["tasks"] = new_tasks
        
        return type.__new__(mcs, classname, bases, classDict)

@six.add_metaclass(TaskSetMeta)
class TaskSet(object):
    """
    Class defining a set of tasks that a Locust user will execute. 
    
    When a TaskSet starts running, it will pick a task from the *tasks* attribute, 
    execute it, and call its *wait_function* which will define a time to sleep for. 
    This defaults to a uniformly distributed random number between *min_wait* and 
    *max_wait* milliseconds. It will then schedule another task for execution and so on.
    
    TaskSets can be nested, which means that a TaskSet's *tasks* attribute can contain 
    another TaskSet. If the nested TaskSet it scheduled to be executed, it will be 
    instantiated and called from the current executing TaskSet. Execution in the
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
    
    wait_function = None
    """
    Function used to calculate waiting time betwen the execution of locust tasks in milliseconds. 
    Can be used to override the wait_function defined in the root Locust class, which will be used
    if not set on the TaskSet.
    """

    locust = None
    """Will refer to the root Locust class instance when the TaskSet has been instantiated"""

    parent = None
    """
    Will refer to the parent TaskSet, or Locust, class instance when the TaskSet has been 
    instantiated. Useful for nested TaskSet classes.
    """

    _setup_has_run = False  # Internal state to see if we have already run
    _teardown_is_set = False  # Internal state to see if we have already run
    _lock = gevent.lock.Semaphore()  # Lock to make sure setup is only run once

    def __init__(self, parent):
        self._task_queue = []
        self._time_start = time()
        
        if isinstance(parent, TaskSet):
            self.locust = parent.locust
        elif isinstance(parent, Locust):
            self.locust = parent
        else:
            raise LocustError("TaskSet should be called with Locust instance or TaskSet instance as first argument")

        self.parent = parent
        
        # if this class doesn't have a min_wait, max_wait or wait_function defined, copy it from Locust
        if not self.min_wait:
            self.min_wait = self.locust.min_wait
        if not self.max_wait:
            self.max_wait = self.locust.max_wait
        if not self.wait_function:
            self.wait_function = self.locust.wait_function

        self._lock.acquire()
        if hasattr(self, "setup") and self._setup_has_run is False:
            self._set_setup_flag()
            self.setup()
        if hasattr(self, "teardown") and self._teardown_is_set is False:
            self._set_teardown_flag()
            events.quitting += self.teardown
        self._lock.release()

    @classmethod
    def _set_setup_flag(cls):
        cls._setup_has_run = True

    @classmethod
    def _set_teardown_flag(cls):
        cls._teardown_is_set = True

    def run(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
        try:
            if hasattr(self, "on_start"):
                self.on_start()
        except InterruptTaskSet as e:
            if e.reschedule:
                six.reraise(RescheduleTaskImmediately, RescheduleTaskImmediately(e.reschedule), sys.exc_info()[2])
            else:
                six.reraise(RescheduleTask, RescheduleTask(e.reschedule), sys.exc_info()[2])
        
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
            except InterruptTaskSet as e:
                if e.reschedule:
                    six.reraise(RescheduleTaskImmediately, RescheduleTaskImmediately(e.reschedule), sys.exc_info()[2])
                else:
                    six.reraise(RescheduleTask, RescheduleTask(e.reschedule), sys.exc_info()[2])
            except StopLocust:
                raise
            except GreenletExit:
                raise
            except Exception as e:
                events.locust_error.fire(locust_instance=self, exception=e, tb=sys.exc_info()[2])
                if self.locust._catch_exceptions:
                    sys.stderr.write("\n" + traceback.format_exc())
                    self.wait()
                else:
                    raise
    
    def execute_next_task(self):
        task = self._task_queue.pop(0)
        self.execute_task(task["callable"], *task["args"], **task["kwargs"])
    
    def execute_task(self, task, *args, **kwargs):
        # check if the function is a method bound to the current locust, and if so, don't pass self as first argument
        if hasattr(task, "__self__") and task.__self__ == self:
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
    
    def get_wait_secs(self):
        millis = self.wait_function()
        return millis / 1000.0

    def wait(self):
        self._sleep(self.get_wait_secs())

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
    
    @property
    def client(self):
        """
        Reference to the :py:attr:`client <locust.core.Locust.client>` attribute of the root 
        Locust instance.
        """
        return self.locust.client


class TaskSequence(TaskSet):
    """
    Class defining a sequence of tasks that a Locust user will execute.

    When a TaskSequence starts running, it will pick the task in `index` from the *tasks* attribute,
    execute it, and call its *wait_function* which will define a time to sleep for.
    This defaults to a uniformly distributed random number between *min_wait* and
    *max_wait* milliseconds. It will then schedule the `index + 1 % len(tasks)` task for execution and so on.

    TaskSequence can be nested with TaskSet, which means that a TaskSequence's *tasks* attribute can contain
    TaskSet instances as well as other TaskSequence instances. If the nested TaskSet it scheduled to be executed, it will be
    instantiated and called from the current executing TaskSet. Execution in the
    currently running TaskSet will then be handed over to the nested TaskSet which will
    continue to run until it throws an InterruptTaskSet exception, which is done when
    :py:meth:`TaskSet.interrupt() <locust.core.TaskSet.interrupt>` is called. (execution
    will then continue in the first TaskSet).

    In this class, tasks should be defined as a list, or simply define the tasks with the @seq_task decorator
    """

    def __init__(self, parent):
        super(TaskSequence, self).__init__(parent)
        self._index = 0
        self.tasks.sort(key=lambda t: t.locust_task_order if hasattr(t, 'locust_task_order') else 1)

    def get_next_task(self):
        task = self.tasks[self._index]
        self._index = (self._index + 1) % len(self.tasks)
        return task
