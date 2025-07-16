from locust.user.task import TaskSetMeta, validate_task_name
from locust.user.users import TaskSet

import logging
import random
from collections.abc import Callable
from typing import Protocol, TypeVar, runtime_checkable

MarkovTaskT = TypeVar("MarkovTaskT", Callable[..., None], type[TaskSet])


@runtime_checkable
class TransitionsHolder(Protocol[MarkovTaskT]):
    transitions: dict[str, MarkovTaskT] | list[str]


def is_markov_task(task: MarkovTaskT):
    return isinstance(task, TransitionsHolder)


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


def get_markov_tasks(class_dict: dict) -> list:
    return [fn for fn in class_dict.values() if is_markov_task(fn)]


def validate_has_markov_tasks(tasks: list[TransitionsHolder], classname: str):
    if not tasks:
        raise Exception(
            f"No Markov tasks defined in class {classname}. Use the @transition(s) decorators to define some."
        )


def validate_transitions(tasks: list, class_dict: dict, classname: str):
    for task in tasks:
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


def validate_no_unreachable_tasks(tasks: list, class_dict: dict, classname: str):
    visited = set()

    def dfs(task_name):
        visited.add(task_name)
        for dest in class_dict.get(task_name).transitions.keys():
            if dest not in visited:
                dfs(dest)

    dfs(tasks[0].__name__)
    unreachable = set([task.__name__ for task in tasks]) - visited

    if len(unreachable) > 0:
        logging.warning(f"The following markov tasks are unreachable in class {classname}: {unreachable}")

    return tasks


def validate_no_tags(task, classname: str):
    if "locust_tag_set" in dir(task):
        raise Exception(
            "Tags are unsupported for MarkovTaskSet since they can make the markov chain invalid. "
            + f"Tags detected on {classname}.{task.__name__}: {task.locust_tag_set}"
        )


def validate_markov_chain(tasks: list, class_dict: dict, classname: str):
    validate_has_markov_tasks(tasks, classname)
    validate_transitions(tasks, class_dict, classname)
    validate_no_unreachable_tasks(tasks, class_dict, classname)
    for task in tasks:
        validate_task_name(task)
        validate_no_tags(task, classname)


class MarkovTaskSetMeta(TaskSetMeta):
    """
    Meta class for MarkovTaskSet. It's used to allow MarkovTaskSet classes to specify
    task execution using the @transition(s) decorator
    """

    def __new__(mcs, classname, bases, class_dict):
        if not class_dict.get("abstract"):
            tasks = get_markov_tasks(class_dict)
            validate_markov_chain(tasks, class_dict, classname)
            class_dict["current"] = tasks[0]
            for task in tasks:
                task.transitions = [name for name in task.transitions.keys() for _ in range(task.transitions[name])]

        return type.__new__(mcs, classname, bases, class_dict)


class MarkovTaskSet(TaskSet, metaclass=MarkovTaskSetMeta):
    """
    Class defining a probabilistic sequence of functions that a User will execute.
    The sequence is defined by a Markov Chain to describe a user's load.
    It holds a current state and a set of possible transitions for each state.
    Every transition as an associated weight that defines how likely it is to be taken.
    """

    current: Callable | TaskSet

    abstract: bool = True
    """If abstract is True, the class is meant to be subclassed, and the markov chain won't be validated"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_next_task(self):
        fn = self.current

        transitions = getattr(fn, "transitions")
        next = random.choice(transitions)
        self.current = getattr(self, next)

        return fn
