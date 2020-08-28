import logging
from . import log
import traceback
from .exception import StopUser, RescheduleTask, RescheduleTaskImmediately, InterruptTaskSet


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

    def fire(self, *, reverse=False, **kwargs):
        if reverse:
            handlers = reversed(self._handlers)
        else:
            handlers = self._handlers
        for handler in handlers:
            try:
                handler(**kwargs)
            except (StopUser, RescheduleTask, RescheduleTaskImmediately, InterruptTaskSet):
                # These exceptions could be thrown by, for example, a request_failure handler,
                # in which case they are entirely appropriate and should not be caught
                raise
            except Exception:
                logging.error("Uncaught exception in event handler: \n%s", traceback.format_exc())
                log.unhandled_greenlet_exception = True


class Events:
    request_success = EventHook
    """
    Fired when a request is completed successfully. This event is typically used to report requests
    when writing custom clients for locust.

    Event arguments:

    :param request_type: Request type method used
    :param name: Path to the URL that was called (or override name if it was used in the call to the client)
    :param response_time: Response time in milliseconds
    :param response_length: Content-length of the response
    """

    request_failure = EventHook
    """
    Fired when a request fails. This event is typically used to report failed requests when writing
    custom clients for locust.

    Event arguments:

    :param request_type: Request type method used
    :param name: Path to the URL that was called (or override name if it was used in the call to the client)
    :param response_time: Time in milliseconds until exception was thrown
    :param response_length: Content-length of the response
    :param exception: Exception instance that was thrown
    """

    user_error = EventHook
    """
    Fired when an exception occurs inside the execution of a User class.

    Event arguments:

    :param user_instance: User class instance where the exception occurred
    :param exception: Exception that was thrown
    :param tb: Traceback object (from sys.exc_info()[2])
    """

    report_to_master = EventHook
    """
    Used when Locust is running in --worker mode. It can be used to attach
    data to the dicts that are regularly sent to the master. It's fired regularly when a report
    is to be sent to the master server.

    Note that the keys "stats" and "errors" are used by Locust and shouldn't be overridden.

    Event arguments:

    :param client_id: The client id of the running locust process.
    :param data: Data dict that can be modified in order to attach data that should be sent to the master.
    """

    worker_report = EventHook
    """
    Used when Locust is running in --master mode and is fired when the master
    server receives a report from a Locust worker server.

    This event can be used to aggregate data from the locust worker servers.

    Event arguments:

    :param client_id: Client id of the reporting worker
    :param data: Data dict with the data from the worker node
    """

    spawning_complete = EventHook
    """
    Fired when all simulated users has been spawned.

    Event arguments:

    :param user_count: Number of users that were spawned
    """

    quitting = EventHook
    """
    Fired when the locust process is exiting

    Event arguments:

    :param environment: Environment instance
    """

    init = EventHook
    """
    Fired when Locust is started, once the Environment instance and locust runner instance
    have been created. This hook can be used by end-users' code to run code that requires access to
    the Environment. For example to register listeners to request_success, request_failure
    or other events.

    Event arguments:

    :param environment: Environment instance
    """

    init_command_line_parser = EventHook
    """
    Event that can be used to add command line options to Locust

    Event arguments:

    :param parser: ArgumentParser instance
    """

    test_start = EventHook
    """
    Fired when a new load test is started. It's not fired again if the number of
    users change during a test. When running locust distributed the event is only fired
    on the master node and not on each worker node.
    """

    test_stop = EventHook
    """
    Fired when a load test is stopped. When running locust distributed the event
    is only fired on the master node and not on each worker node.
    """

    def __init__(self):
        for name, value in vars(type(self)).items():
            if value == EventHook:
                setattr(self, name, value())
