import zmq.green as zmq
from .protocol import Message
from locust.util.exception_handler import retry
from locust.exception import RPCError, RPCSendError, RPCReceiveError
import zmq.error as zmqerr
import msgpack.exceptions as msgerr


class BaseSocket:
    def __init__(self, sock_type):
        context = zmq.Context()
        self.socket = context.socket(sock_type)

        self.socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self.socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 30)

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


class Server(BaseSocket):
    def __init__(self, host, port):
        BaseSocket.__init__(self, zmq.ROUTER)
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
        BaseSocket.__init__(self, zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity.encode())
        self.socket.connect("tcp://%s:%i" % (host, port))
