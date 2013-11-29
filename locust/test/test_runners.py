import unittest

from gevent.queue import Queue
from gevent import sleep

from locust.runners import LocalLocustRunner, MasterLocustRunner, SlaveLocustRunner
from locust.core import Locust, task
from locust.rpc import Message
from locust.stats import RequestStats, global_stats
from locust.main import parse_options
from locust import events


def mocked_rpc_server():
    class MockedRpcServer(object):
        queue = Queue()
        outbox = []

        def __init__(self, host, port):
            pass
        
        @classmethod
        def mocked_send(cls, message):
            cls.queue.put(message.serialize())
        
        def recv(self):
            results = self.queue.get()
            return Message.unserialize(results)
        
        def send(self, message):
            self.outbox.append(message.serialize())
    
    return MockedRpcServer


class TestMasterRunner(unittest.TestCase):
    def setUp(self):
        global_stats.reset_all()
        self._slave_report_event_handlers = [h for h in events.slave_report._handlers]

        parser, _, _ = parse_options()
        args = [
            "--clients", "10",
            "--hatch-rate", "10"
        ]
        opts, _ = parser.parse_args(args)
        self.options = opts
        
    def tearDown(self):
        events.slave_report._handlers = self._slave_report_event_handlers
    
    def test_slave_connect(self):
        import mock
        
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
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
    
    def test_slave_stats_report_median(self):
        import mock
        
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            server.mocked_send(Message("client_ready", None, "fake_client"))
            sleep(0)
            
            master.stats.get("/", "GET").log(100, 23455)
            master.stats.get("/", "GET").log(800, 23455)
            master.stats.get("/", "GET").log(700, 23455)
            
            data = {"user_count":1}
            events.report_to_master.fire("fake_client", data)
            master.stats.clear_all()
            
            server.mocked_send(Message("stats", data, "fake_client"))
            sleep(0)
            s = master.stats.get("/", "GET")
            self.assertEqual(700, s.median_response_time)
    


class TestMessageSerializing(unittest.TestCase):
    def test_message_serialize(self):
        msg = Message("client_ready", None, "my_id")
        rebuilt = Message.unserialize(msg.serialize())
        self.assertEqual(msg.type, rebuilt.type)
        self.assertEqual(msg.data, rebuilt.data)
        self.assertEqual(msg.node_id, rebuilt.node_id)
        
