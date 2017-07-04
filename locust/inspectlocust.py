import inspect
import six

from .core import Locust, TaskSet
from .log import console_logger

def print_task_ratio(locusts, total=False, level=0, parent_ratio=1.0):
    d = get_task_ratio_dict(locusts, total=total, parent_ratio=parent_ratio)
    _print_task_ratio(d)

def _print_task_ratio(x, level=0):
    for k, v in six.iteritems(x):
        padding = 2*" "*level
        ratio = v.get('ratio', 1)
        console_logger.info(" %-10s %-50s" % (padding + "%-6.1f" % (ratio*100), padding + k))
        if 'tasks' in v:
            _print_task_ratio(v['tasks'], level + 1)


def get_task_ratio_dict(tasks, total=False, parent_ratio=1.0):
    """
    Return a dict containing task execution ratio info
    """
    if hasattr(tasks[0], 'weight'):
        divisor = sum(t.weight for t in tasks)
    else:
        divisor = len(tasks) / parent_ratio
    ratio = {}
    for task in tasks:
        ratio.setdefault(task, 0)
        ratio[task] += task.weight if hasattr(task, 'weight') else 1

    # get percentage
    ratio_percent = dict((k, float(v) / divisor) for k, v in six.iteritems(ratio))

    task_dict = {}
    for locust, ratio in six.iteritems(ratio_percent):
        d = {"ratio":ratio}
        if inspect.isclass(locust):
            if issubclass(locust, Locust):
                T = locust.task_set.tasks
            elif issubclass(locust, TaskSet):
                T = locust.tasks
            if total:
                d["tasks"] = get_task_ratio_dict(T, total, ratio)
            else:
                d["tasks"] = get_task_ratio_dict(T, total)
        
        task_dict[locust.__name__] = d

    return task_dict


def get_task_execution_order(locust):
    """
    Return a dict containing task execution order info
    """
    task_list = []
    for task in locust.task_set.tasks:
        task_list.append(task.__name__)
    return task_list


def get_task_dict_with_order(tasks):
    """
    Return a dict containing task execution order info
    """
    order_dict = {}
    for task in tasks:
        order_dict.setdefault(task, None)
        if hasattr(task, 'order'):
            order_dict[task] = task.order
        elif hasattr(task, 'locust_task_order'):
            order_dict[task] = task.locust_task_order

    task_dict = {}
    for locust, order in six.iteritems(order_dict):
        d = {"order":order}
        if inspect.isclass(locust):
            if issubclass(locust, Locust):
                T = locust.task_set.tasks
            elif issubclass(locust, TaskSet):
                T = locust.tasks
            d["tasks"] = get_task_dict_with_order(T)

        task_dict[locust.__name__] = d

    return task_dict
