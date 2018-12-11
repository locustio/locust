import zmq.green as zmq

from .protocol import Message


class BaseSocket(object):
    def __init__(self, sock_type):
        context = zmq.Context()
        self.socket = context.socket(sock_type)

    def send(self, msg):
        self.socket.send(msg.serialize())

    def send_to_client(self, msg):
        self.socket.send_multipart([msg.node_id.encode(), msg.serialize()])

    def recv(self):
        data = self.socket.recv()
        msg = Message.unserialize(data)
        return msg

    def recv_from_client(self):
        data = self.socket.recv_multipart()
        addr = data[0]
        msg = Message.unserialize(data[1])
        return addr, msg

class Server(BaseSocket):
    def __init__(self, host, port):
        BaseSocket.__init__(self, zmq.ROUTER)
        self.socket.bind("tcp://%s:%i" % (host, port))

class Client(BaseSocket):
    def __init__(self, host, port, identity):
        BaseSocket.__init__(self, zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity.encode())
        self.socket.connect("tcp://%s:%i" % (host, port))
        