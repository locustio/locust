import os

if os.getenv("LOCUST_PLAYWRIGHT", None):
    print("LOCUST_PLAYWRIGHT setting is no longer needed (because locust-plugins no longer installs trio)")
    print("Uninstall trio package and remove the setting.")
    try:
        # preserve backwards compatibility for now
        import trio
    except ModuleNotFoundError:
        # dont show a massive callstack if trio is not installed
        os._exit(1)

if not os.getenv("LOCUST_SKIP_MONKEY_PATCH", None):
    from gevent import monkey, queue

    monkey.patch_all()

    if not os.getenv("LOCUST_SKIP_URLLIB3_PATCH", None):
        import urllib3

        urllib3.connectionpool.ConnectionPool.QueueCls = queue.LifoQueue
        # https://github.com/locustio/locust/issues/2812

from ._version import version as __version__
from .contrib.fasthttp import FastHttpUser
from .debug import run_single_user
from .event import Events
from .shape import LoadTestShape
from .user import wait_time
from .user.sequential_taskset import SequentialTaskSet
from .user.task import TaskSet, tag, task
from .user.users import HttpUser, User
from .user.wait_time import between, constant, constant_pacing, constant_throughput

events = Events()

__all__ = (
    "SequentialTaskSet",
    "wait_time",
    "task",
    "tag",
    "TaskSet",
    "HttpUser",
    "FastHttpUser",
    "User",
    "between",
    "constant",
    "constant_pacing",
    "constant_throughput",
    "events",
    "LoadTestShape",
    "run_single_user",
)

# Used for raising a DeprecationWarning if old Locust/HttpLocust is used
from .util.deprecation import DeprecatedHttpLocustClass as HttpLocust
from .util.deprecation import DeprecatedLocustClass as Locust
