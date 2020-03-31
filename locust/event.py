class EventHook(object):
    """
    Simple event class used to provide hooks for different types of events in Locust.

    Here's how to use the EventHook class::

        my_event = EventHook()
        def on_my_event(a, b, **kw):
            print("Event was fired with arguments: %s, %s" % (a, b))
        my_event.add_listener(on_my_event)
        my_event.fire(a="foo", b="bar")

    If reverse is True, then the handlers will run in the reverse order
    that they were inserted
    """

    def __init__(self):
        self._handlers = []
    
    def add_listener(self, handler):
        self._handlers.append(handler)
        return handler
    
    def remove_listener(self, handler):
        self._handlers.remove(handler)

    def fire(self, reverse=False, **kwargs):
        if reverse:
            handlers = reversed(self._handlers)
        else:
            handlers = self._handlers
        for handler in handlers:
            handler(**kwargs)


class Events:
    request_success = EventHook
    """
    *request_success* is fired when a request is completed successfully.
    
    Listeners should take the following arguments:
    
    * *request_type*: Request type method used
    * *name*: Path to the URL that was called (or override name if it was used in the call to the client)
    * *response_time*: Response time in milliseconds
    * *response_length*: Content-length of the response
    """
    
    request_failure = EventHook
    """
    *request_failure* is fired when a request fails
    
    Event is fired with the following arguments:
    
    * *request_type*: Request type method used
    * *name*: Path to the URL that was called (or override name if it was used in the call to the client)
    * *response_time*: Time in milliseconds until exception was thrown
    * *response_length*: Content-length of the response
    * *exception*: Exception instance that was thrown
    """
    
    locust_error = EventHook
    """
    *locust_error* is fired when an exception occurs inside the execution of a Locust class.
    
    Event is fired with the following arguments:
    
    * *locust_instance*: Locust class instance where the exception occurred
    * *exception*: Exception that was thrown
    * *tb*: Traceback object (from sys.exc_info()[2])
    """
    
    report_to_master = EventHook
    """
    *report_to_master* is used when Locust is running in --worker mode. It can be used to attach
    data to the dicts that are regularly sent to the master. It's fired regularly when a report
    is to be sent to the master server.
    
    Note that the keys "stats" and "errors" are used by Locust and shouldn't be overridden.
    
    Event is fired with the following arguments:
    
    * *client_id*: The client id of the running locust process.
    * *data*: Data dict that can be modified in order to attach data that should be sent to the master.
    """
    
    worker_report = EventHook
    """
    *worker_report* is used when Locust is running in --master mode and is fired when the master
    server receives a report from a Locust worker server.
    
    This event can be used to aggregate data from the locust worker servers.
    
    Event is fired with following arguments:
    
    * *client_id*: Client id of the reporting worker
    * *data*: Data dict with the data from the worker node
    """
    
    hatch_complete = EventHook
    """
    *hatch_complete* is fired when all locust users has been spawned.
    
    Event is fire with the following arguments:
    
    * *user_count*: Number of users that was hatched
    """
    
    quitting = EventHook
    """
    *quitting* is fired when the locust process is exiting
    """
    
    master_start_hatching = EventHook
    """
    *master_start_hatching* is fired when we initiate the hatching process on the master.
    
    This event is especially useful to detect when the 'start' button is clicked on the web ui.
    """
    
    master_stop_hatching = EventHook
    """
    *master_stop_hatching* is fired when terminate the hatching process on the master.
    
    This event is especially useful to detect when the 'stop' button is clicked on the web ui.
    """
    
    locust_start_hatching = EventHook
    """
    *locust_start_hatching* is fired when we initiate the hatching process on any locust worker.
    """
    
    locust_stop_hatching = EventHook
    """
    *locust_stop_hatching* is fired when terminate the hatching process on any locust worker.
    """
    
    init = EventHook
    """
    *init* is fired when Locust is started, once the Environment instance and locust runner instance 
    have been created. This hook can be used by end-users' code to run code that requires access to 
    the Envirionment. For example to register listeners to request_success, request_failure 
    or other events.
    
    Event is fired with following arguments:
    
    * *environment*: Environment instance
    """
    
    init_command_line_parser = EventHook
    """
    Event that can be used to add command line options to Locust
    
    Event is fired with the following arguments:
    * *parser*: ArgumentParser instance
    """
    
    def __init__(self):
        for name, value in vars(type(self)).items():
            if value == EventHook:
                setattr(self, name, value())
