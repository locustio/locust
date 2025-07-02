from locust.user.task import TaskSetMeta
from locust.user.users import TaskSet

import logging
import random
from collections.abc import Callable
from typing import Protocol, TypeVar, runtime_checkable

MarkovTaskT = TypeVar("MarkovTaskT", Callable[..., None], type[TaskSet])


@runtime_checkable
class TransitionsHolder(Protocol[MarkovTaskT]):
    transitions: dict[str, MarkovTaskT]

# TODO: add @end decorator that termines a tasksets execution after the function is called


# TODO: This should be deferred to once the graph is completed:
#  - verify targets, warn if some functions are unreachable, etc.
def verify_function_name(decorated_func):
    if decorated_func.__name__ in ["on_stop", "on_start"]:
        logging.warning(
            "You have tagged your on_stop/start function with @transition. This will make the method get called both as a step AND on stop/start."
        )  # this is usually not what the user intended
    if decorated_func.__name__ == "run":
        raise Exception(
            "TaskSet.run() is a method used internally by Locust, and you must not override it or annotate it with transitions"
        )


def transition(func_name: str, weight: int = 1) -> Callable[[MarkovTaskT], MarkovTaskT]:
    def decorator_func(decorated):
        if not hasattr(decorated, "transitions"):
            decorated.transitions = {}

        decorated.transitions[func_name] = weight
        return decorated

    return decorator_func


def transitions(weights: dict[str, int] | list[tuple[str, int] | str]) -> Callable[[MarkovTaskT], MarkovTaskT]:
    def parse_list_item(item: tuple[str, int] | str) -> tuple[str, int]:
        return item if isinstance(item, tuple) else (item, 1)

    def decorator_func(decorated):
        if not hasattr(decorated, "transitions"):
            decorated.transitions = {}

        decorated.transitions.update(
            weights
            if isinstance(weights, dict)
            else {func_name: weight for func_name, weight in map(parse_list_item, weights)}
        )

        return decorated

    return decorator_func


# TODO: Optimize out and delete all calls
def random_choice(weights: dict):
    return random.choice([v for v in weights for _ in range(weights[v])])


def validate_markov_chain(class_dict: dict, classname: str):
    def is_markov_task(func):
        return hasattr(func, "transitions")

    markov_tasks = [fn for fn in class_dict.values() if is_markov_task(fn)]

    if not markov_tasks:
        raise Exception("No steps defined. Use the @step decorator to define steps")

    for task in markov_tasks:
        for dest in task.transitions.keys():
            dest_task = class_dict.get(dest)
            if not dest_task:
                raise Exception(
                    f"Transition to {dest} from {task.__name__} is invalid since no such element exists on class {classname}"
                )
            if not is_markov_task(dest_task):
                raise Exception(
                    f"{classname}.{dest} cannot be used as a target for a transition since it does not define any transitions of its own."
                    + f"Used as a transition from {task.__name__}."
                )

    visited = set()
    def dfs(task_name):
        visited.add(task_name)
        for dest in class_dict.get(task_name).transitions.keys():
            if dest not in visited:
                dfs(dest)

    dfs(markov_tasks[0].__name__)
    unreachable = set([task.__name__ for task in markov_tasks]) - visited

    if len(unreachable) > 0:
        # TODO: Warn instead of throw
        raise Exception(f"The following markov tasks are unreachable in class {classname}: {unreachable}")

    return markov_tasks


class MarkvosTaskSetMeta(TaskSetMeta):
    """
    Meta class for MarkovTaskSet. It's used to allow MarkovTaskSet classes to specify
    task execution using the @transition(s) decorator
    """

    def __new__(mcs, classname, bases, class_dict):
        if classname != "MarkovTaskSet" and not class_dict.get("abstract"):
            markov_tasks = validate_markov_chain(class_dict, classname)
            class_dict["current"] = markov_tasks[0]

        return type.__new__(mcs, classname, bases, class_dict)


class MarkovTaskSet(TaskSet, metaclass=MarkvosTaskSetMeta):
    """
    Class defining a probabilistic sequence of functions that a User will execute.
    The sequence is defined by Markov Chain to describe a user's load.
    It holds a current state and a set of possible transitions for each state.
    Every transition as an associated weight that defines how likely it is to be taken.
    """

    current: Callable | TaskSet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_next_task(self):
        fn = self.current

        transitions = getattr(fn, "transitions")
        next = random_choice(transitions)
        self.current = getattr(self, next)

        return fn
