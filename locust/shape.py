from __future__ import annotations

import time
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from .runners import Runner

if TYPE_CHECKING:
    from . import User


class LoadTestShapeMeta(ABCMeta):
    """
    Meta class for the main User class. It's used to allow User classes to specify task execution
    ratio using an {task:int} dict, or a [(task0,int), ..., (taskN,int)] list.
    """

    def __new__(mcs, classname, bases, class_dict):
        class_dict["abstract"] = class_dict.get("abstract", False)
        return super().__new__(mcs, classname, bases, class_dict)


class LoadTestShape(metaclass=LoadTestShapeMeta):
    """
    Base class for custom load shapes.
    """

    runner: Runner | None = None
    """Reference to the :class:`Runner <locust.runners.Runner>` instance"""

    abstract: ClassVar[bool] = True

    use_common_options: ClassVar[bool] = False

    def __init__(self):
        self.start_time = time.perf_counter()

    def reset_time(self):
        """
        Resets start time back to 0
        """
        self.start_time = time.perf_counter()

    def get_run_time(self):
        """
        Calculates run time in seconds of the load test
        """
        return time.perf_counter() - self.start_time

    def get_current_user_count(self):
        """
        Returns current actual number of users from the runner
        """
        return self.runner.user_count

    @abstractmethod
    def tick(self) -> tuple[int, float] | tuple[int, float, list[type[User]] | None] | None:
        """
        Returns a tuple with 2 elements to control the running load test:

            user_count -- Total user count
            spawn_rate -- Number of users to start/stop per second when changing number of users
            user_classes -- None or a List of userclasses to be spawned in it tick

        If `None` is returned then the running load test will be stopped.

        """
        ...
