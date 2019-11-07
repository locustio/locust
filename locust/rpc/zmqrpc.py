import zmq.green as zmq

from .protocol import Message
from locust.util.exception_handler import retry

class BaseSocket(object):
    def __init__(self, sock_type):
        context = zmq.Context()
        self.socket = context.socket(sock_type)

        self.socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self.socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 30)
    
    @retry()
    def send(self, msg):
        self.socket.send(msg.serialize())

    @retry()
    def send_to_client(self, msg):
        self.socket.send_multipart([msg.node_id.encode(), msg.serialize()])

    @retry()
    def recv(self):
        data = self.socket.recv()
        msg = Message.unserialize(data)
        return msg

    @retry()
    def recv_from_client(self):
        data = self.socket.recv_multipart()
        addr = data[0].decode()
        msg = Message.unserialize(data[1])
        return addr, msg

class Server(BaseSocket):
    def __init__(self, host, port):
        BaseSocket.__init__(self, zmq.ROUTER)
        if port == 0:
            self.port = self.socket.bind_to_random_port("tcp://%s" % host)
        else:
            self.socket.bind("tcp://%s:%i" % (host, port))
            self.port = port

class Client(BaseSocket):
    def __init__(self, host, port, identity):
        BaseSocket.__init__(self, zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity.encode())
        self.socket.connect("tcp://%s:%i" % (host, port))
        