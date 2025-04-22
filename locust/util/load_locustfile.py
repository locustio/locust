from __future__ import annotations

import importlib
import importlib.util
import inspect
import os
import sys

from ..shape import LoadTestShape
from ..user import User


def is_user_class(item) -> bool:
    """
    Check if a variable is a runnable (non-abstract) User class
    """
    return bool(inspect.isclass(item) and issubclass(item, User) and item.abstract is False)


def is_shape_class(item) -> bool:
    """
    Check if a class is a LoadTestShape
    """
    return bool(inspect.isclass(item) and issubclass(item, LoadTestShape) and not getattr(item, "abstract", True))


def load_locustfile(path) -> tuple[dict[str, type[User]], list[LoadTestShape]]:
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
    module_name = os.path.splitext(locustfile)[0]
    if module_name == "locust":
        module_name = "locustfile"  # Avoid conflict with locust package
    loader = importlib.machinery.SourceFileLoader(module_name, path)
    spec = importlib.util.spec_from_file_location(module_name, path, loader=loader)
    if spec is None:
        sys.stderr.write(f"Unable to get module spec for {module_name} in {path}")
        sys.exit(1)

    imported = importlib.util.module_from_spec(spec)
    sys.modules[imported.__name__] = imported
    loader.exec_module(imported)

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
    shape_classes = [value() for value in vars(imported).values() if is_shape_class(value)]

    return user_classes, shape_classes
