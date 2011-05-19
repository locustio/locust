import struct, pickle
import gevent
from gevent import socket
from gevent import queue
from gevent.event import AsyncResult


def sendObj(sock, obj):
    data = pickle.dumps(obj)
    packed = struct.pack('!i', len(data)) + data
    sock.sendall(packed)

def _recvBytes(sock, bytes):
    data = ""
    while bytes:
        temp = sock.recv(bytes)
        if not temp:
            raise Exception("Connection reset by peer? Received so far: %r" % (data, ))
        bytes -= len(temp)
        data += temp
    return data

def recvObj(sock):
    d = _recvBytes(sock, 4)
    bytes, = struct.unpack('!i', d)
    data = _recvBytes(sock, bytes)
    return pickle.loads(data)



def clientCommand(serverIp, serverPort, obj):
    """ Sends a command to a remote server, and returns the result """

    sock = socket.create_connection((serverIp, serverPort))
    sendObj(sock, obj)
    response = recvObj(sock)
    sock.close()
    return response


def clientEventListener(serverIp, serverPort, callback):
    """ Starts a listener for events from a remote server. The specified callback will be called with the event as only argument """

    def task():
        while True:
            try:
                sock = socket.create_connection((serverIp, serverPort))
                while True:
                    cmd = recvObj(sock)
                    response = callback(cmd)
                    sendObj(sock, response)
            except Exception, e:
                try:
                    sock.close()
                except:
                    pass
                gevent.sleep(1)
    gevent.spawn(task)



def serverCommandListener(bindIp, bindPort, callback):
    """ Starts a listener for inbound commands. The specified callback wwill be called with the command as only argument. """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bindIp, bindPort))
    sock.listen(256)
    def listen():
        while True:
            s, addr = sock.accept()
            def handle():
                cmd = recvObj(s)
                responseObj = callback(cmd)
                sendObj(s, responseObj)
                s.close()
            gevent.spawn(handle)

    gevent.spawn(listen)



def serverEventDispatcher(bindIp, bindPort):
    """ This method sets up a listener and returns a function.
        Calling the function with an event object will distribute it to all connected clients.
        Returns a dictionary with results mapped by client address.
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bindIp, bindPort))
    sock.listen(256)
    queues = set()

    def dispatchEvent(obj):
        asyncResults = []
        for q in queues:
            ar = AsyncResult()
            asyncResults.append(ar)
            q.put_nowait((ar, obj))

        results = {}
        for ar in asyncResults:
            addr, result = ar.get()
            results[addr] = result

        return results


    def listener():
        while True:
            _s, _addr = sock.accept()
            def handle(s, addr):
                q = queue.Queue()
                queues.add(q)
                try:
                    while True:
                        asyncResult, eventObj = q.get()
                        try:
                            sendObj(s, eventObj)
                            result = recvObj(s)
                        except Exception, e:
                            result = None
                        finally:
                            asyncResult.set((addr, result))

                except Exception, e:
                    queues.discard(q)
                    try:
                        s.close()
                    except:
                        pass
            gevent.spawn(lambda : handle(_s, _addr))

    gevent.spawn(listener)

    return dispatchEvent



class Client(object):
    def __init__(self, host):
        self.host = host
        self.port = 5558
        self.eventQueue = gevent.queue.Queue()
        clientEventListener(self.host, self.port, self.eventQueue.put_nowait)

    def send(self, msg):
        clientCommand(self.host, self.port, msg)

    def recv(self):
        return self.eventQueue.get()

class Server(object):
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 5558
        self.eventQueue = gevent.queue.Queue()
        serverCommandListener(self.host, self.port, self.eventQueue.put_nowait)
        self.eventDispatcher = serverEventDispatcher(self.host, self.port)

    def send(self, msg):
        self.eventDispatcher(msg)

    def recv(self):
        self.eventQueue.get()
