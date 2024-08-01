import os


def get_abspaths_in(path, extension=None):
    return [
        os.path.abspath(os.path.join(root, f))
        for root, _dirs, fs in os.walk(path)
        for f in fs
        if os.path.isfile(os.path.join(root, f))
        and (f.endswith(extension) or extension is None)
        and not f.startswith("_")
    ]
