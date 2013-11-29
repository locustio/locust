import zmq.green as zmq
from .protocol import Message

class BaseSocket(object):
    def __init__(self, host, port):
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self._init_socket(host, port)

    def _init_socket():
        raise NotImplementedError

    def send(self, msg):
        self.socket.send(msg.serialize())
    
    def recv(self):
        data = self.socket.recv()
        return Message.unserialize(data)


class Server(BaseSocket):
    def _init_socket(self, host, port):
        self.socket.bind("tcp://%s:%d" % (host, port))
    

class Client(BaseSocket):
    def _init_socket(self, host, port):
        self.socket.connect("tcp://%s:%d" % (host, port))
    