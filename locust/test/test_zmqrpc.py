from time import sleep
import zmq
from locust.rpc import zmqrpc, Message
from locust.test.testcases import LocustTestCase
from locust.exception import RPCError


class ZMQRPC_tests(LocustTestCase):
    def setUp(self):
        super().setUp()
        self.server = zmqrpc.Server("127.0.0.1", 0)
        self.client = zmqrpc.Client("localhost", self.server.port, "identity")

    def tearDown(self):
        self.server.close()
        self.client.close()
        super().tearDown()

    def test_constructor(self):
        self.assertEqual(self.server.socket.getsockopt(zmq.TCP_KEEPALIVE), 1)
        self.assertEqual(self.server.socket.getsockopt(zmq.TCP_KEEPALIVE_IDLE), 30)
        self.assertEqual(self.client.socket.getsockopt(zmq.TCP_KEEPALIVE), 1)
        self.assertEqual(self.client.socket.getsockopt(zmq.TCP_KEEPALIVE_IDLE), 30)

    def test_client_send(self):
        self.client.send(Message("test", "message", "identity"))
        addr, msg = self.server.recv_from_client()
        self.assertEqual(addr, "identity")
        self.assertEqual(msg.type, "test")
        self.assertEqual(msg.data, "message")

    def test_client_recv(self):
        sleep(0.1)
        # We have to wait for the client to finish connecting
        # before sending a msg to it.
        self.server.send_to_client(Message("test", "message", "identity"))
        msg = self.client.recv()
        self.assertEqual(msg.type, "test")
        self.assertEqual(msg.data, "message")
        self.assertEqual(msg.node_id, "identity")

    def test_client_retry(self):
        server = zmqrpc.Server("127.0.0.1", 0)
        server.socket.close()
        with self.assertRaises(RPCError):
            server.recv_from_client()

    def test_rpc_error(self):
        server = zmqrpc.Server("127.0.0.1", 0)
        with self.assertRaises(RPCError):
            server = zmqrpc.Server("127.0.0.1", server.port)
        server.close()
        with self.assertRaises(RPCError):
            server.send_to_client(Message("test", "message", "identity"))
