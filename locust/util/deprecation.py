import warnings


# Show deprecation warnings
warnings.filterwarnings('always', category=DeprecationWarning, module="locust")


def check_for_deprecated_wait_api(locust_or_taskset):
    # check if deprecated wait API is used
    if locust_or_taskset.wait_function:
        warnings.warn("Usage of wait_function is deprecated since version 0.13. Declare a %s.wait_time method instead "
                      "(should return seconds and not milliseconds)" % type(locust_or_taskset).__name__, DeprecationWarning)
        from locust.core import TaskSet
        if not locust_or_taskset.wait_time or locust_or_taskset.wait_time.__func__ == TaskSet.wait_time:
            # If wait_function has been declared, and custom wait_time has NOT been declared, 
            # we'll add a wait_time function that just calls wait_function and divides the 
            # returned value by 1000.0
            locust_or_taskset.wait_time = lambda: locust_or_taskset.wait_function() / 1000.0
    if locust_or_taskset.min_wait is not None and locust_or_taskset.max_wait is not None:
        def format_min_max_wait(i):
            float_value = i / 1000.0
            if float_value == int(float_value):
                return "%i" % int(float_value)
            else:
                return "%.3f" % float_value
        warnings.warn("Usage of min_wait and max_wait is deprecated since version 0.13. Instead use: wait_time = between(%s, %s)" % (
            format_min_max_wait(locust_or_taskset.min_wait),
            format_min_max_wait(locust_or_taskset.max_wait),
        ), DeprecationWarning)
