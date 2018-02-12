import os
import sys
import imp
import inspect
import logging
import core

def load(path):
    logger = logging.getLogger(__name__)

    if os.path.isdir(path):
        all_locustfiles = collect_locustfiles(path)
    else:
        locustfile = find_locustfile(path)

        if not locustfile:
            logger.error("Could not find any locustfile! Ensure file ends in '.py' and see --help for available options.")
            sys.exit(1)

        if locustfile == "locust.py":
            logger.error("The locustfile must not be named `locust.py`. Please rename the file and try again.")
            sys.exit(1)

        # docstring, all_locustsfiles = load_locustfile(locustfile)
        all_locustfiles = load_locustfile(locustfile)
    return all_locustfiles

def collect_locustfiles(path):
    collected = dict()

    for root, dirs, files in os.walk(path):
        if files:
            for file_ in files:
                if file_.endswith('.py') and not file_.endswith('__init__.py'):
                    fullpath = os.path.abspath(os.path.join(root, file_))
                    loaded = load_locustfile(fullpath)
                    if loaded:
                        collected.update(loaded)
    return collected

def populate_directories(os_path,working_dir):
    directories = dict()
    for root, subdirs, files in os.walk(os_path+working_dir):
        directories.update({os.sep+working_dir:os.sep+working_dir})
        for subdir in subdirs:
            directory = os.sep+os.path.join(root,subdir).replace(os_path,"")+os.sep
            directories.update({directory:directory})
    return directories

def load_locustfile(path):
    """
    Import given locustfile path and return (docstring, callables).
 
    Specifically, the locustfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a Locust" test.
    """
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
    # Perform the import (trimming off the .py)
    imported = imp.load_source(os.path.splitext(locustfile)[0], path)
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]
    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]
    # Return our two-tuple
    locusts = dict(filter(is_locust, vars(imported).items()))

    # truncate the fullpath
    final_path = truncate_path(path)

    return {final_path: locusts}

def find_locustfile(locustfile):
    """
    Attempt to locate a locustfile, either explicitly or by searching parent dirs.
    """
    # Obtain env value
    names = [locustfile]
    # Create .py version if necessary
    if not names[0].endswith('.py'):
        names += [names[0] + '.py']
    # Does the name contain path elements?
    if os.path.dirname(names[0]):
        # If so, expand home-directory markers and test for existence
        for name in names:
            expanded = os.path.expanduser(name)
            if os.path.exists(expanded):
                if name.endswith('.py') or _is_package(expanded):
                    return os.path.abspath(expanded)
    else:
        # Otherwise, start in cwd and work downwards towards filesystem root
        path = '.'
        # Stop before falling off root of filesystem (should be platform
        # agnostic)
        while os.path.split(os.path.abspath(path))[1]:
            for name in names:
                joined = os.path.join(path, name)
                if os.path.exists(joined):
                    if name.endswith('.py') or _is_package(joined):
                        return os.path.abspath(joined)
            path = os.path.join('..', path)
    # Implicit 'return None' if nothing was found

def truncate_path(path):
    # split path which comes from command on terminal
    splitted_path = os.path.normpath(path).split(os.path.sep)

    count = 0
    for i in reversed(xrange(len(splitted_path))):
        if count < 3 and splitted_path[i]:
            if count == 0:
                final_path = splitted_path[i]
            elif count == 2:
                final_path = os.path.join("...", splitted_path[i], final_path)
            else:
                final_path = os.path.join(splitted_path[i], final_path)
            count += 1
        else:
            break
    return final_path

def is_locust(tup):
    """
    Takes (name, object) tuple, returns True if it's a public Locust subclass.
    """
    name, item = tup
    return bool(
        inspect.isclass(item)
        and issubclass(item, core.Locust)
        and hasattr(item, "task_set")
        and getattr(item, "task_set")
        and not name.startswith('_')
    )

def _is_package(path):
    """
    Is the given path a Python package?
    """
    return (
        os.path.isdir(path)
        and os.path.exists(os.path.join(path, '__init__.py'))
    )