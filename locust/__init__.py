# Apply Gevent monkey patching of stdlib
from gevent import monkey as _monkey
_monkey.patch_all()


from .user.sequential_taskset import SequentialTaskSet
from .user import wait_time
from .user.task import task, TaskSet
from .user.users import HttpUser, User
from .user.wait_time import between, constant, constant_pacing

from .event import Events as _Events
events = _Events()

__version__ = "1.0b2"
