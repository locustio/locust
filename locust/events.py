class EventHook(object):
    """
    Simple event class used to provide hooks for different types of events in Locust.

    Here's how to use the EventHook class::

        my_event = EventHook()
        def on_my_event(a, b, **kw):
            print "Event was fired with arguments: %s, %s" % (a, b)
        my_event += on_my_event
        my_event.fire(a="foo", b="bar")
    """

    def __init__(self):
        self._handlers = []

    def __iadd__(self, handler):
        self._handlers.append(handler)
        return self

    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    def fire(self, **kwargs):
        for handler in self._handlers:
            handler(**kwargs)

    def clear(self):
        del self._handlers[:]

request_success = EventHook()
"""
*request_success* is fired when a request is completed successfully.

Listeners should take the following arguments:

* *request_type*: Request type method used
* *name*: Path to the URL that was called (or override name if it was used in the call to the client)
* *response_time*: Response time in milliseconds
* *response_length*: Content-length of the response
"""

request_failure = EventHook()
"""
*request_failure* is fired when a request fails

Event is fired with the following arguments:

* *request_type*: Request type method used
* *name*: Path to the URL that was called (or override name if it was used in the call to the client)
* *response_time*: Time in milliseconds until exception was thrown
* *exception*: Exception instance that was thrown
"""

task_success = EventHook()
"""
*task_success* is fired when a task is completed successfully.

Listeners should take the following arguments:

* *task_name*: Task name
* *task_time*: Time was taken for task execution
"""

task_failure = EventHook()
"""
*task_failure* is fired when a task is interrupted by request failure during its execution.

Listeners should take the following arguments:

* *task_name*: Task name
* *task_time*: Time was taken for task execution
* *exception*: Exception instance that was thrown
* *action*: Exception instance that was thrown
"""

locust_error = EventHook()
"""
*locust_error* is fired when an exception occurs inside the execution of a Locust class.

Event is fired with the following arguments:

* *locust_instance*: Locust class instance where the exception occurred
* *exception*: Exception that was thrown
* *tb*: Traceback object (from sys.exc_info()[2])
"""

report_to_master = EventHook()
"""
*report_to_master* is used when Locust is running in --slave mode. It can be used to attach
data to the dicts that are regularly sent to the master. It's fired regularly when a report
is to be sent to the master server.

Note that the keys "stats" and "errors" are used by Locust and shouldn't be overridden.

Event is fired with the following arguments:

* *node_id*: The client id of the running locust process.
* *data*: Data dict that can be modified in order to attach data that should be sent to the master.
"""

node_report = EventHook()
"""
*node_report* is used when Locust is running in --master mode and is fired when the master
server receives a report from a Locust slave server.

This event can be used to aggregate data from the locust slave servers.

Event is fired with following arguments:

* *node_id*: Client id of the reporting locust slave
* *data*: Data dict with the data from the slave node
"""

hatch_complete = EventHook()
"""
*hatch_complete* is fired when all locust users has been spawned.

Event is fire with the following arguments:

* *user_count*: Number of users that was hatched
"""

quitting = EventHook()
"""
*quitting* is fired when the locust process in exiting
"""

master_start_hatching = EventHook()
"""
*master_start_hatching* is fired when we initiate the hatching process on the master.

This event is especially usefull to detect when the 'start' button is clicked on the web ui.
"""

master_stop_hatching = EventHook()
"""
*master_stop_hatching* is fired when terminate the hatching process on the master.

This event is especially usefull to detect when the 'stop' button is clicked on the web ui.
"""

locust_start_hatching = EventHook()
"""
*locust_start_hatching* is fired when we initiate the hatching process on any locust worker.
"""

locust_stop_hatching = EventHook()
"""
*locust_stop_hatching* is fired when terminate the hatching process on any locust worker.
"""

def clear_events_handlers():
    request_success.clear()
    request_failure.clear()
    locust_error.clear()
    report_to_master.clear()
    node_report.clear()
    hatch_complete.clear()
    quitting.clear()
    master_start_hatching.clear()
    master_stop_hatching.clear()
    locust_start_hatching.clear()
    locust_stop_hatching.clear()
    task_success.clear()
    task_failure.clear()
