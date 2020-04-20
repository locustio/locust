import os
import socket

from contextlib import contextmanager
from tempfile import NamedTemporaryFile

@contextmanager
def temporary_file(content, suffix="_locustfile.py"):
    f = NamedTemporaryFile(suffix=suffix, delete=False)
    f.write(content.encode("utf-8"))
    f.close()
    try:
        yield f.name
    finally:
        if os.path.exists(f.name):
            os.remove(f.name)


def get_free_tcp_port():
    """
    Find an unused TCP port
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port
