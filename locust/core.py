import logging
import random
import sys
import traceback
from time import time
from collections import defaultdict

import gevent
import six
from gevent import GreenletExit, monkey

from six.moves import xrange

from . import events
from .clients import HttpSession, SocketIOClient, ZMQClient
from .exception import (InterruptTaskSet, LocustError, RescheduleTask,
                        RescheduleTaskImmediately, StopLocust)

monkey.patch_all(thread=False)
logger = logging.getLogger(__name__)


def task(weight=1):
    """
    Used as a convenience decorator to be able to declare tasks for a TaskSet
    inline in the class. Example:

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

def mod_context(key, value):
    """Decorator way to set context variables to task"""
    def wrapper_func(func):
        mods = getattr(func, 'context_mods', {})
        mods[key] = value
        func.context_mods = mods
        return func

    return wrapper_func

class NoClientWarningRaiser(object):
    """
    The purpose of this class is to emit a sensible error message for old test scripts that
    inherits from Locust, and expects there to be an HTTP client under the client attribute.
    """
    def __getattr__(self, _):
        raise LocustError("No client instantiated. Did you intend to inherit from WebLocust?")


class Locust(object):
    """
    Represents a "user" which is to be hatched and attack the system that is to be load tested.

    The behaviour of this user is defined by the task_set attribute, which should point to a
    :py:class:`TaskSet <locust.core.TaskSet>` class.

    This class should usually be subclassed by a class that defines some kind of client. For
    example when load testing an HTTP system, you probably want to use the
    :py:class:`WebLocust <locust.core.WebLocust>` class.
    """

    task_set = None
    """TaskSet class that defines the execution behaviour of this locust"""

    min_wait = None
    """Minimum waiting time between the execution of locust tasks"""

    max_wait = None
    """Maximum waiting time between the execution of locust tasks"""

    weight = 10
    """Probability of locust being chosen. The higher the weight, the greater is the chance of it being chosen."""

    http = NoClientWarningRaiser()
    socket_io = NoClientWarningRaiser()
    zmq = NoClientWarningRaiser()
    _catch_exceptions = True

    def __init__(self, options):
        super(Locust, self).__init__()
        self.current_task = None
        self.options = options
        self.host = options.host
        self.min_wait = self.min_wait or options.min_wait
        self.max_wait = self.max_wait or options.max_wait
        self.stop_timeout = options.stop_timeout

    def run(self):
        try:
            self.task_set(self).run()
        except StopLocust:
            pass
        except (RescheduleTask, RescheduleTaskImmediately) as e:
            six.reraise(LocustError, LocustError("A task inside a Locust class' main TaskSet (`%s.task_set` of type `%s`) seems to have called interrupt() or raised an InterruptTaskSet exception. The interrupt() function is used to hand over execution to a parent TaskSet, and should never be called in the main TaskSet which a Locust class' task_set attribute points to." % (type(self).__name__, self.task_set.__name__)), sys.exc_info()[2])


class LocustWebClient(object):
    """
    Wrapper around HTTP, SocketIO, ZMQ Locust clients to be used as single entry point
    for Locust Task
    """

    def __init__(self, locust):
        self.locust = locust
        self.host = locust.host
        self.config = locust.options
        self._http_client = None
        self._socket_io_client = None
        self._zmq_client = None
        self.context = defaultdict(lambda: None)
        self.persistent_values = {}

    @property
    def http(self):
        """Lazy creation of http client HttpSession"""
        if not self._http_client:
            self._http_client = HttpSession(locust=self.locust, base_url=self.host)
        return self._http_client

    @property
    def socket_io(self):
        """Lazy creation of socketIO client SocketIOClient"""
        if not self._socket_io_client:
            self._socket_io_client = SocketIOClient(
                self.locust,
                self.host,
                self.config.socket_io_resource,
                self.config.socket_io_service
            )
        return self._socket_io_client

    @property
    def zmq(self):
        """Lazy creation of zmq client ZMQClient"""
        if not self._zmq_client:
            self._zmq_client = ZMQClient(self.locust, self.host, 'zmq')
        return self._zmq_client

    def reopen_connections(self):
        """Close existing connections and for future lazy open"""
        if self._http_client:
            self._http_client.close()
            self._http_client = None
        if self._socket_io_client:
            self._socket_io_client.close()
            self._socket_io_client = None
        if self._zmq_client:
            self._zmq_client.close()
            self._zmq_client = None

    def clear_context(self):
        """Clearing context without flushing "persistent" clients values"""
        self.context.clear()
        self.context.update(self.persistent_values)

class WebLocust(Locust):
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

    def __init__(self, options):
        super(WebLocust, self).__init__(options)
        if self.host is None:
            raise LocustError("You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")

        self.client = LocustWebClient(self)


class TaskSetMeta(type):
    """
    Meta class for the main Locust class. Its used to allow Locust classes to specify task execution
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
    execute it, call it's wait function which will sleep a random number between
    *min_wait* and *max_wait* milliseconds. It will then schedule another task for
    execution and so on.

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

    locust = None
    """Will refer to the root Locust class instance when the TaskSet has been instantiated"""

    parent = None
    """
    Will refer to the parent TaskSet, or Locust, class instance when the TaskSet has been
    instantiated. Useful for nested TaskSet classes.
    """

    def __init__(self, parent):
        self._task_queue = []
        self._time_start = time()

        if isinstance(parent, TaskSet):
            self.locust = parent.locust
            self.base_name = "{}::{}".format(parent.__class__.__name__, self.locust.__class__.__name__)
        elif isinstance(parent, Locust):
            self.locust = parent
            self.base_name = parent.__class__.__name__
        else:
            raise LocustError("TaskSet should be called with Locust instance or TaskSet instance as first argument")

        self.parent = parent

        # if this class doesn't have a min_wait or max_wait defined, copy it from Locust
        if not self.min_wait:
            self.min_wait = self.locust.min_wait
        if not self.max_wait:
            self.max_wait = self.locust.max_wait

    def run(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        try:
            if hasattr(self, "on_start"):
                self.on_start()
                if hasattr(self, "client"):
                    self.client.persistent_values = self.client.context.copy()
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
                    task_start_time = time()
                    if hasattr(self, 'on_task_start'):
                        self.on_task_start()
                    self.execute_next_task()
                except RescheduleTaskImmediately as e:
                    self.fire_task_failure(task_start_time, e.reason, e.action)
                    pass
                except RescheduleTask as e:
                    self.fire_task_failure(task_start_time, e.reason, e.action)
                    self.wait()
                else:
                    self.fire_task_success(task_start_time)
                    self.wait()
                self.locust.current_task = ""
                if hasattr(self, 'on_task_end'):
                    self.on_task_end()
                    self.client.clear_context()
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
        self._apply_task_context(task)
        self.execute_task(task["callable"], *task["args"], **task["kwargs"])

    def execute_task(self, task, *args, **kwargs):
        # check if the function is a method bound to the current locust, and if so, don't pass self as first argument
        self.locust.current_task = "{}::{}".format(
            self.base_name,
            task.__name__.replace('_', ' ')
        )

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

    def wait(self):
        millis = random.randint(self.min_wait, self.max_wait)
        seconds = millis / 1000.0
        self._sleep(seconds)

    def _sleep(self, seconds):
        gevent.sleep(seconds)

    def fire_task_success(self, start_time):
        events.task_success.fire(
            task_name=self.locust.current_task,
            task_time=int((time() - start_time) * 1000)
        )

    def fire_task_failure(self, start_time, reason, action):
        events.task_failure.fire(
            task_name=self.locust.current_task,
            task_time=int((time() - start_time) * 1000),
            exception=reason,
            action=action
        )

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

    @property
    def context(self):
        """
        Reference to the :py:attr:`client <locust.core.Locust.client.context>` attribute of the root
        Locust instance.
        """
        return self.locust.client.context

    def _apply_task_context(self, task):
        func = task['callable']
        if hasattr(func, 'context_mods'):
            self.client.context.update(func.context_mods)
