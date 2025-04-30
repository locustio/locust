import random
from locust.user.task import TaskSetMeta
from locust.user.users import TaskSet

import logging
from collections.abc import Callable, Hashable
from typing import Protocol, TypeVar, runtime_checkable

StepFunT = TypeVar("StepFunT", Callable[..., None], type["Scenario"])


@runtime_checkable
class StepHolder(Protocol[StepFunT]):
    steps: list[StepFunT]


def transition(id: Hashable, weight: int = 1) -> Callable[[StepFunT], StepFunT]:
    def decorator_func(decorated):
        if not hasattr(decorated, "locust_step_transitions"):
            decorated.locust_step_transitions = {}

        decorated.locust_step_transitions[id] = weight
        return decorated

    return decorator_func


def transitions(weights: dict[Hashable, int] | list[tuple[Hashable, int]]) -> Callable[[StepFunT], StepFunT]:
    def decorator_func(decorated):
        decorated.locust_step_transitions = (
            weights if isinstance(weights, dict) else {id: weight for id, weight in weights}
        )

        return decorated

    return decorator_func


def step(id: Hashable, weight: int | None = None) -> Callable[[StepFunT], StepFunT]:
    """
    Used as a convenience decorator to be able to declare steps for a User or a Scenario
    inline in the class. Example::

        class ForumPage(Scenario):
            @step("read")
            def read_thread(self):
                pass

            @step("create")
            def create_thread(self):
                pass

            @step(Pages.THREAD)
            class ForumThread(Scenario):
                @step("author")
                def get_author(self):
                    pass

                @step("get created")
                def get_created(self):
                    pass
    """

    def decorator_func(func):
        if func.__name__ in ["on_stop", "on_start"]:
            logging.warning(
                "You have tagged your on_stop/start function with @step. This will make the method get called both as a step AND on stop/start."
            )  # this is usually not what the user intended
        if func.__name__ == "run":
            raise Exception(
                "User.run() is a method used internally by Locust, and you must not override it or register it as a step"
            )
        if not hasattr(func, "locust_step_transitions"):
            raise Exception(
                f"No transitions given for step {func.__name__} with id {id}"
                "Make sure your decorators are ordred properly:"
                "@step(Pages.HOME)"
                "@transition(...)"
                "def home(self): ..."
            )

        func.locust_step_weight = weight
        func.locust_step_id = id
        return func

    return decorator_func


# TODO: Optimize out and delete all calls
def random_choice(weights: dict):
    return random.choice([v for v in weights for _ in range(weights[v])])


class ScenarioMeta(TaskSetMeta):
    """
    Meta class for Scenario. It's used to allow Scenario classes to specify
    task execution using the @step and @transition(s) decorators
    """

    def __new__(mcs, classname, bases, class_dict):
        locust_steps = {fn.locust_step_id: fn for fn in class_dict.values() if hasattr(fn, "locust_step_id")}
        class_dict["locust_steps"] = locust_steps

        if not locust_steps:
            # raise Exception("No steps defined. Use the @step decorator to define steps")
            return type.__new__(mcs, classname, bases, class_dict)

        start_candidates = {id: fn.locust_step_weight for id, fn in locust_steps.items() if fn.locust_step_weight}
        class_dict["locust_current"] = (
            random_choice(start_candidates) if start_candidates else next(iter(locust_steps.keys()))
        )

        return type.__new__(mcs, classname, bases, class_dict)


class Scenario(TaskSet, metaclass=ScenarioMeta):
    """
    Class defining a scenario that a User will execute. A scenario is the implementation
    of a Markov Chain to describe a user's load. It has a current state and will
    change state according to some probabilities (weights).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_next_task(self):
        steps = getattr(self, "locust_steps")
        current = getattr(self, "locust_current")
        fn = steps[current]

        next = random_choice(getattr(fn, "locust_step_transitions"))
        self.locust_current = next

        return fn
