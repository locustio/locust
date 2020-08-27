from __future__ import absolute_import

import functools
from time import time


def memoize(timeout, dynamic_timeout=False):
    """
    Memoization decorator with support for timeout.

    If dynamic_timeout is set, the cache timeout is doubled if the cached function
    takes longer time to run than the timeout time
    """
    cache = {"timeout": timeout}

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time()
            if (not "time" in cache) or (start - cache["time"] > cache["timeout"]):
                # cache miss
                cache["result"] = func(*args, **kwargs)
                cache["time"] = time()
                if dynamic_timeout and cache["time"] - start > cache["timeout"]:
                    cache["timeout"] *= 2
            return cache["result"]

        def clear_cache():
            if "time" in cache:
                del cache["time"]
            if "result" in cache:
                del cache["result"]

        wrapper.clear_cache = clear_cache
        return wrapper

    return decorator
