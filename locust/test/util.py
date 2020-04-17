import os

from contextlib import contextmanager
from tempfile import NamedTemporaryFile

@contextmanager
def temporary_file(content, suffix="_locustfile.py"):
    f = NamedTemporaryFile(suffix=suffix, delete=False)
    f.write(content.encode("utf-8"))
    f.close()
    yield f.name
    if os.path.exists(f.name):
        os.remove(f.name)
