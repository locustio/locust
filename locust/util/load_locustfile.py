import importlib
import inspect
import os
import sys
from typing import Dict, Optional, Tuple
from ..shape import LoadTestShape
from ..user import User


def is_user_class(item):
    """
    Check if a variable is a runnable (non-abstract) User class
    """
    return bool(inspect.isclass(item) and issubclass(item, User) and item.abstract is False)


def is_shape_class(item):
    """
    Check if a class is a LoadTestShape
    """
    return bool(
        inspect.isclass(item) and issubclass(item, LoadTestShape) and item.__dict__["__module__"] != "locust.shape"
    )


def load_locustfile(path) -> Tuple[Optional[str], Dict[str, User], Optional[LoadTestShape]]:
    """
    Import given locustfile path and return (docstring, callables).

    Specifically, the locustfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a Locust" test.
    """

    # Start with making sure the current working dir is in the sys.path
    sys.path.insert(0, os.getcwd())
    # Get directory and locustfile name
    directory, locustfile = os.path.split(path)
    # If the directory isn't in the PYTHONPATH, add it so our import will work
    added_to_path = False
    index = None
    if directory not in sys.path:
        sys.path.insert(0, directory)
        added_to_path = True
    # If the directory IS in the PYTHONPATH, move it to the front temporarily,
    # otherwise other locustfiles -- like Locusts's own -- may scoop the intended
    # one.
    else:
        i = sys.path.index(directory)
        if i != 0:
            # Store index for later restoration
            index = i
            # Add to front, then remove from original position
            sys.path.insert(0, directory)
            del sys.path[i + 1]
    # Perform the import
    source = importlib.machinery.SourceFileLoader(os.path.splitext(locustfile)[0], path)
    imported = source.load_module()
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]
    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]
    # Return our two-tuple
    user_classes = {name: value for name, value in vars(imported).items() if is_user_class(value)}

    # Find shape class, if any, return it
    shape_classes = [value for name, value in vars(imported).items() if is_shape_class(value)]
    if shape_classes:
        shape_class = shape_classes[0]()
    else:
        shape_class = None

    return imported.__doc__, user_classes, shape_class
