import unittest

import gevent
from gevent import sleep
from gevent.queue import Queue

import mock
from locust import events
from locust.core import Locust, TaskSet, task
from locust.exception import LocustError
from locust.rpc import Message
from locust.runners import LocustRunner, LocalLocustRunner, MasterLocustRunner, SlaveNode, \
     STATE_INIT, STATE_HATCHING, STATE_RUNNING, STATE_MISSING
from locust.stats import global_stats, RequestStats
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
            sleep(0)
        
        def recv(self):
            results = self.queue.get()
            return Message.unserialize(results)
        
        def send(self, message):
            self.outbox.append(message.serialize())
    
        def send_to_client(self, message):
            self.outbox.append([message.node_id, message.serialize()])

        def recv_from_client(self):
            results = self.queue.get()
            msg = Message.unserialize(results)
            return msg.node_id, msg

    return MockedRpcServer


class mocked_options(object):
    def __init__(self):
        self.hatch_rate = 5
        self.num_clients = 5
        self.host = '/'
        self.master_host = 'localhost'
        self.master_port = 5557
        self.master_bind_host = '*'
        self.master_bind_port = 5557
        self.heartbeat_liveness = 3
        self.heartbeat_interval = 0.01
        self.stop_timeout = None

    def reset_stats(self):
        pass


class TestLocustRunner(LocustTestCase):
    def assert_locust_class_distribution(self, expected_distribution, classes):
        # Construct a {LocustClass => count} dict from a list of locust classes
        distribution = {}
        for locust_class in classes:
            if not locust_class in distribution:
                distribution[locust_class] = 0
            distribution[locust_class] += 1
        expected_str = str({k.__name__:v for k,v in expected_distribution.items()})
        actual_str = str({k.__name__:v for k,v in distribution.items()})
        self.assertEqual(
            expected_distribution,
            distribution,
            "Expected a locust class distribution of %s but found %s" % (
                expected_str,
                actual_str,
            ),
        )

    def test_weight_locusts(self):
        maxDiff = 2048
        class BaseLocust(Locust):
            class task_set(TaskSet): pass
        class L1(BaseLocust):
            weight = 101
        class L2(BaseLocust):
            weight = 99
        class L3(BaseLocust):
            weight = 100

        runner = LocustRunner([L1, L2, L3], mocked_options())
        self.assert_locust_class_distribution({L1:10, L2:9, L3:10}, runner.weight_locusts(29))
        self.assert_locust_class_distribution({L1:10, L2:10, L3:10}, runner.weight_locusts(30))
        self.assert_locust_class_distribution({L1:11, L2:10, L3:10}, runner.weight_locusts(31))

    def test_weight_locusts_fewer_amount_than_locust_classes(self):
        class BaseLocust(Locust):
            class task_set(TaskSet): pass
        class L1(BaseLocust):
            weight = 101
        class L2(BaseLocust):
            weight = 99
        class L3(BaseLocust):
            weight = 100

        runner = LocustRunner([L1, L2, L3], mocked_options())
        self.assertEqual(1, len(runner.weight_locusts(1)))
        self.assert_locust_class_distribution({L1:1},  runner.weight_locusts(1))
    
    def test_kill_locusts(self):
        triggered = [False]
        class BaseLocust(Locust):
            class task_set(TaskSet):
                @task
                def trigger(self):
                    triggered[0] = True
        runner = LocustRunner([BaseLocust], mocked_options())
        runner.spawn_locusts(2, wait=False)
        self.assertEqual(2, len(runner.locusts))
        g1 = list(runner.locusts)[0]
        g2 = list(runner.locusts)[1]
        runner.kill_locusts(2)
        self.assertEqual(0, len(runner.locusts))
        self.assertTrue(g1.dead)
        self.assertTrue(g2.dead)
        self.assertTrue(triggered[0])
        


class TestMasterRunner(LocustTestCase):
    def setUp(self):
        global_stats.reset_all()
        self._slave_report_event_handlers = [h for h in events.slave_report._handlers]
        self.options = mocked_options()

        
    def tearDown(self):
        events.slave_report._handlers = self._slave_report_event_handlers
    
    def test_slave_connect(self):
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            server.mocked_send(Message("client_ready", None, "zeh_fake_client1"))
            self.assertEqual(1, len(master.clients))
            self.assertTrue("zeh_fake_client1" in master.clients, "Could not find fake client in master instance's clients dict")
            server.mocked_send(Message("client_ready", None, "zeh_fake_client2"))
            server.mocked_send(Message("client_ready", None, "zeh_fake_client3"))
            server.mocked_send(Message("client_ready", None, "zeh_fake_client4"))
            self.assertEqual(4, len(master.clients))
            
            server.mocked_send(Message("quit", None, "zeh_fake_client3"))
            self.assertEqual(3, len(master.clients))
    
    def test_slave_stats_report_median(self):
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            server.mocked_send(Message("client_ready", None, "fake_client"))
            
            master.stats.get("/", "GET").log(100, 23455)
            master.stats.get("/", "GET").log(800, 23455)
            master.stats.get("/", "GET").log(700, 23455)
            
            data = {"user_count":1}
            events.report_to_master.fire(client_id="fake_client", data=data)
            master.stats.clear_all()
            
            server.mocked_send(Message("stats", data, "fake_client"))
            s = master.stats.get("/", "GET")
            self.assertEqual(700, s.median_response_time)

    def test_slave_stats_report_with_none_response_times(self):
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            server.mocked_send(Message("client_ready", None, "fake_client"))
            
            master.stats.get("/mixed", "GET").log(0, 23455)
            master.stats.get("/mixed", "GET").log(800, 23455)
            master.stats.get("/mixed", "GET").log(700, 23455)
            master.stats.get("/mixed", "GET").log(None, 23455)
            master.stats.get("/mixed", "GET").log(None, 23455)
            master.stats.get("/mixed", "GET").log(None, 23455)
            master.stats.get("/mixed", "GET").log(None, 23455)
            master.stats.get("/onlyNone", "GET").log(None, 23455)
            
            data = {"user_count":1}
            events.report_to_master.fire(client_id="fake_client", data=data)
            master.stats.clear_all()
            
            server.mocked_send(Message("stats", data, "fake_client"))
            s1 = master.stats.get("/mixed", "GET")
            self.assertEqual(700, s1.median_response_time)
            self.assertEqual(500, s1.avg_response_time)            
            s2 = master.stats.get("/onlyNone", "GET")
            self.assertEqual(0, s2.median_response_time)
            self.assertEqual(0, s2.avg_response_time)

    def test_master_marks_downed_slaves_as_missing(self):
        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            server.mocked_send(Message("client_ready", None, "fake_client"))
            sleep(0.1)
            # print(master.clients['fake_client'].__dict__)
            assert master.clients['fake_client'].state == STATE_MISSING

    def test_master_total_stats(self):
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            server.mocked_send(Message("client_ready", None, "fake_client"))
            stats = RequestStats()
            stats.log_request("GET", "/1", 100, 3546)
            stats.log_request("GET", "/1", 800, 56743)
            stats2 = RequestStats()
            stats2.log_request("GET", "/2", 700, 2201)
            server.mocked_send(Message("stats", {
                "stats":stats.serialize_stats(), 
                "stats_total": stats.total.serialize(),
                "errors":stats.serialize_errors(),
                "user_count": 1,
            }, "fake_client"))
            server.mocked_send(Message("stats", {
                "stats":stats2.serialize_stats(), 
                "stats_total": stats2.total.serialize(),
                "errors":stats2.serialize_errors(),
                "user_count": 2,
            }, "fake_client"))
            self.assertEqual(700, master.stats.total.median_response_time)

    def test_master_total_stats_with_none_response_times(self):
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            server.mocked_send(Message("client_ready", None, "fake_client"))
            stats = RequestStats()
            stats.log_request("GET", "/1", 100, 3546)
            stats.log_request("GET", "/1", 800, 56743)
            stats.log_request("GET", "/1", None, 56743)
            stats2 = RequestStats()
            stats2.log_request("GET", "/2", 700, 2201)
            stats2.log_request("GET", "/2", None, 2201)
            stats3 = RequestStats()
            stats3.log_request("GET", "/3", None, 2201)
            server.mocked_send(Message("stats", {
                "stats":stats.serialize_stats(), 
                "stats_total": stats.total.serialize(),
                "errors":stats.serialize_errors(),
                "user_count": 1,
            }, "fake_client"))
            server.mocked_send(Message("stats", {
                "stats":stats2.serialize_stats(), 
                "stats_total": stats2.total.serialize(),
                "errors":stats2.serialize_errors(),
                "user_count": 2,
            }, "fake_client"))
            server.mocked_send(Message("stats", {
                "stats":stats3.serialize_stats(), 
                "stats_total": stats3.total.serialize(),
                "errors":stats3.serialize_errors(),
                "user_count": 2,
            }, "fake_client"))
            self.assertEqual(700, master.stats.total.median_response_time)
        
    def test_master_current_response_times(self):
        class MyTestLocust(Locust):
            pass
        
        start_time = 1
        with mock.patch("time.time") as mocked_time:
            mocked_time.return_value = start_time
            global_stats.reset_all()
            with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
                master = MasterLocustRunner(MyTestLocust, self.options)
                mocked_time.return_value += 1
                server.mocked_send(Message("client_ready", None, "fake_client"))
                stats = RequestStats()
                stats.log_request("GET", "/1", 100, 3546)
                stats.log_request("GET", "/1", 800, 56743)
                server.mocked_send(Message("stats", {
                    "stats":stats.serialize_stats(),
                    "stats_total": stats.total.get_stripped_report(),
                    "errors":stats.serialize_errors(),
                    "user_count": 1,
                }, "fake_client"))
                mocked_time.return_value += 1
                stats2 = RequestStats()
                stats2.log_request("GET", "/2", 400, 2201)
                server.mocked_send(Message("stats", {
                    "stats":stats2.serialize_stats(),
                    "stats_total": stats2.total.get_stripped_report(),
                    "errors":stats2.serialize_errors(),
                    "user_count": 2,
                }, "fake_client"))
                mocked_time.return_value += 4
                self.assertEqual(400, master.stats.total.get_current_response_time_percentile(0.5))
                self.assertEqual(800, master.stats.total.get_current_response_time_percentile(0.95))
                
                # let 10 second pass, do some more requests, send it to the master and make
                # sure the current response time percentiles only accounts for these new requests
                mocked_time.return_value += 10
                stats.log_request("GET", "/1", 20, 1)
                stats.log_request("GET", "/1", 30, 1)
                stats.log_request("GET", "/1", 3000, 1)
                server.mocked_send(Message("stats", {
                    "stats":stats.serialize_stats(),
                    "stats_total": stats.total.get_stripped_report(),
                    "errors":stats.serialize_errors(),
                    "user_count": 2,
                }, "fake_client"))
                self.assertEqual(30, master.stats.total.get_current_response_time_percentile(0.5))
                self.assertEqual(3000, master.stats.total.get_current_response_time_percentile(0.95))
    
    def test_sends_hatch_data_to_ready_running_hatching_slaves(self):
        '''Sends hatch job to running, ready, or hatching slaves'''
        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            master.clients[1] = SlaveNode(1)
            master.clients[2] = SlaveNode(2)
            master.clients[3] = SlaveNode(3)
            master.clients[1].state = STATE_INIT
            master.clients[2].state = STATE_HATCHING
            master.clients[3].state = STATE_RUNNING
            master.start_hatching(5,5)

            self.assertEqual(3, len(server.outbox))

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
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            for i in range(5):
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))
            
            master.start_hatching(7, 7)
            self.assertEqual(5, len(server.outbox))
            
            num_clients = 0
            for _, msg in server.outbox:
                num_clients += Message.unserialize(msg).data["num_clients"]
            
            self.assertEqual(7, num_clients, "Total number of locusts that would have been spawned is not 7")
    
    def test_spawn_fewer_locusts_than_slaves(self):
        class MyTestLocust(Locust):
            pass
        
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc_server()) as server:
            master = MasterLocustRunner(MyTestLocust, self.options)
            for i in range(5):
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))
            
            master.start_hatching(2, 2)
            self.assertEqual(5, len(server.outbox))
            
            num_clients = 0
            for _, msg in server.outbox:
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

class TestStopTimeout(unittest.TestCase):
    def test_stop_timeout(self):
        short_time = 0.05
        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                MyTaskSet.state = "first"
                gevent.sleep(short_time)
                MyTaskSet.state = "second" # should only run when run time + stop_timeout is > short_time
                gevent.sleep(short_time)
                MyTaskSet.state = "third" # should only run when run time + stop_timeout is > short_time * 2

        class MyTestLocust(Locust):
            task_set = MyTaskSet
            min_wait = 0
            max_wait = 0
        
        options = mocked_options()
        runner = LocalLocustRunner([MyTestLocust], options)
        runner.start_hatching(1, 1)
        gevent.sleep(short_time / 2)
        runner.quit()
        self.assertEqual("first", MyTaskSet.state)

        options.stop_timeout = short_time / 2 # exit with timeout
        runner = LocalLocustRunner([MyTestLocust], options)
        runner.start_hatching(1, 1)
        gevent.sleep(short_time)
        runner.quit()
        self.assertEqual("second", MyTaskSet.state)
        
        options.stop_timeout = short_time * 3 # allow task iteration to complete, with some margin
        runner = LocalLocustRunner([MyTestLocust], options)
        runner.start_hatching(1, 1)
        gevent.sleep(short_time)
        timeout = gevent.Timeout(short_time * 2)
        timeout.start()
        try:
            runner.quit()
            runner.greenlet.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception. Some locusts must have kept runnining after iteration finish")
        finally:
            timeout.cancel()
        self.assertEqual("third", MyTaskSet.state)

    def test_stop_timeout_during_on_start(self):
        short_time = 0.05
        class MyTaskSet(TaskSet):
            finished_on_start = False
            my_task_run = False
            def on_start(self):
                gevent.sleep(short_time)
                MyTaskSet.finished_on_start = True

            @task
            def my_task(self):
                MyTaskSet.my_task_run = True

        class MyTestLocust(Locust):
            task_set = MyTaskSet
            min_wait = 0
            max_wait = 0
        
        options = mocked_options()
        options.stop_timeout = short_time
        runner = LocalLocustRunner([MyTestLocust], options)
        runner.start_hatching(1, 1)
        gevent.sleep(short_time / 2)
        runner.quit()

        self.assertTrue(MyTaskSet.finished_on_start)
        self.assertFalse(MyTaskSet.my_task_run)

    def test_stop_timeout_exit_during_wait(self):
        short_time = 0.05
        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                pass

        class MyTestLocust(Locust):
            task_set = MyTaskSet
            min_wait = 1000
            max_wait = 1000

        options = mocked_options()
        options.stop_timeout = short_time
        runner = LocalLocustRunner([MyTestLocust], options)
        runner.start_hatching(1, 1)
        gevent.sleep(short_time) # sleep to make sure locust has had time to start waiting
        timeout = gevent.Timeout(short_time)
        timeout.start()
        try:
            runner.quit()
            runner.greenlet.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception. Waiting locusts should stop immediately, even when using stop_timeout.")
        finally:
            timeout.cancel()

    def test_stop_timeout_with_interrupt(self):
        short_time = 0.05
        class MySubTaskSet(TaskSet):
            @task
            def a_task(self):
                gevent.sleep(0)
                self.interrupt(reschedule=True)

        class MyTaskSet(TaskSet):
            tasks = [MySubTaskSet]
        
        class MyTestLocust(Locust):
            task_set = MyTaskSet

        options = mocked_options()
        options.stop_timeout = short_time
        runner = LocalLocustRunner([MyTestLocust], options)
        runner.start_hatching(1, 1)
        gevent.sleep(0)
        timeout = gevent.Timeout(short_time)
        timeout.start()
        try:
            runner.quit()
            runner.greenlet.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception. Interrupted locusts should exit immediately during stop_timeout.")
        finally:
            timeout.cancel()
