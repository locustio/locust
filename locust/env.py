from .event import Events


class Environment:
    events = None
    """
    Event hooks used by Locust internally, as well as to extend Locust's functionality
    See :ref:`events` for available events.
    """
    
    options = None
    """Parsed command line options"""
    
    host = None
    """Base URL of the target system"""
    
    reset_stats = False
    """Determines if stats should be reset once all simulated users have been spawned"""
    
    step_load = False
    """Determines if we're running in step load mode"""
    
    def  __init__(self, events=None, options=None, host=None, reset_stats=False, step_load=False):
        if events:
            self.events = events
        else:
            self.events = Events()
        
        self.host = host
        self.reset_stats = reset_stats
        self.step_load = step_load
        self.options = options
