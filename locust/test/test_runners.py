import unittest

import gevent
from gevent import sleep
from gevent.queue import Queue

import mock
from locust import events
from locust.core import Locust, TaskSet, task
from locust.exception import LocustError
from locust.main import parse_options
from locust.rpc import Message
from locust.runners import LocalLocustRunner, MasterLocustRunner
from locust.stats import global_stats
from locust.test.testcases import LocustTestCase


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


class TestMasterRunner(LocustTestCase):
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
            events.report_to_master.fire(client_id="fake_client", data=data)
            master.stats.clear_all()
            
            server.mocked_send(Message("stats", data, "fake_client"))
            sleep(0)
            s = master.stats.get("/", "GET")
            self.assertEqual(700, s.median_response_time)
    
    def test_spawn_zero_locusts(self):
        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                pass
            
        class MyTestLocust(Locust):
            task_set = MyTaskSet
            min_wait = 100
            max_wait = 100
        
        runner = LocalLocustRunner([MyTestLocust], self.options)
        
        timeout = gevent.Timeout(2.0)
        timeout.start()
        
        try:
            runner.start_hatching(0, 1, wait=True)
            runner.greenlet.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception. A locust seems to have been spawned, even though 0 was specified.")
        finally:
            timeout.cancel()
    
    def test_spawn_uneven_locusts(self):
        """
        Tests that we can accurately spawn a certain number of locusts, even if it's not an 
        even number of the connected slaves
        """
        import mock
        
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            for i in range(5):
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))
                sleep(0)
            
            master.start_hatching(7, 7)
            self.assertEqual(5, len(server.outbox))
            
            num_clients = 0
            for msg in server.outbox:
                num_clients += Message.unserialize(msg).data["num_clients"]
            
            self.assertEqual(7, num_clients, "Total number of locusts that would have been spawned is not 7")
    
    def test_spawn_fewer_locusts_than_slaves(self):
        import mock
        
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            for i in range(5):
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))
                sleep(0)
            
            master.start_hatching(2, 2)
            self.assertEqual(5, len(server.outbox))
            
            num_clients = 0
            for msg in server.outbox:
                num_clients += Message.unserialize(msg).data["num_clients"]
            
            self.assertEqual(2, num_clients, "Total number of locusts that would have been spawned is not 2")
    
    def test_exception_in_task(self):
        class HeyAnException(Exception):
            pass
        
        class MyLocust(Locust):
            class task_set(TaskSet):
                @task
                def will_error(self):
                    raise HeyAnException(":(")
        
        runner = LocalLocustRunner([MyLocust], self.options)
        
        l = MyLocust()
        l._catch_exceptions = False
        
        self.assertRaises(HeyAnException, l.run)
        self.assertRaises(HeyAnException, l.run)
        self.assertEqual(1, len(runner.exceptions))
        
        hash_key, exception = runner.exceptions.popitem()
        self.assertTrue("traceback" in exception)
        self.assertTrue("HeyAnException" in exception["traceback"])
        self.assertEqual(2, exception["count"])
    
    def test_exception_is_catched(self):
        """ Test that exceptions are stored, and execution continues """
        class HeyAnException(Exception):
            pass
        
        class MyTaskSet(TaskSet):
            def __init__(self, *a, **kw):
                super(MyTaskSet, self).__init__(*a, **kw)
                self._task_queue = [
                    {"callable":self.will_error, "args":[], "kwargs":{}}, 
                    {"callable":self.will_stop, "args":[], "kwargs":{}},
                ]
            
            @task(1)
            def will_error(self):
                raise HeyAnException(":(")
            
            @task(1)
            def will_stop(self):
                self.interrupt()
        
        class MyLocust(Locust):
            min_wait = 10
            max_wait = 10
            task_set = MyTaskSet
        
        runner = LocalLocustRunner([MyLocust], self.options)
        l = MyLocust()
        
        # supress stderr
        with mock.patch("sys.stderr") as mocked:
            l.task_set._task_queue = [l.task_set.will_error, l.task_set.will_stop]
            self.assertRaises(LocustError, l.run) # make sure HeyAnException isn't raised
            l.task_set._task_queue = [l.task_set.will_error, l.task_set.will_stop]
            self.assertRaises(LocustError, l.run) # make sure HeyAnException isn't raised
        self.assertEqual(2, len(mocked.method_calls))
        
        # make sure exception was stored
        self.assertEqual(1, len(runner.exceptions))
        hash_key, exception = runner.exceptions.popitem()
        self.assertTrue("traceback" in exception)
        self.assertTrue("HeyAnException" in exception["traceback"])
        self.assertEqual(2, exception["count"])


class TestMessageSerializing(unittest.TestCase):
    def test_message_serialize(self):
        msg = Message("client_ready", None, "my_id")
        rebuilt = Message.unserialize(msg.serialize())
        self.assertEqual(msg.type, rebuilt.type)
        self.assertEqual(msg.data, rebuilt.data)
        self.assertEqual(msg.node_id, rebuilt.node_id)
