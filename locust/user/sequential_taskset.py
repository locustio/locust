from locust.exception import LocustError
from .task import TaskSet, TaskSetMeta


class SequentialTaskSetMeta(TaskSetMeta):
    """
    Meta class for SequentialTaskSet. It's used to allow SequentialTaskSet classes to specify
    task execution in both a list as the tasks attribute or using the @task decorator

    We use the fact that class_dict order is the order of declaration in Python 3.6
    (See https://www.python.org/dev/peps/pep-0520/)
    """

    def __new__(mcs, classname, bases, class_dict):
        new_tasks = []
        for base in bases:
            # first get tasks from base classes
            if hasattr(base, "tasks") and base.tasks:
                new_tasks += base.tasks
        for key, value in class_dict.items():
            if key == "tasks":
                # we want to insert tasks from the tasks attribute at the point of it's declaration
                # compared to methods declared with @task
                if isinstance(value, list):
                    new_tasks.extend(value)
                else:
                    raise ValueError("On SequentialTaskSet the task attribute can only be set to a list")

            if "locust_task_weight" in dir(value):
                # method decorated with @task
                new_tasks.append(value)

        class_dict["tasks"] = new_tasks
        return type.__new__(mcs, classname, bases, class_dict)


class SequentialTaskSet(TaskSet, metaclass=SequentialTaskSetMeta):
    """
    Class defining a sequence of tasks that a User will execute.

    Works like TaskSet, but task weight is ignored, and all tasks are executed in order. Tasks can
    either be specified by setting the *tasks* attribute to a list of tasks, or by declaring tasks
    as methods using the @task decorator. The order of declaration decides the order of execution.

    It's possible to combine a task list in the *tasks* attribute, with some tasks declared using
    the @task decorator. The order of declaration is respected also in that case.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task_index = 0

    def get_next_task(self):
        if not self.tasks:
            raise LocustError(
                "No tasks defined. use the @task decorator or set the tasks property of the SequentialTaskSet"
            )
        task = self.tasks[self._task_index % len(self.tasks)]
        self._task_index += 1
        return task
