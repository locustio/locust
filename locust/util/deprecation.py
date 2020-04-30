import warnings


# Show deprecation warnings
warnings.filterwarnings('always', category=DeprecationWarning, module="locust")


def check_for_deprecated_task_set_attribute(class_dict):
    from locust.user.task import TaskSet
    if "task_set" in class_dict:
        task_set = class_dict["task_set"]
        if issubclass(task_set, TaskSet) and not hasattr(task_set, "locust_task_weight"):
            warnings.warn("Usage of User.task_set is deprecated since version 1.0. Set the tasks attribute instead "
                          "(tasks = [%s])" % task_set.__name__, DeprecationWarning)
