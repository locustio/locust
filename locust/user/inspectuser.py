from collections import defaultdict
import inspect
from json import dumps
from typing import List, Type, Dict

from .task import TaskSet
from .users import User


def print_task_ratio(user_classes, num_users, total):
    """
    This function calculates the task ratio of users based on the user total count.
    """
    d = get_ratio(user_classes, _calc_distribution(user_classes, num_users), total)
    _print_task_ratio(d)


def print_task_ratio_json(user_classes, num_users):
    d = _calc_distribution(user_classes, num_users)
    task_data = {
        "per_class": get_ratio(user_classes, d, False),
        "total": get_ratio(user_classes, d, True),
    }

    print(dumps(task_data, indent=4))


def _calc_distribution(user_classes, num_users):
    fixed_count = sum(u.fixed_count for u in user_classes if u.fixed_count)
    total_weight = sum(u.weight for u in user_classes if not u.fixed_count)
    num_users = num_users or (total_weight if not fixed_count else 1)
    weighted_count = num_users - fixed_count
    weighted_count = weighted_count if weighted_count > 0 else 0
    user_classes_count = {}

    for u in user_classes:
        count = u.fixed_count if u.fixed_count else (u.weight / total_weight) * weighted_count
        user_classes_count[u.__name__] = round(count)

    return user_classes_count


def _print_task_ratio(x, level=0):
    padding = 2 * " " * level
    for k, v in x.items():
        ratio = v.get("ratio", 1)
        print(" %-10s %-50s" % (padding + "%-6.1f" % (ratio * 100), padding + k))
        if "tasks" in v:
            _print_task_ratio(v["tasks"], level + 1)


def get_ratio(user_classes: List[Type[User]], user_spawned: Dict[str, int], total: bool) -> Dict[str, Dict[str, float]]:
    user_count = sum(user_spawned.values()) or 1
    ratio_percent: Dict[Type[User], float] = {u: user_spawned.get(u.__name__, 0) / user_count for u in user_classes}

    task_dict: Dict[str, Dict[str, float]] = {}
    for u, r in ratio_percent.items():
        d = {"ratio": r}
        d["tasks"] = _get_task_ratio(u.tasks, total, r)
        task_dict[u.__name__] = d

    return task_dict


def _get_task_ratio(tasks, total, parent_ratio):
    parent_ratio = parent_ratio if total else 1.0
    ratio = defaultdict(int)
    for task in tasks:
        ratio[task] += 1

    ratio_percent = {t: r * parent_ratio / len(tasks) for t, r in ratio.items()}

    task_dict = {}
    for t, r in ratio_percent.items():
        d = {"ratio": r}
        if inspect.isclass(t) and issubclass(t, TaskSet):
            d["tasks"] = _get_task_ratio(t.tasks, total, r)
        task_dict[t.__name__] = d

    return task_dict
