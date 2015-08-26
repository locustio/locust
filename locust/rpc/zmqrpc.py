import zmq.green as zmq
from .protocol import Message

class BaseSocket(object):

    def send(self, msg):
        self.sender.send(msg.serialize())
    
    def recv(self):
        data = self.receiver.recv()
        return Message.unserialize(data)


class Server(BaseSocket):
    def __init__(self, host, port):
        context = zmq.Context()
        self.receiver = context.socket(zmq.PULL)
        self.receiver.bind("tcp://%s:%i" % (host, port))
        
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://%s:%i" % (host, port+1))
    

class Client(BaseSocket):
    def __init__(self, host, port):
        context = zmq.Context()
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://%s:%i" % (host, port+1))
        
        self.sender = context.socket(zmq.PUSH)
        self.sender.connect("tcp://%s:%i" % (host, port))
