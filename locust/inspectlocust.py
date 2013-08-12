import inspect

from core import Locust, TaskSet
from log import console_logger

def print_task_ratio(locusts, total=False, level=0, parent_ratio=1.0):
    """
    Output table with task execution ratio info to console_logger
    """
    ratio = {}
    for locust in locusts:
        ratio.setdefault(locust, 0)
        ratio[locust] += 1

    # get percentage
    ratio_percent = dict(map(lambda x: (x[0], float(x[1])/len(locusts) * parent_ratio), ratio.iteritems()))
    
    for locust, ratio in ratio_percent.iteritems():
        console_logger.info(" %-10s %-50s" % ("  "*level + "%-6.1f" % (ratio*100), "  "*level + locust.__name__))
        if inspect.isclass(locust):
            if issubclass(locust, Locust):
                if total:
                    print_task_ratio(locust.task_set.tasks, total, level+1, ratio)
                else:
                    print_task_ratio(locust.task_set.tasks, total, level+1)
            elif issubclass(locust, TaskSet):
                if total:
                    print_task_ratio(locust.tasks, total, level+1, ratio)
                else:
                    print_task_ratio(locust.tasks, total, level+1)


def get_task_ratio_dict(tasks, total=False, parent_ratio=1.0):
    """
    Return a dict containing task execution ratio info
    """
    ratio = {}
    for task in tasks:
        ratio.setdefault(task, 0)
        ratio[task] += 1

    # get percentage
    ratio_percent = dict(map(lambda x: (x[0], float(x[1])/len(tasks) * parent_ratio), ratio.iteritems()))

    task_dict = {}
    for locust, ratio in ratio_percent.iteritems():
        d = {"ratio":ratio}
        if inspect.isclass(locust):
            if issubclass(locust, Locust):
                if total:
                    d["tasks"] = get_task_ratio_dict(locust.task_set.tasks, total, ratio)
                else:
                    d["tasks"] = get_task_ratio_dict(locust.task_set.tasks, total)
            elif issubclass(locust, TaskSet):
                if total:
                    d["tasks"] = get_task_ratio_dict(locust.tasks, total, ratio)
                else:
                    d["tasks"] = get_task_ratio_dict(locust.tasks, total)
        
        task_dict[locust.__name__] = d

    return task_dict