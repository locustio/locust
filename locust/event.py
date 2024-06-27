from __future__ import annotations

import logging
import time
import traceback
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from . import log
from .exception import InterruptTaskSet, RescheduleTask, RescheduleTaskImmediately, StopUser


class EventHook:
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
                # These exceptions could be thrown by, for example, a request handler,
                # in which case they are entirely appropriate and should not be caught
                raise
            except Exception:
                logging.error("Uncaught exception in event handler: \n%s", traceback.format_exc())
                log.unhandled_greenlet_exception = True

    @contextmanager
    def measure(
        self, request_type: str, name: str, response_length: int = 0, context=None
    ) -> Generator[dict[str, Any], None, None]:
        """Convenience method for firing the event with automatically calculated response time and automatically marking the request as failed if an exception is raised (this is really only useful for the *request* event)

        Example usage (in a task):

        .. code-block:: python

            with self.environment.events.request.measure("requestType", "requestName") as request_meta:
                # do the stuff you want to measure

        You can optionally add/overwrite entries in the request_meta dict and they will be passed to the request event.

        Experimental.
        """
        start_time = time.time()
        start_perf_counter = time.perf_counter()
        request_meta = {
            "request_type": request_type,
            "name": name,
            "response_length": response_length,
            "context": context or {},
            "exception": None,
            "start_time": start_time,
        }
        try:
            yield request_meta
        except Exception as e:
            request_meta["exception"] = e
        finally:
            request_meta["response_time"] = (time.perf_counter() - start_perf_counter) * 1000
            self.fire(**request_meta)


class DeprecatedEventHook(EventHook):
    def __init__(self, message):
        self.message = message
        super().__init__()

    def add_listener(self, handler):
        logging.warning(self.message)
        return super().add_listener(handler)


class Events:
    request: EventHook
    """
    Fired when a request in completed.

    Event arguments:

    :param request_type: Request type method used
    :param name: Path to the URL that was called (or override name if it was used in the call to the client)
    :param response_time: Time in milliseconds until exception was thrown
    :param response_length: Content-length of the response
    :param response: Response object (e.g. a :py:class:`requests.Response`)
    :param context: :ref:`User/request context <request_context>`
    :param exception: Exception instance that was thrown. None if request was successful.

    If you want to simplify a custom client, you can have Locust measure the time for you by using :meth:`measure() <locust.event.EventHook.measure>`
    """

    user_error: EventHook
    """
    Fired when an exception occurs inside the execution of a User class.

    Event arguments:

    :param user_instance: User class instance where the exception occurred
    :param exception: Exception that was thrown
    :param tb: Traceback object (from e.__traceback__)
    """

    report_to_master: EventHook
    """
    Used when Locust is running in --worker mode. It can be used to attach
    data to the dicts that are regularly sent to the master. It's fired regularly when a report
    is to be sent to the master server.

    Note that the keys "stats" and "errors" are used by Locust and shouldn't be overridden.

    Event arguments:

    :param client_id: The client id of the running locust process.
    :param data: Data dict that can be modified in order to attach data that should be sent to the master.
    """

    worker_report: EventHook
    """
    Used when Locust is running in --master mode and is fired when the master
    server receives a report from a Locust worker server.

    This event can be used to aggregate data from the locust worker servers.

    Event arguments:

    :param client_id: Client id of the reporting worker
    :param data: Data dict with the data from the worker node
    """

    worker_connect: EventHook
    """
    Fired on master when a new worker connects. Note that is fired immediately after the connection is established, so init event may not yet have finished on worker.

    :param client_id: Client id of the connected worker
    """

    spawning_complete: EventHook
    """
    Fired when all simulated users has been spawned. The event is fired on master first, and then distributed to workers.

    Event arguments:

    :param user_count: Number of users that were spawned (in total, not per-worker)
    """

    quitting: EventHook
    """
    Fired when the locust process is exiting.

    Event arguments:

    :param environment: Environment instance
    """

    quit: EventHook
    """
    Fired after quitting events, just before process is exited.

    Event arguments:

    :param exit_code: Exit code for process
    """

    init: EventHook
    """
    Fired when Locust is started, once the Environment instance and locust runner instance
    have been created. This hook can be used by end-users' code to run code that requires access to
    the Environment. For example to register listeners to other events.

    Event arguments:

    :param environment: Environment instance
    """

    init_command_line_parser: EventHook
    """
    Event that can be used to add command line options to Locust

    Event arguments:

    :param parser: ArgumentParser instance
    """

    test_start: EventHook
    """
    Fired on each node when a new load test is started. It's not fired again if the number of
    users change during a test.
    """

    test_stopping: EventHook
    """
    Fired on each node when a load test is about to stop - before stopping users.
    """

    test_stop: EventHook
    """
    Fired on each node when a load test is stopped.
    """

    reset_stats: EventHook
    """
    Fired when the Reset Stats button is clicked in the web UI.
    """

    cpu_warning: EventHook
    """
    Fired when the CPU usage exceeds runners.CPU_WARNING_THRESHOLD (90% by default)
    """

    heartbeat_sent: EventHook
    """
    Fired when a heartbeat is sent by master to a worker.

    Event arguments:

    :param client_id: worker client id
    :param timestamp: time in seconds since the epoch (float) when the event occured
    """

    heartbeat_received: EventHook
    """
    Fired when a heartbeat is received by a worker from master.

    Event arguments:

    :param client_id: worker client id
    :param timestamp: time in seconds since the epoch (float) when the event occured
    """

    usage_monitor: EventHook
    """
    Fired every runners.CPU_MONITOR_INTERVAL (5.0 seconds by default) with information about
    current CPU and memory usage.

    Event arguments:

    :param environment: locust environment
    :param cpu_usage: current CPU usage in percent
    :param memory_usage: current memory usage (RSS) in bytes
    """

    def __init__(self):
        # For backward compatibility use also values of class attributes
        for name, value in vars(type(self)).items():
            if value == "EventHook":
                setattr(self, name, EventHook())

        for name, value in self.__annotations__.items():
            if value == "EventHook":
                setattr(self, name, EventHook())
