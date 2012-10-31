import unittest

from gevent.queue import Queue
from gevent import sleep

from locust.runners import LocalLocustRunner, MasterLocustRunner, SlaveLocustRunner
from locust.core import Locust, task
from locust.rpc import Message


def mocked_rpc_server():
    class MockedRpcServer(object):
        queue = Queue()
        outbox = []
        
        @classmethod
        def mocked_send(cls, message):
            cls.queue.put(message)
        
        def recv(self):
            results = self.queue.get()
            return results
        
        def send(self, message):
            self.outbox.append(message)
    
    return MockedRpcServer


class TestMasterRunner(unittest.TestCase):
    def test_slave_connect(self):
        import mock
        
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, 10, 10, None)
            server.mocked_send(Message("client_ready", None, "zeh_fake_client1"))
            sleep(0)
            self.assertEqual(1, len(master.clients))
            self.assertTrue("zeh_fake_client1" in master.clients, "Could not find fake client in master instance's clients dict")
            server.mocked_send(Message("client_ready", None, "zeh_fake_client2"))
            server.mocked_send(Message("client_ready", None, "zeh_fake_client3"))
            server.mocked_send(Message("client_ready", None, "zeh_fake_client4"))
            sleep(0)
            self.assertEqual(4, len(master.clients))
            
            server.mocked_send(Message("quit", None, "zeh_fake_client3"))
            sleep(0)
            self.assertEqual(3, len(master.clients))
        
