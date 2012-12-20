from collections import namedtuple
import warnings

try:
    import zmqrpc as rpc
except ImportError:
    warnings.warn("WARNING: Using pure Python socket RPC implementation instead of zmq. This will not affect you if you're not running locust in distributed mode, but if you are, we recommend you to install the python packages: pyzmq and gevent-zeromq")
    import socketrpc as rpc

Message = namedtuple("Message", ["type", "data", "node_id"])
