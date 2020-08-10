from .event import Events
from .exception import RunnerAlreadyExistsError
from .stats import RequestStats
from .runners import LocalRunner, MasterRunner, WorkerRunner
from .web import WebUI
from .user.task import filter_tasks_by_tags


class Environment:
    events = None
    """
    Event hooks used by Locust internally, as well as to extend Locust's functionality
    See :ref:`events` for available events.
    """
    
    user_classes = []
    """User classes that the runner will run"""
    
    tags = None
    """If set, only tasks that are tagged by tags in this list will be executed"""

    exclude_tags = None
    """If set, only tasks that aren't tagged by tags in this list will be executed"""

    stats = None
    """Reference to RequestStats instance"""
    
    runner = None
    """Reference to the :class:`Runner <locust.runners.Runner>` instance"""
    
    web_ui = None
    """Reference to the WebUI instance"""
    
    host = None
    """Base URL of the target system"""
    
    reset_stats = False
    """Determines if stats should be reset once all simulated users have been spawned"""
    
    step_load = False
    """Determines if we're running in step load mode"""
    
    stop_timeout = None
    """
    If set, the runner will try to stop the running users gracefully and wait this many seconds
    before killing them hard.
    """
    
    catch_exceptions = True
    """
    If True exceptions that happen within running users will be caught (and reported in UI/console).
    If False, exceptions will be raised.
    """
    
    process_exit_code: int = None
    """
    If set it'll be the exit code of the Locust process
    """

    parsed_options = None
    """Optional reference to the parsed command line options (used to pre-populate fields in Web UI)"""
    
    def  __init__(
        self, *,
        user_classes=[],
        tags=None,
        exclude_tags=None,
        events=None, 
        host=None, 
        reset_stats=False, 
        step_load=False, 
        stop_timeout=None,
        catch_exceptions=True,
        parsed_options=None,
    ):
        if events:
            self.events = events
        else:
            self.events = Events()
        
        self.user_classes = user_classes
        self.tags = tags
        self.exclude_tags = exclude_tags
        self.stats = RequestStats()
        self.host = host
        self.reset_stats = reset_stats
        self.step_load = step_load
        self.stop_timeout = stop_timeout
        self.catch_exceptions = catch_exceptions
        self.parsed_options = parsed_options

        self._filter_tasks_by_tags()
    
    def _create_runner(self, runner_class, *args, **kwargs):
        if self.runner is not None:
            raise RunnerAlreadyExistsError("Environment.runner already exists (%s)" % self.runner)
        self.runner = runner_class(self, *args, **kwargs)
        return self.runner
    
    def create_local_runner(self):
        """
        Create a :class:`LocalRunner <locust.runners.LocalRunner>` instance for this Environment
        """
        return self._create_runner(LocalRunner)
        
    def create_master_runner(self, master_bind_host="*", master_bind_port=5557):
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
    
    def create_worker_runner(self, master_host, master_port):
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

    def create_web_ui(self, host="", port=8089, auth_credentials=None, tls_cert=None, tls_key=None):
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
        """
        self.web_ui = WebUI(self, host, port, auth_credentials=auth_credentials, tls_cert=tls_cert, tls_key=tls_key)
        return self.web_ui
    
    def _filter_tasks_by_tags(self):
        """
        Filter the tasks on all the user_classes recursively, according to the tags and
        exclude_tags attributes
        """
        if self.tags is not None:
            self.tags = set(self.tags)
        if self.exclude_tags is not None:
            self.exclude_tags = set(self.exclude_tags)

        for user_class in self.user_classes:
            filter_tasks_by_tags(user_class, self.tags, self.exclude_tags)
