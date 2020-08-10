import logging
import random
import sys
import traceback
from time import time

import gevent
from gevent import GreenletExit

from locust.exception import InterruptTaskSet, RescheduleTask, RescheduleTaskImmediately, \
     StopUser, MissingWaitTimeError


logger = logging.getLogger(__name__)

LOCUST_STATE_RUNNING, LOCUST_STATE_WAITING, LOCUST_STATE_STOPPING = ["running", "waiting", "stopping"]


def task(weight=1):
    """
    Used as a convenience decorator to be able to declare tasks for a User or a TaskSet
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


def tag(*tags):
    """
    Decorator for tagging tasks and TaskSets with the given tag name. You can then limit the test
    to only execute tasks that are tagged with any of the tags provided by the --tags command-line
    argument. Example::

        class ForumPage(TaskSet):
            @tag('thread')
            @task(100)
            def read_thread(self):
                pass

            @tag('thread')
            @tag('post')
            @task(7)
            def create_thread(self):
                pass

            @tag('post')
            @task(11)
            def comment(self):
                pass
    """

    def decorator_func(decorated):
        if hasattr(decorated, 'tasks'):
            decorated.tasks = list(map(tag(*tags), decorated.tasks))
        else:
            if 'locust_tag_set' not in decorated.__dict__:
                decorated.locust_tag_set = set()
            decorated.locust_tag_set |= set(tags)
        return decorated

    if len(tags) == 0 or callable(tags[0]):
        raise ValueError('No tag name was supplied')

    return decorator_func

def get_tasks_from_base_classes(bases, class_dict):
    """
    Function used by both TaskSetMeta and UserMeta for collecting all declared tasks
    on the TaskSet/User class and all its base classes
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

def filter_tasks_by_tags(task_holder, tags=None, exclude_tags=None, checked=None):
    """
    Function used by Environment to recursively remove any tasks/TaskSets from a TaskSet/User that
    shouldn't be executed according to the tag options
    """

    new_tasks = []
    if checked is None:
        checked = {}
    for task in task_holder.tasks:
        if task in checked:
            if checked[task]:
                new_tasks.append(task)
            continue

        passing = True
        if hasattr(task, 'tasks'):
            filter_tasks_by_tags(task, tags, exclude_tags, checked)
            passing = len(task.tasks) > 0
        else:
            if tags is not None:
                passing &= 'locust_tag_set' in dir(task) and len(task.locust_tag_set & tags) > 0
            if exclude_tags is not None:
                passing &= 'locust_tag_set' not in dir(task) or len(task.locust_tag_set & exclude_tags) == 0

        if passing:
            new_tasks.append(task)
        checked[task] = passing

    task_holder.tasks = new_tasks

class TaskSetMeta(type):
    """
    Meta class for the main User class. It's used to allow User classes to specify task execution
    ratio using an {task:int} dict, or a [(task0,int), ..., (taskN,int)] list.
    """
    
    def __new__(mcs, classname, bases, class_dict):
        class_dict["tasks"] = get_tasks_from_base_classes(bases, class_dict)
        return type.__new__(mcs, classname, bases, class_dict)


class TaskSet(object, metaclass=TaskSetMeta):
    """
    Class defining a set of tasks that a User will execute.
    
    When a TaskSet starts running, it will pick a task from the *tasks* attribute, 
    execute it, and then sleep for the number of seconds returned by its *wait_time*
    function. If no wait_time method has been declared on the TaskSet, it'll call the 
    wait_time function on the User by default. It will then schedule another task
    for execution and so on.
    
    TaskSets can be nested, which means that a TaskSet's *tasks* attribute can contain 
    another TaskSet. If the nested TaskSet is scheduled to be executed, it will be
    instantiated and called from the currently executing TaskSet. Execution in the
    currently running TaskSet will then be handed over to the nested TaskSet which will 
    continue to run until it throws an InterruptTaskSet exception, which is done when 
    :py:meth:`TaskSet.interrupt() <locust.TaskSet.interrupt>` is called. (execution 
    will then continue in the first TaskSet).
    """
    
    tasks = []
    """
    Collection of python callables and/or TaskSet classes that the User(s) will run.

    If tasks is a list, the task to be performed will be picked randomly.

    If tasks is a *(callable,int)* list of two-tuples, or a {callable:int} dict, 
    the task to be performed will be picked randomly, but each task will be weighted 
    according to its corresponding int value. So in the following case, *ThreadPage* will 
    be fifteen times more likely to be picked than *write_post*::

        class ForumPage(TaskSet):
            tasks = {ThreadPage:15, write_post:1}
    """
    
    min_wait = None
    """
    Deprecated: Use wait_time instead. 
    Minimum waiting time between the execution of user tasks. Can be used to override 
    the min_wait defined in the root User class, which will be used if not set on the 
    TaskSet.
    """
    
    max_wait = None
    """
    Deprecated: Use wait_time instead. 
    Maximum waiting time between the execution of user tasks. Can be used to override 
    the max_wait defined in the root User class, which will be used if not set on the 
    TaskSet.
    """
    
    wait_function = None
    """
    Deprecated: Use wait_time instead.
    Function used to calculate waiting time between the execution of user tasks in milliseconds. 
    Can be used to override the wait_function defined in the root User class, which will be used
    if not set on the TaskSet.
    """

    _user = None
    _parent = None

    def __init__(self, parent):
        self._task_queue = []
        self._time_start = time()
        
        if isinstance(parent, TaskSet):
            self._user = parent.user
        else:
            self._user = parent

        self._parent = parent
        
        # if this class doesn't have a min_wait, max_wait or wait_function defined, copy it from Locust
        if not self.min_wait:
            self.min_wait = self.user.min_wait
        if not self.max_wait:
            self.max_wait = self.user.max_wait
        if not self.wait_function:
            self.wait_function = self.user.wait_function



    @property
    def user(self):
        """:py:class:`User <locust.User>` instance that this TaskSet was created by"""
        return self._user

    @property
    def parent(self):
        """Parent TaskSet instance of this TaskSet (or :py:class:`User <locust.User>` if this is not a nested TaskSet)"""
        return self._parent

    def on_start(self):
        """
        Called when a User starts executing this TaskSet
        """
        pass
    
    def on_stop(self):
        """
        Called when a User stops executing this TaskSet. E.g. when TaskSet.interrupt() is called
        or when the User is killed
        """
        pass

    def run(self):
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
            except (StopUser, GreenletExit):
                self.on_stop()
                raise
            except Exception as e:
                self.user.environment.events.user_error.fire(user_instance=self, exception=e, tb=sys.exc_info()[2])
                if self.user.environment.catch_exceptions:
                    logger.error("%s\n%s", e, traceback.format_exc())
                    self.wait()
                else:
                    raise
    
    def execute_next_task(self):
        self.execute_task(self._task_queue.pop(0))
    
    def execute_task(self, task):
        # check if the function is a method bound to the current locust, and if so, don't pass self as first argument
        if hasattr(task, "__self__") and task.__self__ == self:
            # task is a bound method on self
            task()
        elif hasattr(task, "tasks") and issubclass(task, TaskSet):
            # task is another (nested) TaskSet class
            task(self).run()
        else:
            # task is a function
            task(self)
    
    def schedule_task(self, task_callable, first=False):
        """
        Add a task to the User's task execution queue.
        
        :param task_callable: User task to schedule.
        :param args: Arguments that will be passed to the task callable.
        :param kwargs: Dict of keyword arguments that will be passed to the task callable.
        :param first: Optional keyword argument. If True, the task will be put first in the queue.
        """
        if first:
            self._task_queue.insert(0, task_callable)
        else:
            self._task_queue.append(task_callable)
    
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
        if self.user.wait_time:
            return self.user.wait_time()
        elif self.min_wait is not None and self.max_wait is not None:
            return random.randint(self.min_wait, self.max_wait) / 1000.0
        else:
            raise MissingWaitTimeError("You must define a wait_time method on either the %s or %s class" % (
                type(self.user).__name__, 
                type(self).__name__,
            ))
    
    def wait(self):
        """
        Make the running user sleep for a duration defined by the Locust.wait_time
        function (or TaskSet.wait_time function if it's been defined).

        The user can also be killed gracefully while it's sleeping, so calling this
        method within a task makes it possible for a user to be killed mid-task, even if you've
        set a stop_timeout. If this behaviour is not desired you should make the user wait using
        gevent.sleep() instead.
        """
        self._check_stop_condition()
        self.user._state = LOCUST_STATE_WAITING
        self._sleep(self.wait_time())
        self._check_stop_condition()
        self.user._state = LOCUST_STATE_RUNNING

    def _sleep(self, seconds):
        gevent.sleep(seconds)
    
    def _check_stop_condition(self):
        if self.user._state == LOCUST_STATE_STOPPING:
            raise StopUser()
    
    def interrupt(self, reschedule=True):
        """
        Interrupt the TaskSet and hand over execution control back to the parent TaskSet.
        
        If *reschedule* is True (default), the parent User will immediately re-schedule,
        and execute, a new task.
        """
        raise InterruptTaskSet(reschedule)
    
    @property
    def client(self):
        """
        Shortcut to the client :py:attr:`client <locust.User.client>` attribute of this TaskSet's :py:class:`User <locust.User>`
        """
        return self.user.client


class DefaultTaskSet(TaskSet):
    """
    Default root TaskSet that executes tasks in User.tasks.
    It executes tasks declared directly on the Locust with the user instance as the task argument.
    """
    def get_next_task(self):
        if not self.user.tasks:
            raise Exception("No tasks defined. use the @task decorator or set the tasks property of the User")
        return random.choice(self.user.tasks)
    
    def execute_task(self, task):
        if hasattr(task, "tasks") and issubclass(task, TaskSet):
            # task is  (nested) TaskSet class
            task(self.user).run()
        else:
            # task is a function
            task(self.user)

