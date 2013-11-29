import struct
import logging

import gevent
from gevent import socket
from gevent import queue

from locust.exception import LocustError
from .protocol import Message

logger = logging.getLogger(__name__)

def _recv_bytes(sock, bytes):
    data = ""
    while bytes:
        temp = sock.recv(bytes)
        if not temp:
            raise Exception("Connection reset by peer? Received so far: %r" % (data, ))
        bytes -= len(temp)
        data += temp
    return data

def _send_obj(sock, msg):
    data = msg.serialize()
    packed = struct.pack('!i', len(data)) + data
    try:
        sock.sendall(packed)
    except Exception as e:
        try:
            sock.close()
        except:
            pass
        finally:
            raise LocustError("Slave has disconnected")

def _recv_obj(sock):
    d = _recv_bytes(sock, 4)
    bytes, = struct.unpack('!i', d)
    data = _recv_bytes(sock, bytes)
    return Message.unserialize(data)

class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.command_queue = gevent.queue.Queue()
        self.socket = self._connect()

    def _connect(self):
        sock = socket.create_connection((self.host, self.port))
        def handle():
            try:
                while True:
                    self.command_queue.put_nowait(_recv_obj(sock))
            except Exception as e:
                try:
                    sock.close()
                except:
                    pass

        gevent.spawn(handle)
        return sock

    def send(self, event):
        _send_obj(self.socket, event)

    def recv(self):
        return self.command_queue.get()

class Server(object):
    def __init__(self, host, port):
        self.host = "0.0.0.0" if host == "*" else host
        self.port = port
        self.event_queue = gevent.queue.Queue()
        self.command_dispatcher = self._listen()

    def send(self, msg):
        self.command_dispatcher(msg)

    def recv(self):
        return self.event_queue.get()

    def _listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(256)
        self.slave_index = 0
        slaves = []

        def dispatch_command(cmd):

            _send_obj(slaves[self.slave_index], cmd)
            self.slave_index += 1
            if self.slave_index == len(slaves):
                self.slave_index = 0

        def handle_slave(sock):
            try:
                while True:
                    self.event_queue.put_nowait(_recv_obj(sock))
            except Exception as e:
                logger.info("Slave disconnected")
                slaves.remove(sock)
                if self.slave_index == len(slaves) and len(slaves) > 0:
                    self.slave_index -= 1

                try:
                    sock.close()
                except:
                    pass

        def listener():
            while True:
                _socket, _addr = sock.accept()
                logger.info("Slave connected")
                slaves.append(_socket)
                gevent.spawn(lambda: handle_slave(_socket))

        gevent.spawn(listener)
        return dispatch_command
