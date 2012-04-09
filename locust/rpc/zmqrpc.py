from gevent_zeromq import zmq

try:
    import cPickle as pickle
except ImportError:
    import pickle

class Server(object):
    def __init__(self):
        context = zmq.Context()
        
        self.receiver = context.socket(zmq.PULL)
        self.receiver.bind("tcp://*:5557")
        
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://*:5558")
    
    def send(self, data):
        self.sender.send(pickle.dumps(data))
    
    def recv(self):
        data = self.receiver.recv()
        return pickle.loads(data)
    
class Client(object):
    def __init__(self, host):
        context = zmq.Context()
        
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://%s:5558" % host)
        
        self.sender = context.socket(zmq.PUSH)
        self.sender.connect("tcp://%s:5557" % host)
    
    def send(self, data):
        self.sender.send(pickle.dumps(data))
    
    def recv(self):
        data = self.receiver.recv()
        return pickle.loads(data)