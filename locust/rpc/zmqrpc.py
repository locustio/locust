from locust.exception import RPCError, RPCReceiveError, RPCSendError
from locust.util.exception_handler import retry

import socket as csocket
from socket import gaierror, has_dualstack_ipv6

import msgpack.exceptions as msgerr
import zmq.error as zmqerr
import zmq.green as zmq

from .protocol import Message


class BaseSocket:
    def __init__(self, sock_type, ipv4_only):
        context = zmq.Context()
        self.socket = context.socket(sock_type)

        self.socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self.socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 30)
        if has_dualstack_ipv6() and not ipv4_only:
            self.socket.setsockopt(zmq.IPV6, 1)

    @retry()
    def send(self, msg):
        try:
            self.socket.send(msg.serialize(), zmq.NOBLOCK)
        except zmqerr.ZMQError as e:
            raise RPCSendError("ZMQ sent failure") from e

    @retry()
    def send_to_client(self, msg):
        try:
            self.socket.send_multipart([msg.node_id.encode(), msg.serialize()])
        except zmqerr.ZMQError as e:
            raise RPCSendError("ZMQ sent failure") from e

    def recv(self):
        try:
            data = self.socket.recv()
            msg = Message.unserialize(data)
        except msgerr.ExtraData as e:
            raise RPCReceiveError("ZMQ interrupted message") from e
        except zmqerr.ZMQError as e:
            raise RPCError("ZMQ network broken") from e
        return msg

    def recv_from_client(self):
        try:
            data = self.socket.recv_multipart()
            addr = data[0].decode()
        except UnicodeDecodeError as e:
            raise RPCReceiveError("ZMQ interrupted or corrupted message") from e
        except zmqerr.ZMQError as e:
            raise RPCError("ZMQ network broken") from e
        try:
            msg = Message.unserialize(data[1])
        except (UnicodeDecodeError, msgerr.ExtraData) as e:
            raise RPCReceiveError("ZMQ interrupted or corrupted message", addr=addr) from e
        return addr, msg

    def close(self, linger=None):
        self.socket.close(linger=linger)

    def ipv4_only(self, host, port) -> bool:
        try:
            if host == "*":
                return False
            if str(csocket.getaddrinfo(host, port, proto=csocket.IPPROTO_TCP)).find("Family.AF_INET6") == -1:
                return True
        except gaierror as e:
            print(f"Error resolving address: {e}")
            return False
        return False


class Server(BaseSocket):
    def __init__(self, host, port):
        BaseSocket.__init__(self, zmq.ROUTER, self.ipv4_only(host, port))
        if port == 0:
            self.port = self.socket.bind_to_random_port(f"tcp://{host}")
        else:
            try:
                self.socket.bind("tcp://%s:%i" % (host, port))
                self.port = port
            except zmqerr.ZMQError as e:
                raise RPCError(f"Socket bind failure: {e}")


class Client(BaseSocket):
    def __init__(self, host, port, identity):
        BaseSocket.__init__(self, zmq.DEALER, self.ipv4_only(host, port))
        self.socket.setsockopt(zmq.IDENTITY, identity.encode())
        self.socket.connect("tcp://%s:%i" % (host, port))
