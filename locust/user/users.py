from locust.user.wait_time import constant
from typing import Any, Callable, Dict, List, TypeVar, Union
from typing_extensions import final
from gevent import GreenletExit, greenlet
from gevent.pool import Group
from locust.clients import HttpSession
from locust.exception import LocustError, StopUser
from locust.util import deprecation
from .task import (
    TaskSet,
    DefaultTaskSet,
    get_tasks_from_base_classes,
    LOCUST_STATE_RUNNING,
    LOCUST_STATE_WAITING,
    LOCUST_STATE_STOPPING,
)


class UserMeta(type):
    """
    Meta class for the main User class. It's used to allow User classes to specify task execution
    ratio using an {task:int} dict, or a [(task0,int), ..., (taskN,int)] list.
    """

    def __new__(mcs, classname, bases, class_dict):
        # gather any tasks that is declared on the class (or it's bases)
        tasks = get_tasks_from_base_classes(bases, class_dict)
        class_dict["tasks"] = tasks

        if not class_dict.get("abstract"):
            # Not a base class
            class_dict["abstract"] = False

        deprecation.check_for_deprecated_task_set_attribute(class_dict)

        return type.__new__(mcs, classname, bases, class_dict)


class User(object, metaclass=UserMeta):
    """
    Represents a "user" which is to be spawned and attack the system that is to be load tested.

    The behaviour of this user is defined by its tasks. Tasks can be declared either directly on the
    class by using the :py:func:`@task decorator <locust.task>` on methods, or by setting
    the :py:attr:`tasks attribute <locust.User.tasks>`.

    This class should usually be subclassed by a class that defines some kind of client. For
    example when load testing an HTTP system, you probably want to use the
    :py:class:`HttpUser <locust.HttpUser>` class.
    """

    host: str = None
    """Base hostname to swarm. i.e: http://127.0.0.1:1234"""

    min_wait = None
    """Deprecated: Use wait_time instead. Minimum waiting time between the execution of locust tasks"""

    max_wait = None
    """Deprecated: Use wait_time instead. Maximum waiting time between the execution of locust tasks"""

    wait_time = constant(0)
    """
    Method that returns the time (in seconds) between the execution of locust tasks.
    Can be overridden for individual TaskSets.

    Example::

        from locust import User, between
        class MyUser(User):
            wait_time = between(3, 25)
    """

    wait_function = None
    """
    .. warning::

        DEPRECATED: Use wait_time instead. Note that the new wait_time method should return seconds and not milliseconds.

    Method that returns the time between the execution of locust tasks in milliseconds
    """

    tasks: List[Union[TaskSet, Callable]] = []
    """
    Collection of python callables and/or TaskSet classes that the Locust user(s) will run.

    If tasks is a list, the task to be performed will be picked randomly.

    If tasks is a *(callable,int)* list of two-tuples, or a {callable:int} dict,
    the task to be performed will be picked randomly, but each task will be weighted
    according to its corresponding int value. So in the following case, *ThreadPage* will
    be fifteen times more likely to be picked than *write_post*::

        class ForumPage(TaskSet):
            tasks = {ThreadPage:15, write_post:1}
    """

    weight = 1
    """Probability of user class being chosen. The higher the weight, the greater the chance of it being chosen."""

    abstract = True
    """If abstract is True, the class is meant to be subclassed, and locust will not spawn users of this class during a test."""

    environment = None
    """A reference to the :py:class:`Environment <locust.env.Environment>` in which this user is running"""

    client = None
    _state = None
    _greenlet: greenlet.Greenlet = None
    _group: Group
    _taskset_instance = None

    def __init__(self, environment):
        super().__init__()
        self.environment = environment

    def on_start(self):
        """
        Called when a User starts running.
        """
        pass

    def on_stop(self):
        """
        Called when a User stops running (is killed)
        """
        pass

    @final
    def run(self):
        self._state = LOCUST_STATE_RUNNING
        self._taskset_instance = DefaultTaskSet(self)
        try:
            # run the TaskSet on_start method, if it has one
            self.on_start()

            self._taskset_instance.run()
        except (GreenletExit, StopUser):
            # run the on_stop method, if it has one
            self.on_stop()

    def wait(self):
        """
        Make the running user sleep for a duration defined by the User.wait_time
        function.

        The user can also be killed gracefully while it's sleeping, so calling this
        method within a task makes it possible for a user to be killed mid-task even if you've
        set a stop_timeout. If this behaviour is not desired, you should make the user wait using
        gevent.sleep() instead.
        """
        self._taskset_instance.wait()

    def start(self, group: Group):
        """
        Start a greenlet that runs this User instance.

        :param group: Group instance where the greenlet will be spawned.
        :type group: gevent.pool.Group
        :returns: The spawned greenlet.
        """

        def run_user(user):
            """
            Main function for User greenlet. It's important that this function takes the user
            instance as an argument, since we use greenlet_instance.args[0] to retrieve a reference to the
            User instance.
            """
            user.run()

        self._greenlet = group.spawn(run_user, self)
        self._group = group
        return self._greenlet

    def stop(self, force=False):
        """
        Stop the user greenlet.

        :param force: If False (the default) the stopping is done gracefully by setting the state to LOCUST_STATE_STOPPING
                      which will make the User instance stop once any currently running task is complete and on_stop
                      methods are called. If force is True the greenlet will be killed immediately.
        :returns: True if the greenlet was killed immediately, otherwise False
        """
        if force or self._state == LOCUST_STATE_WAITING:
            self._group.killone(self._greenlet)
            return True
        elif self._state == LOCUST_STATE_RUNNING:
            self._state = LOCUST_STATE_STOPPING
            return False

    @property
    def group(self):
        return self._group

    @property
    def greenlet(self):
        return self._greenlet

    def context(self) -> Dict:
        """
        Adds the returned value (a dict) to the context for :ref:`request event <request_context>`
        """
        return {}

    @classmethod
    def fullname(cls) -> str:
        """Fully qualified name of the user class, e.g. my_package.my_module.MyUserClass"""
        return ".".join(filter(lambda x: x != "<locals>", (cls.__module__ + "." + cls.__qualname__).split(".")))


class HttpUser(User):
    """
    Represents an HTTP "user" which is to be spawned and attack the system that is to be load tested.

    The behaviour of this user is defined by its tasks. Tasks can be declared either directly on the
    class by using the :py:func:`@task decorator <locust.task>` on methods, or by setting
    the :py:attr:`tasks attribute <locust.User.tasks>`.

    This class creates a *client* attribute on instantiation which is an HTTP client with support
    for keeping a user session between requests.
    """

    abstract = True
    """If abstract is True, the class is meant to be subclassed, and users will not choose this locust during a test"""

    client: HttpSession = None
    """
    Instance of HttpSession that is created upon instantiation of Locust.
    The client supports cookies, and therefore keeps the session between HTTP requests.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.host is None:
            raise LocustError(
                "You must specify the base host. Either in the host attribute in the User class, or on the command line using the --host option."
            )

        session = HttpSession(
            base_url=self.host,
            request_event=self.environment.events.request,
            user=self,
        )
        session.trust_env = False
        self.client = session
