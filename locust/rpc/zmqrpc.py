import zmq.green as zmq
from zmq import ZMQError
from .protocol import Message


class BaseSocket(object):

    def bind_handler(self, handler):
        self.handler = handler

    def send_all(self, msg):
        self.sender.send('all ' + msg.serialize())

    def send_to(self, id, msg):
        self.sender.send(id + ' ' + msg.serialize())

    def recv(self):
        data = self.receiver.recv()
        msg = Message.unserialize(data.split(' ', 1)[1])
        getattr(self.handler, 'on_' + msg.type)(msg)

    def close(self):
        self.sender.close()
        self.receiver.close()
        self.context.term()

class MasterServer(BaseSocket):
    def __init__(self, host, port):
        context = zmq.Context()
        self.context = context

        self.receiver = context.socket(zmq.SUB)
        self.receiver.bind("tcp://%s:%i" % (host, port))
        self.receiver.setsockopt(zmq.SUBSCRIBE, '')

        self.sender = context.socket(zmq.PUB)
        self.sender.bind("tcp://%s:%i" % (host, port + 1))


class SlaveClient(BaseSocket):
    def __init__(self, host, port, id):
        context = zmq.Context()
        self.context = context

        self.receiver = context.socket(zmq.SUB)
        self.receiver.connect("tcp://%s:%i" % (host, port + 1))
        self.receiver.setsockopt(zmq.SUBSCRIBE, 'all')
        self.receiver.setsockopt(zmq.SUBSCRIBE, id)

        self.sender = context.socket(zmq.PUB)
        self.sender.connect("tcp://%s:%i" % (host, port))


class SlaveServer(MasterServer):
    def __init__(self, port):
        super(SlaveServer, self).__init__('*', port + 2)


class WorkerClient(SlaveClient):
    def __init__(self, port, id):
        super(WorkerClient, self).__init__('127.0.0.1', port + 2, id)
