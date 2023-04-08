from datetime import datetime, timezone
import os
import inspect
import locust
from locust import User, argument_parser
from typing import Type, Optional
from locust.env import Environment
from locust.exception import CatchResponseError, RescheduleTask


def _print_t(s):
    """
    Print something with a tab instead of newline at the end
    """
    print(str(s), end="\t")


class PrintListener:
    """
    Print every response (useful when debugging a single locust)
    """

    def __init__(
        self,
        env: locust.env.Environment,
        include_length=False,
        include_time=False,
        include_context=False,
        include_payload=False,
    ):
        env.events.request.add_listener(self.on_request)

        self.include_length = "length\t" if include_length else ""
        self.include_time = "time                    \t" if include_time else ""
        self.include_context = "context\t" if include_context else ""
        self.include_payload = "payload\t" if include_payload else ""

        print(
            f"\n{self.include_time}type\t{'name'.ljust(50)}\tresp_ms\t{self.include_length}exception\t{self.include_context}\t{self.include_payload}"
        )

    def on_request(
        self,
        request_type,
        name,
        response_time,
        response_length,
        exception,
        context: dict,
        start_time=None,
        response=None,
        **_kwargs,
    ):
        if exception:
            if isinstance(exception, RescheduleTask):
                pass
            if isinstance(exception, CatchResponseError):
                e = str(exception)
            else:
                try:
                    e = repr(exception)
                except AttributeError:
                    e = f"{exception.__class__} (and it has no string representation)"
            errortext = e[:500].replace("\n", " ")
        else:
            errortext = ""

        if response_time is None:
            response_time = -1
        n = name.ljust(30) if name else ""

        if self.include_time:
            if start_time:
                _print_t(datetime.fromtimestamp(start_time, tz=timezone.utc))
            else:
                _print_t(datetime.now())

        _print_t(request_type)
        _print_t(n.ljust(50))
        _print_t(str(round(response_time)).ljust(7))

        if self.include_length:
            _print_t(response_length)

        _print_t(errortext.ljust(9))

        if self.include_context:
            _print_t(context or "")

        if self.include_payload:
            _print_t(response._request.payload)

        print()


_env: Optional[Environment] = None  # minimal Environment for debugging


def run_single_user(
    user_class: Type[User],
    include_length=False,
    include_time=False,
    include_context=False,
    include_payload=False,
    loglevel=None,
):
    """
    Runs a single User. Useful when you want to run a debugger.

    It creates in a new locust :py:attr:`Environment <locust.env.Environment>` and triggers any ``init`` or ``test_start`` :ref:`events <extending_locust>` as normal.

    It does **not** trigger ``test_stop`` or ``quit`` when you quit the debugger.

    It prints some info about every request to stdout, and you can get additional info using the `include_*` flags

    By default, it does not set up locusts logging system (because it could interfere with the printing of requests),
    but you can change that by passing a log level (e.g. *loglevel="INFO"*)
    """
    global _env

    if loglevel:
        locust.log.setup_logging(loglevel)

    if not _env:
        _env = locust.env.Environment(events=locust.events)
        # in case your test goes looking for the file name of your locustfile
        _env.parsed_options = argument_parser.parse_options()
        frame = inspect.stack()[1]
        _env.parsed_options.locustfile = os.path.basename(frame[0].f_code.co_filename)
        # log requests to stdout
        PrintListener(
            _env,
            include_length=include_length,
            include_time=include_time,
            include_context=include_context,
            include_payload=include_payload,
        )
        # fire various events (quit and test_stop will never get called, sorry about that)
        _env.events.init.fire(environment=_env, runner=None, web_ui=None)

    # do the things that the Runner usually does
    _env.user_classes = [user_class]
    _env._filter_tasks_by_tags()
    _env.events.test_start.fire(environment=_env)

    # create a single user
    user = user_class(_env)
    setattr(_env, "single_user_instance", user)  # if you happen to need access to this from the Environment instance
    user.run()
