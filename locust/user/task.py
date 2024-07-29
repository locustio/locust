from __future__ import annotations

from locust.exception import (
    InterruptTaskSet,
    LocustError,
    MissingWaitTimeError,
    RescheduleTask,
    RescheduleTaskImmediately,
    StopUser,
)

import logging
import random
import traceback
from abc import ABC, ABCMeta, abstractmethod
from collections import deque
from itertools import accumulate, cycle
from time import time
from typing import (
    TYPE_CHECKING,
    Callable,
    Protocol,
    TypeVar,
    final,
    overload,
    runtime_checkable,
)

import gevent
from gevent import GreenletExit

if TYPE_CHECKING:
    from locust import User


logger = logging.getLogger(__name__)
TaskT = TypeVar("TaskT", Callable[..., None], type["TaskSet"])

LOCUST_STATE_RUNNING, LOCUST_STATE_WAITING, LOCUST_STATE_STOPPING = ["running", "waiting", "stopping"]


@runtime_checkable
class TaskHolder(Protocol[TaskT]):
    tasks: list[TaskT]


@overload
def task(weight: TaskT) -> TaskT: ...


@overload
def task(weight: int | float) -> Callable[[TaskT], TaskT]: ...


def task(weight: TaskT | int | float = 1) -> TaskT | Callable[[TaskT], TaskT]:
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

            @task(25)
            class ForumThread(TaskSet):
                @task
                def get_author(self):
                    pass

                @task
                def get_created(self):
                    pass
    """

    def decorator_func(func):
        if func.__name__ in ["on_stop", "on_start"]:
            logging.warning(
                "You have tagged your on_stop/start function with @task. This will make the method get called both as a task AND on stop/start."
            )  # this is usually not what the user intended
        if func.__name__ == "run":
            raise Exception(
                "User.run() is a method used internally by Locust, and you must not override it or register it as a task"
            )
        func.locust_task_weight = weight
        return func

    """
    Check if task was used without parentheses (not called), like this::

        @task
        def my_task(self)
            pass
    """
    if callable(weight):
        func = weight
        weight = 1
        return decorator_func(func)
    else:
        return decorator_func


def tag(*tags: str) -> Callable[[TaskT], TaskT]:
    """
    Decorator for tagging tasks and TaskSets with the given tag name. You can
    then limit the test to only execute tasks that are tagged with any of the
    tags provided by the :code:`--tags` command-line argument. Example::

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
        if hasattr(decorated, "tasks"):
            decorated.tasks = list(map(tag(*tags), decorated.tasks))
        else:
            if "locust_tag_set" not in decorated.__dict__:
                decorated.locust_tag_set = set()
            decorated.locust_tag_set |= set(tags)
        return decorated

    if len(tags) == 0 or callable(tags[0]):
        raise ValueError("No tag name was supplied")

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

    for key, value in class_dict.items():
        if key == "tasks":
            # we want to insert tasks from the tasks attribute at the point of it's declaration
            # compared to methods declared with @task
            tasks = value
            if not (isinstance(tasks, dict) or isinstance(tasks, list)):
                raise LocustError("'tasks' attribute must be list or dict")
            if isinstance(tasks, dict):
                tasks = tasks.items()
            for task in tasks:
                task, count = task if isinstance(task, tuple) else task, 1
                task.locust_task_weight = count
                new_tasks.append(task)

        if "locust_task_weight" in dir(value):
            # method decorated with @task
            new_tasks.append(value)

    return new_tasks


def filter_tasks_by_tags(
    task_holder: type[TaskHolder],
    tags: set[str] | None = None,
    exclude_tags: set[str] | None = None,
):
    """
    Function used by Environment to recursively remove any tasks/TaskSets from a TaskSet/User that
    shouldn't be executed according to the tag options
    """

    new_tasks = []
    for task in task_holder.tasks:
        passing = True
        if hasattr(task, "tasks"):
            filter_tasks_by_tags(task, tags, exclude_tags)
            passing = len(task.tasks) > 0
        else:
            if tags is not None:
                passing &= "locust_tag_set" in dir(task) and len(task.locust_tag_set & tags) > 0
            if exclude_tags is not None:
                passing &= "locust_tag_set" not in dir(task) or len(task.locust_tag_set & exclude_tags) == 0

        if passing:
            new_tasks.append(task)

    task_holder.tasks = new_tasks
    if not new_tasks:
        logging.warning(f"{task_holder.__name__} had no tasks left after filtering, instantiating it will fail!")


class TaskSetMeta(ABCMeta):
    """
    Meta class for the main User class. It's used to allow User classes to specify task execution
    ratio using an {task:int} dict, or a [(task0,int), ..., (taskN,int)] list.
    """

    def __new__(mcs, classname, bases, class_dict):
        class_dict["tasks"] = get_tasks_from_base_classes(bases, class_dict)
        return super().__new__(mcs, classname, bases, class_dict)


class AbstractTaskSet(ABC, metaclass=TaskSetMeta):
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

    tasks: list[TaskSet | Callable] = []
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

    min_wait: float | None = None
    """
    Deprecated: Use wait_time instead.
    Minimum waiting time between the execution of user tasks. Can be used to override
    the min_wait defined in the root User class, which will be used if not set on the
    TaskSet.
    """

    max_wait: float | None = None
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

    _user: User
    _parent: User

    def __init__(self, parent: User) -> None:
        self._task_queue: deque = deque()
        self._time_start = time()

        if isinstance(parent, AbstractTaskSet):
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
        self._cp_last_run = time()  # used by constant_pacing wait_time

    @property
    def user(self) -> User:
        """:py:class:`User <locust.User>` instance that this TaskSet was created by"""
        return self._user

    @property
    def parent(self):
        """Parent TaskSet instance of this TaskSet (or :py:class:`User <locust.User>` if this is not a nested TaskSet)"""
        return self._parent

    def on_start(self) -> None:
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

    @abstractmethod
    def _setup_tasks(self):
        pass

    @final
    def run(self):
        self._setup_tasks()
        try:
            self.on_start()
        except InterruptTaskSet as e:
            if e.reschedule:
                raise RescheduleTaskImmediately(e.reschedule).with_traceback(e.__traceback__)
            else:
                raise RescheduleTask(e.reschedule).with_traceback(e.__traceback__)

        while True:
            try:
                if isinstance(self, DefaultTaskSet):
                    if not self.user.tasks:
                        extra_message = (
                            ", but you have set a 'task' attribute on your class - maybe you meant to set 'tasks'?"
                            if getattr(self.user, "task", None)
                            else "."
                        )
                        raise LocustError(
                            f"No tasks defined on {self.user.__class__.__name__}{extra_message} Use the @task decorator or set the 'tasks' attribute of the User (or mark it as abstract = True if you only intend to subclass it)"
                        )
                else:
                    if not self.tasks:
                        extra_message = (
                            ", but you have set a 'task' attribute - maybe you meant to set 'tasks'?"
                            if getattr(self, "task", None)
                            else "."
                        )
                        raise LocustError(
                            f"No tasks defined on {self.__class__.__name__}{extra_message} use the @task decorator or set the 'tasks' attribute."
                        )

                if not self._task_queue:
                    self.schedule_task(self.get_next_task())

                try:
                    if self.user._state == LOCUST_STATE_STOPPING:
                        raise StopUser()
                    self.execute_next_task()
                except RescheduleTaskImmediately:
                    pass
                except RescheduleTask:
                    self.wait()
                else:
                    self.wait()
            except InterruptTaskSet as e:
                try:
                    self.on_stop()
                except (StopUser, GreenletExit):
                    raise
                except Exception:
                    logging.error("Uncaught exception in on_stop: \n%s", traceback.format_exc())
                if e.reschedule:
                    raise RescheduleTaskImmediately(e.reschedule) from e
                else:
                    raise RescheduleTask(e.reschedule) from e
            except (StopUser, GreenletExit):
                try:
                    self.on_stop()
                except Exception:
                    logging.error("Uncaught exception in on_stop: \n%s", traceback.format_exc())
                raise
            except Exception as e:
                self.user.environment.events.user_error.fire(user_instance=self, exception=e, tb=e.__traceback__)
                if self.user.environment.catch_exceptions:
                    logger.error("%s\n%s", e, traceback.format_exc())
                    self.wait()
                else:
                    raise

    def execute_next_task(self):
        self.execute_task(self._task_queue.popleft())

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
        :param first: Optional keyword argument. If True, the task will be put first in the queue.
        """
        if first:
            self._task_queue.appendleft(task_callable)
        else:
            self._task_queue.append(task_callable)

    @abstractmethod
    def get_next_task(self):
        pass

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
            raise MissingWaitTimeError(
                "You must define a wait_time method on either the {type(self.user).__name__} or {type(self).__name__} class"
            )

    def wait(self):
        """
        Make the running user sleep for a duration defined by the Locust.wait_time
        function (or TaskSet.wait_time function if it's been defined).

        The user can also be killed gracefully while it's sleeping, so calling this
        method within a task makes it possible for a user to be killed mid-task, even if you've
        set a stop_timeout. If this behaviour is not desired you should make the user wait using
        gevent.sleep() instead.
        """
        if self.user._state == LOCUST_STATE_STOPPING:
            raise StopUser()
        self.user._state = LOCUST_STATE_WAITING
        self._sleep(self.wait_time())
        if self.user._state == LOCUST_STATE_STOPPING:
            raise StopUser()
        self.user._state = LOCUST_STATE_RUNNING

    def _sleep(self, seconds):
        gevent.sleep(seconds)

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


class TaskSet(AbstractTaskSet):
    def _setup_tasks(self):
        self._task_weights = list(accumulate(map(lambda x: x.locust_task_weight, self.tasks)))

    def get_next_task(self):
        return random.choices(self.tasks, cum_weights=self._task_weights)[0]


class SequentialTaskSet(TaskSet):
    """
    Class defining a sequence of tasks that a User will execute.

    Works like TaskSet, but The order of declaration decides the order of execution.
    Tasks can either be specified by setting the *tasks* attribute to a list of tasks, or by declaring tasks
    as methods using the @task decorator. Weight determines the repetition of the task.

    It's possible to combine the *tasks* attribute, with some tasks declared using
    the @task decorator. The order of declaration is respected also in that case.
    """

    def _setup_tasks(self):
        task_cycle = []
        for t in self.tasks:
            for _ in range(t.locust_task_weight):
                task_cycle.append(t)
        self._task_cycle = cycle(task_cycle)

    def get_next_task(self):
        return next(self._task_cycle)


class DefaultTaskSet(AbstractTaskSet):
    """
    Default root TaskSet that executes tasks in User.tasks.
    It executes tasks declared directly on the Locust with the user instance as the task argument.
    """

    def _setup_tasks(self):
        self._task_weights = list(accumulate(map(lambda x: x.locust_task_weight, self.user.tasks)))

    def get_next_task(self):
        return random.choices(self.user.tasks, cum_weights=self._task_weights)[0]

    def execute_task(self, task):
        if hasattr(task, "tasks") and issubclass(task, TaskSet):
            # task is  (nested) TaskSet class
            task(self.user).run()
        else:
            # task is a function
            task(self.user)
