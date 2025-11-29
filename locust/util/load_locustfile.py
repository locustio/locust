from __future__ import annotations

import importlib
import importlib.util
import inspect
import os
import sys

from ..shape import LoadTestShape
from ..user import User
from ..user.users import PytestUser


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


def load_locustfile_pytest(path) -> dict[str, type[User]]:
    """
    Create User classes from pytest test functions.

    It relies on some pytest internals to collect test functions and their fixtures,
    but it should be reasonably stable for simple use cases.

    Fixtures (like `session` and `fastsession`) are defined in `pytestplugin.py`

    See `examples/test_pytest.py` and `locust/test/test_pytest_locustfile.py`
    """
    import pytest
    from _pytest.config import Config

    user_classes: dict[str, type[PytestUser]] = {}
    # collect tests and set up fixture manager
    config = Config.fromdictargs(
        {},
        [
            "-q",  # suppress pytest loggings about "test session starts" and "collected 0 items" etc
            "-s",  # dont capture stdin (locust uses it for opening a browser and other input events)
            path,
        ],
    )
    config._do_configure()
    session = pytest.Session.from_config(config)
    config.hook.pytest_sessionstart(session=session)
    session.perform_collect()
    config.hook.pytest_collection_modifyitems(session=session, config=config, items=session.items)
    fm = session._fixturemanager

    for function in session.items:
        if isinstance(function, pytest.Function):
            sig = inspect.signature(function.obj)
            function.kwargs = {}  # type: ignore[attr-defined]
            for name in sig.parameters:
                defs = fm.getfixturedefs(name, function)
                if not defs:
                    raise ValueError(f"Could not find fixture for parameter {name!r} in {function.name}")
                if len(defs) > 1:
                    raise ValueError(f"Multiple fixtures found for parameter {name!r} in {function.name}: {defs}")
                function.fixturedef = defs[0]  # type: ignore[attr-defined]
            if not function.name in user_classes:
                user_classes[function.name] = type(function.name, (PytestUser,), {})
                user_classes[function.name].functions = []
            user_classes[function.name].functions.append(function)
        else:
            pass  # Skipping non-function item
    return user_classes  # type: ignore
