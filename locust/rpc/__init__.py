import warnings

try:
    from . import zmqrpc as rpc
except ImportError:
    warnings.warn("WARNING: Using pure Python socket RPC implementation instead of zmq. If running in distributed mode, this could cause a performance decrease. We recommend you to install the pyzmq python package when running in distributed mode.")
    from . import socketrpc as rpc

from .protocol import Message
