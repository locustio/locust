from locust.exception import LocustError
from locust.user.task import TaskSetMeta
from locust.user.users import TaskSet

import logging
import random
from collections.abc import Callable

MarkovTaskT = Callable[..., None]


class NoMarkovTasksError(LocustError):
    """Raised when a MarkovTaskSet class doesn't define any Markov tasks."""

    pass


class InvalidTransitionError(LocustError):
    """Raised when a transition in a MarkovTaskSet points to a non-existent task."""

    pass


class NonMarkovTaskTransitionError(LocustError):
    """Raised when a transition in a MarkovTaskSet points to a task that doesn't define transitions."""

    pass


class MarkovTaskTagError(LocustError):
    """Raised when tags are used with Markov tasks, which is unsupported."""

    pass


def is_markov_task(task: MarkovTaskT):
    """
    Determines if a task is a Markov task by checking if it has transitions defined.

    :param task: The task to check
    :return: True if the task is a Markov task, False otherwise
    """
    return "transitions" in dir(task)


def transition(func_name: str, weight: int = 1) -> Callable[[MarkovTaskT], MarkovTaskT]:
    """
    Decorator for adding a single transition to a Markov task.

    This decorator allows you to define a transition from one task to another in a MarkovTaskSet,
    with an associated weight that determines the probability of taking this transition.

    :param func_name: The name of the target task function
    :param weight: The weight of this transition (default: 1)
    :return: The decorated function with the transition added

    Example::

        class UserBehavior(MarkovTaskSet):
            @transition('browse_products')
            def index(self):
                self.client.get("/")

            @transition('index', weight=3)
            @transition('product_page', weight=1)
            def browse_products(self):
                self.client.get("/products/")
    """

    def decorator_func(decorated):
        if not hasattr(decorated, "transitions"):
            decorated.transitions = {}

        decorated.transitions[func_name] = weight
        return decorated

    return decorator_func


def transitions(weights: dict[str, int] | list[tuple[str, int] | str]) -> Callable[[MarkovTaskT], MarkovTaskT]:
    """
    Decorator for adding multiple transitions to a Markov task at once.

    This decorator allows you to define multiple transitions from one task to others in a MarkovTaskSet,
    with associated weights that determine the probability of taking each transition.

    :param weights: Either a dictionary mapping function names to weights, or a list of function names
                   (with default weight 1) or (function_name, weight) tuples
    :return: The decorated function with the transitions added

    Example::

        class UserBehavior(MarkovTaskSet):
            @transitions({'checkout': 1, 'browse_products': 3, 'index': 2})
            def view_cart(self):
                self.client.get("/cart/")

            @transitions([
                ('index', 2),      # with weight 2
                'browse_products'  # with default weight 1
            ])
            def checkout(self):
                self.client.get("/checkout/")
    """

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
    """
    Extracts all Markov tasks from a class dictionary.

    This function is used internally by MarkovTaskSetMeta to find all methods
    that have been decorated with @transition or @transitions.

    :param class_dict: Dictionary containing class attributes and methods
    :return: List of functions that are Markov tasks
    """
    return [fn for fn in class_dict.values() if is_markov_task(fn)]


def to_weighted_list(transitions: dict):
    return [name for name in transitions.keys() for _ in range(transitions[name])]


def validate_has_markov_tasks(tasks: list, classname: str):
    """
    Validates that a MarkovTaskSet has at least one Markov task.

    This function is used internally during MarkovTaskSet validation to ensure
    that the class has at least one method decorated with @transition or @transitions.

    :param tasks: List of tasks to validate
    :param classname: Name of the class being validated (for error messages)
    :raises NoMarkovTasksError: If no Markov tasks are found
    """
    if not tasks:
        raise NoMarkovTasksError(
            f"No Markov tasks defined in class {classname}. Use the @transition(s) decorators to define some."
        )


def validate_transitions(tasks: list, class_dict: dict, classname: str):
    """
    Validates that all transitions in Markov tasks point to existing Markov tasks.

    This function checks two conditions for each transition:
    1. The target task exists in the class
    2. The target task is also a Markov task (has transitions defined)

    :param tasks: List of Markov tasks to validate
    :param class_dict: Dictionary containing class attributes and methods
    :param classname: Name of the class being validated (for error messages)
    :raises InvalidTransitionError: If a transition points to a non-existent task
    :raises NonMarkovTaskTransitionError: If a transition points to a task that isn't a Markov task
    """
    for task in tasks:
        for dest in task.transitions.keys():
            dest_task = class_dict.get(dest)
            if not dest_task:
                raise InvalidTransitionError(
                    f"Transition to {dest} from {task.__name__} is invalid since no such element exists on class {classname}"
                )
            if not is_markov_task(dest_task):
                raise NonMarkovTaskTransitionError(
                    f"{classname}.{dest} cannot be used as a target for a transition since it does not define any transitions of its own."
                    + f"Used as a transition from {task.__name__}."
                )


def validate_no_unreachable_tasks(tasks: list, class_dict: dict, classname: str):
    """
    Checks for and warns about unreachable Markov tasks in a MarkovTaskSet.

    This function uses depth-first search (DFS) starting from the first task to identify
    all reachable tasks. It then warns about any tasks that cannot be reached from the
    starting task through the defined transitions.

    :param tasks: List of Markov tasks to validate
    :param class_dict: Dictionary containing class attributes and methods
    :param classname: Name of the class being validated (for warning messages)
    :return: The original list of tasks
    """
    visited = set()

    def dfs(task_name):
        visited.add(task_name)
        # Convert to a weighted list first to handle bad weights
        for dest in set(to_weighted_list(class_dict.get(task_name).transitions)):
            if dest not in visited:
                dfs(dest)

    dfs(tasks[0].__name__)
    unreachable = set([task.__name__ for task in tasks]) - visited

    if len(unreachable) > 0:
        logging.warning(f"The following markov tasks are unreachable in class {classname}: {unreachable}")

    return tasks


def validate_no_tags(task, classname: str):
    """
    Validates that Markov tasks don't have tags, which are unsupported.

    Tags are not supported for MarkovTaskSet because they can make the Markov chain invalid
    by potentially filtering out tasks that are part of the chain.

    :param task: The task to validate
    :param classname: Name of the class being validated (for error messages)
    :raises MarkovTaskTagError: If the task has tags
    """
    if "locust_tag_set" in dir(task):
        raise MarkovTaskTagError(
            "Tags are unsupported for MarkovTaskSet since they can make the markov chain invalid. "
            + f"Tags detected on {classname}.{task.__name__}: {task.locust_tag_set}"
        )


def validate_task_name(decorated_func):
    """
    Validates that certain method names aren't used as Markov tasks.

    This function checks for special method names that shouldn't be used as Markov tasks:
    - "on_stop" and "on_start": Using these as Markov tasks will cause them to be called
      both as tasks AND on stop/start, which is usually not what the user intended.
    - "run": This method is used internally by Locust and must not be overridden or
      annotated with transitions.

    :param decorated_func: The function to validate
    :raises Exception: If the function name is "run"
    """
    if decorated_func.__name__ in ["on_stop", "on_start"]:
        logging.warning(
            "You have tagged your on_stop/start function with @transition. This will make the method get called both as a step AND on stop/start."
        )  # this is usually not what the user intended
    if decorated_func.__name__ == "run":
        raise Exception(
            "TaskSet.run() is a method used internally by Locust, and you must not override it or annotate it with transitions"
        )


def validate_markov_chain(tasks: list, class_dict: dict, classname: str):
    """
    Runs all validation functions on a Markov chain.

    :param tasks: List of Markov tasks to validate
    :param class_dict: Dictionary containing class attributes and methods
    :param classname: Name of the class being validated (for error/warning messages)
    :raises: Various exceptions if validation fails
    """
    validate_has_markov_tasks(tasks, classname)
    validate_transitions(tasks, class_dict, classname)
    validate_no_unreachable_tasks(tasks, class_dict, classname)
    for task in tasks:
        validate_task_name(task)
        validate_no_tags(task, classname)


class MarkovTaskSetMeta(TaskSetMeta):
    """
    Meta class for MarkovTaskSet. It's used to allow MarkovTaskSet classes to specify
    task execution using the @transition(s) decorators
    """

    def __new__(mcs, classname, bases, class_dict):
        if not class_dict.get("abstract"):
            class_dict["abstract"] = False

            tasks = get_markov_tasks(class_dict)
            validate_markov_chain(tasks, class_dict, classname)
            class_dict["current"] = tasks[0]
            for task in tasks:
                task.transitions = to_weighted_list(task.transitions)

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
        """
        Gets the next task to execute based on the current state and transitions.

        :return: The current task to execute
        """
        fn = self.current

        transitions = getattr(fn, "transitions")
        next = random.choice(transitions)
        self.current = getattr(self, next)

        return fn
