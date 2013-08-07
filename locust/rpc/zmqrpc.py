import zmq.green as zmq
from .protocol import Message


class Server(object):

    def __init__(self):
        context = zmq.Context()

        self.receiver = context.socket(zmq.PULL)
        self.receiver.bind("tcp://*:5557")

        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://*:5558")

    def send(self, msg):
        self.sender.send(msg.serialize())

    def recv(self):
        data = self.receiver.recv()
        return Message.unserialize(data)
    

class Client(object):

    def __init__(self, host):
        context = zmq.Context()

        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://%s:5558" % host)

        self.sender = context.socket(zmq.PUSH)
        self.sender.connect("tcp://%s:5557" % host)

    def send(self, msg):
        self.sender.send(msg.serialize())

    def recv(self):
        data = self.receiver.recv()
        return Message.unserialize(data)
