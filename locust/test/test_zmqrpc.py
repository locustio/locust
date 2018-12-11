import unittest
from time import sleep
import zmq
from locust.rpc import zmqrpc, Message

PORT = 5557

class ZMQRPC_tests(unittest.TestCase):

    def test_server(self):
        server = zmqrpc.Server('*', PORT)
        server.socket.close()

    def test_client(self):
        client = zmqrpc.Client('localhost', PORT, 'identity')
        client.socket.close()

    def test_client_send(self):
        server = zmqrpc.Server('*', PORT)
        client = zmqrpc.Client('localhost', PORT, 'identity')
        client.send(Message('test', None, None))
        server.recv_from_client()
        server.socket.close()
        client.socket.close()

    def test_client_recv(self):
        server = zmqrpc.Server('*', PORT)
        client = zmqrpc.Client('localhost', PORT, 'identity')
        sleep(0.01)
        # We have to wait for the client to finish connecting 
        # before sending a msg to it.
        server.send_to_client(Message('test', None, 'identity'))
        client.recv()
        server.socket.close()
        client.socket.close()
