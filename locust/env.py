from .event import Events


class Environment:
    events = None
    """
    Event hooks used by Locust internally, as well as to extend Locust's functionality
    See :ref:`events` for available events.
    """
    
    runner = None
    """Reference to the LocustRunner instance"""
    
    web_ui = None
    """Reference to the WebUI instance"""
    
    options = None
    """Parsed command line options"""
    
    host = None
    """Base URL of the target system"""
    
    reset_stats = False
    """Determines if stats should be reset once all simulated users have been spawned"""
    
    step_load = False
    """Determines if we're running in step load mode"""
    
    stop_timeout = None
    """
    If set, the runner will try to stop the runnning users gracefully and wait this many seconds 
    before killing them hard.
    """
    
    master_host = "127.0.0.1"
    """Hostname of master node that the worker should connect to"""
    
    master_port = 5557
    """Port of master node that the worker should connect to. Defaults to 5557."""
    
    master_bind_host = "*"
    """Hostname/interfaces that the master node should expect workers to connect to. Defaults to '*' which means all interfaces."""
    
    master_bind_port = 5557    
    """Port that the master node should listen to and expect workers to connect to. Defaults to 5557."""
    
    def  __init__(
        self, 
        events=None, 
        options=None, 
        host=None, 
        reset_stats=False, 
        step_load=False, 
        stop_timeout=None,
    ):
        if events:
            self.events = events
        else:
            self.events = Events()
        
        self.options = options
        self.host = host
        self.reset_stats = reset_stats
        self.step_load = step_load
        self.stop_timeout = stop_timeout
        
