from operator import methodcaller
from typing import (
    Callable,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    Optional,
)

from configargparse import Namespace

from .event import Events
from .exception import RunnerAlreadyExistsError
from .stats import RequestStats
from .runners import Runner, LocalRunner, MasterRunner, WorkerRunner
from .web import WebUI
from .user import User
from .user.task import TaskSet, filter_tasks_by_tags
from .shape import LoadTestShape


RunnerType = TypeVar("RunnerType", bound=Runner)


class Environment:
    def __init__(
        self,
        *,
        user_classes: Union[List[Type[User]], None] = None,
        shape_class: Union[LoadTestShape, None] = None,
        tags: Union[List[str], None] = None,
        locustfile: str = None,
        exclude_tags=None,
        events: Events = None,
        host: str = None,
        reset_stats=False,
        stop_timeout: Union[float, None] = None,
        catch_exceptions=True,
        parsed_options: Namespace = None,
    ):

        self.runner: Optional[Runner] = None
        """Reference to the :class:`Runner <locust.runners.Runner>` instance"""

        self.web_ui: Optional[WebUI] = None
        """Reference to the WebUI instance"""

        self.process_exit_code: Optional[int] = None
        """
        If set it'll be the exit code of the Locust process
        """

        if events:
            self.events = events
            """
            Event hooks used by Locust internally, as well as to extend Locust's functionality
            See :ref:`events` for available events.
            """
        else:
            self.events = Events()

        self.locustfile = locustfile
        """Filename (not path) of locustfile"""
        self.user_classes: List[Type[User]] = user_classes or []
        """User classes that the runner will run"""
        self.shape_class = shape_class
        """A shape class to control the shape of the load test"""
        self.tags = tags
        """If set, only tasks that are tagged by tags in this list will be executed. Leave this as None to use the one from parsed_options"""
        self.exclude_tags = exclude_tags
        """If set, only tasks that aren't tagged by tags in this list will be executed. Leave this as None to use the one from parsed_options"""
        self.stats = RequestStats()
        """Reference to RequestStats instance"""
        self.host = host
        """Base URL of the target system"""
        self.reset_stats = reset_stats
        """Determines if stats should be reset once all simulated users have been spawned"""
        self.stop_timeout = stop_timeout
        """
        If set, the runner will try to stop the running users gracefully and wait this many seconds
        before killing them hard.
        """
        self.catch_exceptions = catch_exceptions
        """
        If True exceptions that happen within running users will be caught (and reported in UI/console).
        If False, exceptions will be raised.
        """
        self.parsed_options = parsed_options
        """Reference to the parsed command line options (used to pre-populate fields in Web UI). May be None when using Locust as a library"""

        self._remove_user_classes_with_weight_zero()

        # Validate there's no class with the same name but in different modules
        if len({user_class.__name__ for user_class in self.user_classes}) != len(self.user_classes):
            raise ValueError(
                "The following user classes have the same class name: {}".format(
                    ", ".join(map(methodcaller("fullname"), self.user_classes))
                )
            )
        if self.shape_class is not None and not isinstance(self.shape_class, LoadTestShape):
            raise ValueError(
                "shape_class should be instance of LoadTestShape or subclass LoadTestShape, but got: %s"
                % self.shape_class
            )

    def _create_runner(
        self,
        runner_class: Type[RunnerType],
        *args,
        **kwargs,
    ) -> RunnerType:
        if self.runner is not None:
            raise RunnerAlreadyExistsError(f"Environment.runner already exists ({self.runner})")
        self.runner = runner_class(self, *args, **kwargs)

        # Attach the runner to the shape class so that the shape class can access user count state
        if self.shape_class:
            self.shape_class.runner = self.runner

        return self.runner

    def create_local_runner(self) -> LocalRunner:
        """
        Create a :class:`LocalRunner <locust.runners.LocalRunner>` instance for this Environment
        """
        return self._create_runner(LocalRunner)

    def create_master_runner(self, master_bind_host="*", master_bind_port=5557) -> MasterRunner:
        """
        Create a :class:`MasterRunner <locust.runners.MasterRunner>` instance for this Environment

        :param master_bind_host: Interface/host that the master should use for incoming worker connections.
                                 Defaults to "*" which means all interfaces.
        :param master_bind_port: Port that the master should listen for incoming worker connections on
        """
        return self._create_runner(
            MasterRunner,
            master_bind_host=master_bind_host,
            master_bind_port=master_bind_port,
        )

    def create_worker_runner(self, master_host, master_port) -> WorkerRunner:
        """
        Create a :class:`WorkerRunner <locust.runners.WorkerRunner>` instance for this Environment

        :param master_host: Host/IP of a running master node
        :param master_port: Port on master node to connect to
        """
        # Create a new RequestStats with use_response_times_cache set to False to save some memory
        # and CPU cycles, since the response_times_cache is not needed for Worker nodes
        self.stats = RequestStats(use_response_times_cache=False)
        return self._create_runner(
            WorkerRunner,
            master_host=master_host,
            master_port=master_port,
        )

    def create_web_ui(
        self,
        host="",
        port=8089,
        auth_credentials=None,
        tls_cert=None,
        tls_key=None,
        stats_csv_writer=None,
        delayed_start=False,
    ):
        """
        Creates a :class:`WebUI <locust.web.WebUI>` instance for this Environment and start running the web server

        :param host: Host/interface that the web server should accept connections to. Defaults to ""
                     which means all interfaces
        :param port: Port that the web server should listen to
        :param auth_credentials: If provided (in format "username:password") basic auth will be enabled
        :param tls_cert: An optional path (str) to a TLS cert. If this is provided the web UI will be
                         served over HTTPS
        :param tls_key: An optional path (str) to a TLS private key. If this is provided the web UI will be
                        served over HTTPS
        :param stats_csv_writer: `StatsCSV <stats_csv.StatsCSV>` instance.
        :param delayed_start: Whether or not to delay starting web UI until `start()` is called. Delaying web UI start
                              allows for adding Flask routes or Blueprints before accepting requests, avoiding errors.
        """
        self.web_ui = WebUI(
            self,
            host,
            port,
            auth_credentials=auth_credentials,
            tls_cert=tls_cert,
            tls_key=tls_key,
            stats_csv_writer=stats_csv_writer,
            delayed_start=delayed_start,
        )
        return self.web_ui

    def _filter_tasks_by_tags(self):
        """
        Filter the tasks on all the user_classes recursively, according to the tags and
        exclude_tags attributes
        """
        if getattr(self, "_tasks_filtered", False):
            return  # only filter once
        self._tasks_filtered = True

        if self.tags is not None:
            tags = set(self.tags)
        elif self.parsed_options and self.parsed_options.tags:
            tags = set(self.parsed_options.tags)
        else:
            tags = None

        if self.exclude_tags is not None:
            exclude_tags = set(self.exclude_tags)
        elif self.parsed_options and self.parsed_options.exclude_tags:
            exclude_tags = set(self.parsed_options.exclude_tags)
        else:
            exclude_tags = None

        for user_class in self.user_classes:
            filter_tasks_by_tags(user_class, tags, exclude_tags)

    def _remove_user_classes_with_weight_zero(self):
        """
        Remove user classes having a weight of zero.
        """
        if len(self.user_classes) == 0:
            # Preserve previous behaviour that allowed no user classes to be specified.
            return
        filtered_user_classes = [
            user_class for user_class in self.user_classes if user_class.weight > 0 or user_class.fixed_count > 0
        ]
        if len(filtered_user_classes) == 0:
            # TODO: Better exception than `ValueError`?
            raise ValueError("There are no users with weight > 0.")
        self.user_classes[:] = filtered_user_classes

    def assign_equal_weights(self):
        """
        Update the user classes such that each user runs their specified tasks with equal
        probability.
        """
        for u in self.user_classes:
            u.weight = 1
            user_tasks = []
            tasks_frontier = u.tasks
            while len(tasks_frontier) != 0:
                t = tasks_frontier.pop()
                if hasattr(t, "tasks") and t.tasks:
                    tasks_frontier.extend(t.tasks)
                elif isinstance(t, Callable):
                    if t not in user_tasks:
                        user_tasks.append(t)
                else:
                    raise ValueError("Unrecognized task type in user")
            u.tasks = user_tasks

    @property
    def user_classes_by_name(self) -> Dict[str, Type[User]]:
        return {u.__name__: u for u in self.user_classes}
