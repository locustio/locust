import unittest
from time import sleep
import zmq
from locust.rpc import zmqrpc, Message


class ZMQRPC_tests(unittest.TestCase):
    def setUp(self):
        self.server = zmqrpc.Server('*', 0)
        self.client = zmqrpc.Client('localhost', self.server.port, 'identity')

    def tearDown(self):
        self.server.socket.close()
        self.client.socket.close()

    def test_constructor(self):
        self.assertEqual(self.server.socket.getsockopt(zmq.TCP_KEEPALIVE), 1)
        self.assertEqual(self.server.socket.getsockopt(zmq.TCP_KEEPALIVE_IDLE), 30)
        self.assertEqual(self.client.socket.getsockopt(zmq.TCP_KEEPALIVE), 1)
        self.assertEqual(self.client.socket.getsockopt(zmq.TCP_KEEPALIVE_IDLE), 30)

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

    def test_client_retry(self):
        server = zmqrpc.Server('0.0.0.0', 8888)
        server.socket.close()
        with self.assertRaises(zmq.error.ZMQError):
            server.recv_from_client()
