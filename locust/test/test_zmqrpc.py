import unittest
from time import sleep
import zmq
from locust.rpc import zmqrpc, Message

PORT = 5557

class ZMQRPC_tests(unittest.TestCase):
    def setUp(self):
        self.server = zmqrpc.Server('*', PORT)
        self.client = zmqrpc.Client('localhost', PORT, 'identity')

    def tearDown(self):
        self.server.socket.close()
        self.client.socket.close()

    def test_client_send(self):
        self.client.send(Message('test', 'message', 'identity'))
        addr, msg = self.server.recv_from_client()
        self.assertEqual(addr, 'identity')
        self.assertEqual(msg.type, 'test')
        self.assertEqual(msg.data, 'message')

    def test_client_recv(self):
        sleep(0.1)
        # We have to wait for the client to finish connecting 
        # before sending a msg to it.
        self.server.send_to_client(Message('test', 'message', 'identity'))
        msg = self.client.recv()
        self.assertEqual(msg.type, 'test')
        self.assertEqual(msg.data, 'message')
        self.assertEqual(msg.node_id, 'identity')
