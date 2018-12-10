import zmq.green as zmq

from .protocol import Message


class BaseSocket(object):
    def __init__(self, sock_type):
        context = zmq.Context()
        self.socket = context.socket(sock_type)

    def send(self, msg):
        self.socket.send(msg.serialize())
    
    def send_multipart(self, client_id, msg):
        print 'sending %s to %s' % (msg, client_id)
        self.socket.send_multipart([client_id, msg.serialize()])

    def recv(self):
        data = self.socket.recv()
        msg = Message.unserialize(data)
        return msg

    def recv_multipart(self):
        try:
            data = self.socket.recv_multipart()
            addr = data[0]
            msg = Message.unserialize(data[1])
            return addr, msg
        except Exception:
            raise

class Server(BaseSocket):
    def __init__(self, host, port):
        BaseSocket.__init__(self, zmq.ROUTER)
        self.socket.bind("tcp://%s:%i" % (host, port))

class Client(BaseSocket):
    def __init__(self, host, port, identity):
        BaseSocket.__init__(self, zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, identity)
        self.socket.connect("tcp://%s:%i" % (host, port))
        