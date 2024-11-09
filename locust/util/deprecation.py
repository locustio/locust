import warnings

# Show deprecation warnings
warnings.filterwarnings("always", category=DeprecationWarning, module="locust")


def check_for_deprecated_task_set_attribute(class_dict):
    from locust.user.task import TaskSet

    if "task_set" in class_dict:
        task_set = class_dict["task_set"]
        if issubclass(task_set, TaskSet) and not hasattr(task_set, "locust_task_weight"):
            warnings.warn(
                "Usage of User.task_set is deprecated since version 1.0. Set the tasks attribute instead "
                f"(tasks = [{task_set.__name__}])",
                DeprecationWarning,
            )


def deprecated_locust_meta_class(deprecation_message):
    class MetaClass(type):
        def __new__(mcs, classname, bases, class_dict):
            if classname in ["DeprecatedLocustClass", "DeprecatedHttpLocustClass", "DeprecatedFastHttpLocustClass"]:
                return super().__new__(mcs, classname, bases, class_dict)
            else:
                raise ImportError(deprecation_message)

    return MetaClass


# PEP 484 specifies "Generic metaclasses are not supported", see https://github.com/python/mypy/issues/3602, ignore typing errors
class DeprecatedLocustClass(
    metaclass=deprecated_locust_meta_class(  # type: ignore
        "The Locust class has been renamed to User in version 1.0. "
        "For more info see: https://docs.locust.io/en/latest/changelog.html#changelog-1-0"
    )
):
    pass


class DeprecatedHttpLocustClass(
    metaclass=deprecated_locust_meta_class(  # type: ignore
        "The HttpLocust class has been renamed to HttpUser in version 1.0. "
        "For more info see: https://docs.locust.io/en/latest/changelog.html#changelog-1-0"
    )
):
    pass


class DeprecatedFastHttpLocustClass(
    metaclass=deprecated_locust_meta_class(  # type: ignore
        "The FastHttpLocust class has been renamed to FastHttpUser in version 1.0. "
        "For more info see: https://docs.locust.io/en/latest/changelog.html#changelog-1-0"
    )
):
    pass
