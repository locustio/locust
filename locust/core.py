import logging
import random
import sys
import traceback
from time import time

import gevent
from gevent import GreenletExit, monkey

# The monkey patching must run before requests is imported, or else 
# we'll get an infinite recursion when doing SSL/HTTPS requests.
# See: https://github.com/requests/requests/issues/3752#issuecomment-294608002
monkey.patch_all()

from .clients import HttpSession
from .exception import (InterruptTaskSet, LocustError, RescheduleTask,
                        RescheduleTaskImmediately, StopLocust, MissingWaitTimeError)
from .util import deprecation


logger = logging.getLogger(__name__)


LOCUST_STATE_RUNNING, LOCUST_STATE_WAITING, LOCUST_STATE_STOPPING = ["running", "waiting", "stopping"]


def task(weight=1):
    """
    Used as a convenience decorator to be able to declare tasks for a Locust or a TaskSet 
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


class NoClientWarningRaiser(object):
    """
    The purpose of this class is to emit a sensible error message for old test scripts that 
    inherits from Locust, and expects there to be an HTTP client under the client attribute.
    """
    def __getattr__(self, _):
        raise LocustError("No client instantiated. Did you intend to inherit from HttpLocust?")


def get_tasks_from_base_classes(bases, class_dict):
    """
    Function used by both TaskSetMeta and LocustMeta for collecting all declared tasks 
    on the TaskSet/Locust class and all it's base classes
    """
    new_tasks = []
    for base in bases:
        if hasattr(base, "tasks") and base.tasks:
            new_tasks += base.tasks
    
    if "tasks" in class_dict and class_dict["tasks"] is not None:
        tasks = class_dict["tasks"]
        if isinstance(tasks, dict):
            tasks = tasks.items()
        
        for task in tasks:
            if isinstance(task, tuple):
                task, count = task
                for i in range(count):
                    new_tasks.append(task)
            else:
                new_tasks.append(task)
    
    for item in class_dict.values():
        if "locust_task_weight" in dir(item):
            for i in range(0, item.locust_task_weight):
                new_tasks.append(item)
    
    return new_tasks


class TaskSetMeta(type):
    """
    Meta class for the main Locust class. It's used to allow Locust classes to specify task execution 
    ratio using an {task:int} dict, or a [(task0,int), ..., (taskN,int)] list.
    """
    
    def __new__(mcs, classname, bases, class_dict):
        class_dict["tasks"] = get_tasks_from_base_classes(bases, class_dict)
        return type.__new__(mcs, classname, bases, class_dict)


class TaskSet(object, metaclass=TaskSetMeta):
    """
    Class defining a set of tasks that a Locust user will execute. 
    
    When a TaskSet starts running, it will pick a task from the *tasks* attribute, 
    execute it, and then sleep for the number of seconds returned by it's *wait_time* 
    function. If no wait_time method has been declared on the TaskSet, it'll call the 
    wait_time function on the Locust by default. It will then schedule another task 
    for execution and so on.
    
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
    Collection of python callables and/or TaskSet classes that the Locust user(s) will run.

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
    Deprecated: Use wait_time instead. 
    Minimum waiting time between the execution of locust tasks. Can be used to override 
    the min_wait defined in the root Locust class, which will be used if not set on the 
    TaskSet.
    """
    
    max_wait = None
    """
    Deprecated: Use wait_time instead. 
    Maximum waiting time between the execution of locust tasks. Can be used to override 
    the max_wait defined in the root Locust class, which will be used if not set on the 
    TaskSet.
    """
    
    wait_function = None
    """
    Deprecated: Use wait_time instead.
    Function used to calculate waiting time between the execution of locust tasks in milliseconds. 
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

    def __init__(self, parent):
        # check if deprecated wait API is used
        deprecation.check_for_deprecated_wait_api(self)
        
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

    def on_start(self):
        """
        Called when a Locust user starts executing (enters) this TaskSet
        """
        pass
    
    def on_stop(self):
        """
        Called when a Locust user stops executing this TaskSet. E.g. when Taskset.interrupt() is called 
        or when the user is killed
        """
        pass

    def run(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
        try:
            self.on_start()
        except InterruptTaskSet as e:
            if e.reschedule:
                raise RescheduleTaskImmediately(e.reschedule).with_traceback(sys.exc_info()[2])
            else:
                raise RescheduleTask(e.reschedule).with_traceback(sys.exc_info()[2])
        
        while (True):
            try:
                if not self._task_queue:
                    self.schedule_task(self.get_next_task())
                
                try:
                    self._check_stop_condition()
                    self.execute_next_task()
                except RescheduleTaskImmediately:
                    pass
                except RescheduleTask:
                    self.wait()
                else:
                    self.wait()
            except InterruptTaskSet as e:
                self.on_stop()
                if e.reschedule:
                    raise RescheduleTaskImmediately(e.reschedule) from e
                else:
                    raise RescheduleTask(e.reschedule) from e
            except (StopLocust, GreenletExit):
                self.on_stop()
                raise
            except Exception as e:
                self.locust.environment.events.locust_error.fire(locust_instance=self, exception=e, tb=sys.exc_info()[2])
                if self.locust.environment.catch_exceptions:
                    logger.error("%s\n%s", e, traceback.format_exc())
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
        if not self.tasks:
            raise Exception("No tasks defined. use the @task decorator or set the tasks property of the TaskSet")
        return random.choice(self.tasks)
    
    def wait_time(self):
        """
        Method that returns the time (in seconds) between the execution of tasks. 
        
        Example::
        
            from locust import TaskSet, between
            class Tasks(TaskSet):
                wait_time = between(3, 25)
        """
        if self.locust.wait_time:
            return self.locust.wait_time()
        elif self.min_wait is not None and self.max_wait is not None:
            return random.randint(self.min_wait, self.max_wait) / 1000.0
        else:
            raise MissingWaitTimeError("You must define a wait_time method on either the %s or %s class" % (
                type(self.locust).__name__, 
                type(self).__name__,
            ))
    
    def wait(self):
        """
        Make the running locust user sleep for a duration defined by the Locust.wait_time 
        function (or TaskSet.wait_time function if it's been defined). 
        
        The user can also be killed gracefully while it's sleeping so calling this 
        method within a task makes it possible for a user to be killed mid-task even if you've 
        set a stop_timeout. If this behavour is not desired you should make the user wait using 
        gevent.sleep() instead.
        """
        self._check_stop_condition()
        self.locust._state = LOCUST_STATE_WAITING
        self._sleep(self.wait_time())
        self._check_stop_condition()
        self.locust._state = LOCUST_STATE_RUNNING

    def _sleep(self, seconds):
        gevent.sleep(seconds)
    
    def _check_stop_condition(self):
        if self.locust._state == LOCUST_STATE_STOPPING:
            raise StopLocust()
    
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


class DefaultTaskSet(TaskSet):
    """
    Default root TaskSet that executes tasks in Locust.tasks.
    It executes tasks declared directly on the Locust with the Locust user instance as the task argument.
    """
    def get_next_task(self):
        return random.choice(self.locust.tasks)
    
    def execute_task(self, task, *args, **kwargs):
        if hasattr(task, "tasks") and issubclass(task, TaskSet):
            # task is  (nested) TaskSet class
            task(self.locust).run(*args, **kwargs)
        else:
            # task is a function
            task(self.locust, *args, **kwargs)


class LocustMeta(type):
    """
    Meta class for the main Locust class. It's used to allow Locust classes to specify task execution 
    ratio using an {task:int} dict, or a [(task0,int), ..., (taskN,int)] list.
    """
    def __new__(mcs, classname, bases, class_dict):
        # gather any tasks that is declared on the class (or it's bases)
        tasks = get_tasks_from_base_classes(bases, class_dict)   
        class_dict["tasks"] = tasks
        
        if not class_dict.get("abstract"):
            # Not a base class
            class_dict["abstract"] = False
        
        # check if class uses deprecated task_set attribute
        deprecation.check_for_deprecated_task_set_attribute(class_dict)
        
        return type.__new__(mcs, classname, bases, class_dict)


class Locust(object, metaclass=LocustMeta):
    """
    Represents a "user" which is to be hatched and attack the system that is to be load tested.
    
    The behaviour of this user is defined by it's tasks. Tasks can be declared either directly on the 
    class by using the :py:func:`@task decorator <locust.core.task>` on the methods, or by setting 
    the :py:attr:`tasks attribute <locust.core.Locust.tasks>`.
    
    This class should usually be subclassed by a class that defines some kind of client. For 
    example when load testing an HTTP system, you probably want to use the 
    :py:class:`HttpLocust <locust.core.HttpLocust>` class.
    """
    
    host = None
    """Base hostname to swarm. i.e: http://127.0.0.1:1234"""
    
    min_wait = None
    """Deprecated: Use wait_time instead. Minimum waiting time between the execution of locust tasks"""
    
    max_wait = None
    """Deprecated: Use wait_time instead. Maximum waiting time between the execution of locust tasks"""
    
    wait_time = None
    """
    Method that returns the time (in seconds) between the execution of locust tasks. 
    Can be overridden for individual TaskSets.
    
    Example::
    
        from locust import Locust, between
        class User(Locust):
            wait_time = between(3, 25)
    """
    
    wait_function = None
    """
    .. warning::
    
        DEPRECATED: Use wait_time instead. Note that the new wait_time method should return seconds and not milliseconds.
    
    Method that returns the time between the execution of locust tasks in milliseconds
    """
    
    tasks = []
    """
    Collection of python callables and/or TaskSet classes that the Locust user(s) will run.

    If tasks is a list, the task to be performed will be picked randomly.

    If tasks is a *(callable,int)* list of two-tuples, or a  {callable:int} dict, 
    the task to be performed will be picked randomly, but each task will be weighted 
    according to it's corresponding int value. So in the following case *ThreadPage* will 
    be fifteen times more likely to be picked than *write_post*::

        class ForumPage(TaskSet):
            tasks = {ThreadPage:15, write_post:1}
    """

    weight = 10
    """Probability of locust being chosen. The higher the weight, the greater is the chance of it being chosen."""
    
    abstract = True
    """If abstract is True it the class is meant to be subclassed (users of this class itself will not be spawned during a test)"""
    
    client = NoClientWarningRaiser()
    _state = None
    _greenlet = None
    _taskset_instance = None
    
    def __init__(self, environment):
        super(Locust, self).__init__()
        # check if deprecated wait API is used
        deprecation.check_for_deprecated_wait_api(self)
        self.environment = environment
    
    def on_start(self):
        """
        Called when a Locust user starts running. 
        """
        pass
    
    def on_stop(self):
        """
        Called when a Locust user stops running (is killed)
        """
        pass
    
    def run(self):
        self._state = LOCUST_STATE_RUNNING
        self._taskset_instance = DefaultTaskSet(self)
        try:
            # run the task_set on_start method, if it has one
            self.on_start()
            
            self._taskset_instance.run()
        except (GreenletExit, StopLocust) as e:
            # run the on_stop method, if it has one
            self.on_stop()
    
    def wait(self):
        """
        Make the running locust user sleep for a duration defined by the Locust.wait_time 
        function. 
        
        The user can also be killed gracefully while it's sleeping so calling this 
        method within a task makes it possible for a user to be killed mid-task even if you've 
        set a stop_timeout. If this behavour is not desired you should make the user wait using 
        gevent.sleep() instead.
        """
        self._taskset_instance.wait()
    
    def start(self, gevent_group):
        """
        Start a greenlet that runs this locust instance. 
        
        *Arguments*:
        
        * gevent_group:  gevent.pool.Group instance where the greenlet will be spawned.
        
        Returns the spawned greenlet.
        """
        def run_locust(user):
            """
            Main function for Locust user greenlet. It's important that this function takes the locust 
            instance as argument, since we use greenlet_instance.args[0] to retrieve a reference to the 
            locust instance.
            """
            user.run()
        self._greenlet = gevent_group.spawn(run_locust, self)
        return self._greenlet
    
    def stop(self, gevent_group, force=False):
        """
        Stop the locust user greenlet that exists in the gevent_group. 
        This method is not meant to be called from within of the Locust's greenlet. 
        
        *Arguments*:
        
        * gevent_group:  gevent.pool.Group instance where the greenlet will be spawned.
        * force: If False (the default) the stopping is done gracefully by setting the state to LOCUST_STATE_STOPPING 
                 which will make the Locust instance stop once any currently running task is complete and on_stop 
                 methods are called. If force is True the greenlet will be killed immediately.
        
        Returns True if the greenlet was killed immediately, otherwise False
        """
        if force or self._state == LOCUST_STATE_WAITING:
            gevent_group.killone(self._greenlet)
            return True
        elif self._state == LOCUST_STATE_RUNNING:
            self._state = LOCUST_STATE_STOPPING
            return False


class HttpLocust(Locust):
    """
    Represents an HTTP "user" which is to be hatched and attack the system that is to be load tested.
    
    The behaviour of this user is defined by it's tasks. Tasks can be declared either directly on the 
    class by using the :py:func:`@task decorator <locust.core.task>` on the methods, or by setting 
    the :py:attr:`tasks attribute <locust.core.Locust.tasks>`.
    
    This class creates a *client* attribute on instantiation which is an HTTP client with support 
    for keeping a user session between requests.
    """
    
    abstract = True
    """If abstract is True it the class is meant to be subclassed (users of this class itself will not be spawned during a test)"""
    
    client = None
    """
    Instance of HttpSession that is created upon instantiation of Locust. 
    The client support cookies, and therefore keeps the session between HTTP requests.
    """
    
    def __init__(self, *args, **kwargs):
        super(HttpLocust, self).__init__(*args, **kwargs)
        if self.host is None:
            raise LocustError("You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")

        session = HttpSession(
            base_url=self.host, 
            request_success=self.environment.events.request_success, 
            request_failure=self.environment.events.request_failure,
        )
        session.trust_env = False
        self.client = session
