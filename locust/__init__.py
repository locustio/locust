from .core import WebLocust, Locust, TaskSet, task, mod_context
from .exception import InterruptTaskSet, ResponseError, RescheduleTaskImmediately
from .config import configure, locust_config, register_config

__version__ = "0.8dr3"
