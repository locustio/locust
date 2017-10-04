import unittest

import gevent
from gevent import sleep
from gevent.queue import Queue

import mock
from locust import events
from locust.core import Locust, TaskSet, task
from locust.exception import LocustError
from locust import config
from locust.rpc import Message
from locust import runners
from locust.runners import MasterLocustRunner, SlaveLocustRunner, WorkerLocustRunner
from locust.runners.worker import LocustRunner
from locust.stats import global_stats
from locust.test.testcases import LocustTestCase


def mocked_rpc_server():
    class MockedRpcServer(object):
        queue = Queue()
        outbox_all = []
        outbox_direct = []

        def __init__(self, *args):
            pass

        @classmethod
        def mocked_send(cls, to, message):
            cls.queue.put(to + ' ' + message.serialize())

        def recv(self):
            data = self.queue.get()
            msg = Message.unserialize(data.split(' ', 1)[1])
            getattr(self.handler, 'on_' + msg.type)(msg)

        def send_all(self, message):
            self.outbox_all.append(message.serialize())

        def send_to(self, id, message):
            self.outbox_direct.append((id, message.serialize()))

        def bind_handler(self, handler):
            self.handler = handler

        def close(self):
            pass

    return MockedRpcServer

def mocked_process():
    class MockedProcess(object):
        started = []

        def __init__(self, *args, **target):
            pass

        def start(self):
            self.started.append('pid')

    return MockedProcess


class TestMasterDefaultSlave(LocustTestCase):

    def tearDown(self):
        self.master.quit()

    def test_default_slave_up(self):
        class MyTestLocust(Locust):
            pass

        self.master = MasterLocustRunner(MyTestLocust, config.locust_config())
        self.assertEqual(self.master.slave_count, 1)


class TestMasterRunner(LocustTestCase):
    def setUp(self):
        global_stats.reset_all()
        self._slave_report_event_handlers = [h for h in events.node_report._handlers]

    def tearDown(self):
        events.node_report._handlers = self._slave_report_event_handlers
        self.master.quit()

    def test_slave_connect(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.MasterServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.master.Process", mocked_process()):
                server.mocked_send('all', Message("slave_ready", None, "zeh_fake_client1"))
                self.master = MasterLocustRunner(MyTestLocust, config.locust_config())
                sleep(0)
                self.assertEqual(1, self.master.slave_count)
                self.assertTrue(
                    "zeh_fake_client1" in self.master.slaves,
                    "Could not find fake client in master instance's clients dict"
                )
                server.mocked_send("all", Message("slave_ready", None, "zeh_fake_client2"))
                server.mocked_send("all", Message("slave_ready", None, "zeh_fake_client3"))
                server.mocked_send("all", Message("slave_ready", None, "zeh_fake_client4"))
                sleep(0)
                self.assertEqual(4, self.master.slave_count)

                server.mocked_send("all", Message("quit", None, "zeh_fake_client3"))
                sleep(0)
                self.assertEqual(3, self.master.slave_count)

    def test_automatic_options_propagate(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.MasterServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.master.Process", mocked_process()):
                server.mocked_send('all', Message("slave_ready", None, "zeh_fake_client1"))
                self.master = MasterLocustRunner(MyTestLocust, config.locust_config())
                sleep(0)
                self.assertEqual(1, self.master.slave_count)
                self.assertEqual(1, len(server.outbox_direct))
                msg = Message.unserialize(server.outbox_direct[0][1]).data
                self.assertEqual(self.master.options._config, msg)

    def test_on_demand_options_propagate(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.MasterServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.master.Process", mocked_process()):
                server.mocked_send('all', Message("slave_ready", None, "zeh_fake_client1"))
                self.master = MasterLocustRunner(MyTestLocust, config.locust_config())
                sleep(0)
                self.assertEqual(1, self.master.slave_count)
                server.outbox_all = []
                config_upd = {'host': 'custom_host.com', 'master_host': 'new_master_host.com'}
                self.master.propagate_config(config_upd)
                self.assertEqual(1, len(server.outbox_all))

                msg = Message.unserialize(server.outbox_all[0]).data
                self.assertEqual(msg['host'], 'custom_host.com')
                self.assertEqual(msg['master_host'], '127.0.0.1')

    def test_slave_stats_report_median(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.MasterServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.master.Process", mocked_process()):
                server.mocked_send('all', Message("slave_ready", None, "fake_client"))
                self.master = MasterLocustRunner(MyTestLocust, config.locust_config())
                sleep(0)

                self.master.stats.get("Task", "/", "GET").log(100, 23455)
                self.master.stats.get("Task", "/", "GET").log(800, 23455)
                self.master.stats.get("Task", "/", "GET").log(700, 23455)

                data = {"user_count": 1, "worker_count": 1}
                events.report_to_master.fire(node_id="fake_client", data=data)
                self.master.stats.clear_all()

                server.mocked_send("all", Message("stats", data, "fake_client"))
                sleep(0)
                s = self.master.stats.get("Task", "/", "GET")
                self.assertEqual(700, s.median_response_time)

    def test_spawn_uneven_locusts(self):
        """
        Tests that we can accurately spawn a certain number of locusts, even if it's not an
        even number of the connected slaves
        """
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.MasterServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.master.Process", mocked_process()):
                server.mocked_send('all', Message("slave_ready", None, "fake_client0"))
                self.master = MasterLocustRunner(MyTestLocust, config.locust_config())
                for i in range(1, 5):
                    server.mocked_send("all", Message("slave_ready", None, "fake_client%i" % i))
                    sleep(0)

                server.outbox_direct = []
                self.master.start_hatching(7, 7)
                self.assertEqual(5, len(server.outbox_direct))

                num_clients = 0
                for msg in server.outbox_direct:
                    num_clients += Message.unserialize(msg[1]).data["num_clients"]
                self.assertEqual(
                    7,
                    num_clients,
                    "Total number of locusts that would have been spawned is not 7"
                )

    def test_spawn_fewer_locusts_than_slaves(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.MasterServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.master.Process", mocked_process()):
                server.mocked_send('all', Message("slave_ready", None, "fake_client0"))
                self.master = MasterLocustRunner(MyTestLocust, config.locust_config())
                for i in range(1, 5):
                    server.mocked_send('all', Message("slave_ready", None, "fake_client%i" % i))
                    sleep(0)

                server.outbox_direct = []
                self.master.start_hatching(2, 2)
                self.assertEqual(5, len(server.outbox_direct))

                num_clients = 0
                for msg in server.outbox_direct:
                    num_clients += Message.unserialize(msg[1]).data["num_clients"]

                self.assertEqual(
                    2,
                    num_clients,
                    "Total number of locusts that would have been spawned is not 2"
                )

    def test_heartbeat(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.MasterServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.master.Process", mocked_process()):
                server.mocked_send('all', Message("slave_ready", None, "fake_client0"))
                self.master = MasterLocustRunner(MyTestLocust, config.locust_config())

                sleep(0)
                self.assertEqual(1, len(server.outbox_all))
                self.assertEqual('ping', Message.unserialize(server.outbox_all[0]).type)
                server.mocked_send('all', Message("pong", None, "fake_client0"))
                sleep(runners.master.HEARTBEAT_INTERVAL)
                self.assertEqual(1, self.master.slave_count)
                sleep(runners.master.HEARTBEAT_INTERVAL)
                self.assertEqual(0, self.master.slave_count)


class TestSlaveRunner(LocustTestCase):

    def setUp(self):
        global_stats.reset_all()
        self._slave_report_event_handlers = [h for h in events.node_report._handlers]

    def tearDown(self):
        events.node_report._handlers = self._slave_report_event_handlers
        self.slave.quit()

    def test_worker_connect(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.slave.Process", mocked_process()):
                self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())
                server.mocked_send('all', Message("worker_ready", None, "zeh_fake_client1"))
                sleep(0)
                self.slave.start_hatching(1, 1)
                self.assertEqual(1, self.slave.worker_count)
                self.assertTrue(
                    "zeh_fake_client1" in self.slave.workers,
                    "Could not find fake client in master instance's clients dict"
                )
                server.mocked_send("all", Message("worker_ready", None, "zeh_fake_client2"))
                server.mocked_send("all", Message("worker_ready", None, "zeh_fake_client3"))
                server.mocked_send("all", Message("worker_ready", None, "zeh_fake_client4"))
                sleep(0)
                self.assertEqual(4, self.slave.worker_count)

                server.mocked_send("all", Message("quit", None, "zeh_fake_client3"))
                sleep(0)
                self.assertEqual(3, self.slave.worker_count)

    def test_worker_receive_propagated_config(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveClient", mocked_rpc_server()) as client:
            with mock.patch("locust.runners.slave.Process", mocked_process()) as processes:
                self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())
                sleep(0)
                self.assertEqual(2, len(client.outbox_all))
                msg = {'host': 'custom_host.com', 'master_host': 'new_master_host.com'}
                client.mocked_send('all', Message("new_config", msg, "master"))
                sleep(0)
                self.assertEqual(self.slave.options.host, 'http://custom_host.com')
                self.assertEqual(self.slave.options.master_host, '127.0.0.1')

    def test_worker_stats_report_median(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.slave.Process", mocked_process()):
                self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())
                server.mocked_send('all', Message("worker_ready", None, "fake_client"))
                sleep(0)
                self.slave.start_hatching(1, 1)

                self.slave.stats.get("Task", "/", "GET").log(100, 23455)
                self.slave.stats.get("Task", "/", "GET").log(800, 23455)
                self.slave.stats.get("Task", "/", "GET").log(700, 23455)

                data = {"user_count": 1}
                events.report_to_master.fire(node_id="fake_client", data=data)
                self.slave.stats.clear_all()

                server.mocked_send("all", Message("stats", data, "fake_client"))
                sleep(0)
                s = self.slave.stats.get("Task", "/", "GET")
                self.assertEqual(700, s.median_response_time)

    def test_spawn_uneven_locusts(self):
        """
        Tests that we can accurately spawn a certain number of locusts, even if it's not an
        even number of the connected slaves
        """
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.slave.Process", mocked_process()):
                self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())
                server.mocked_send('all', Message("worker_ready", None, "fake_client0"))
                sleep(0)
                self.slave.start_hatching(1, 1)
                for i in range(1, 5):
                    server.mocked_send("all", Message("worker_ready", None, "fake_client%i" % i))
                    sleep(0)

                del server.outbox_direct[:]
                self.slave.start_hatching(42, 7)

                self.assertEqual(5, len(server.outbox_direct))

                num_clients = 0
                for msg in server.outbox_direct:
                    num_clients += Message.unserialize(msg[1]).data["num_clients"]
                self.assertEqual(
                    42,
                    num_clients,
                    "Total number of locusts that would have been spawned is not 42"
                )

    def test_worker_amount_spawn(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.slave.Process", mocked_process()) as processes:
                self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())

                timeout = gevent.Timeout(3.0)
                timeout.start()

                try:
                    for i in range(5):
                        server.mocked_send("all", Message("worker_ready", None, "fake_client%i" % i))
                    self.slave.start_hatching(42, 2)
                except gevent.Timeout:
                    self.fail("Got Timeout exception")
                finally:
                    timeout.cancel()

                self.assertEqual(5, len(processes.started))
                self.assertEqual(5, self.slave.worker_count)

    def test_heartbeat(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveServer", mocked_rpc_server()) as server:
            with mock.patch("locust.runners.slave.Process", mocked_process()):
                self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())
                server.mocked_send('all', Message("worker_ready", None, "fake_client0"))
                self.slave.start_hatching(1, 1)
                sleep(runners.slave.HEARTBEAT_INTERVAL)

                self.assertEqual(1, len(server.outbox_all))
                self.assertEqual('ping', Message.unserialize(server.outbox_all[0]).type)
                server.mocked_send('all', Message("pong", None, "fake_client0"))
                sleep(runners.slave.HEARTBEAT_INTERVAL)
                self.assertEqual(1, self.slave.worker_count)
                sleep(runners.slave.HEARTBEAT_INTERVAL)
                self.assertEqual(0, self.slave.worker_count)


    def worker_relaunch(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveServer", mocked_rpc_server()) as server:
            with mock.patch("locust.rpc.rpc.SlaveClient", mocked_rpc_server()) as client:
                with mock.patch("locust.runners.slave.Process", mocked_process()) as processes:
                    self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())
                    server.mocked_send('all', Message("worker_ready", None, "fake_client0"))
                    self.slave.start_hatching(1, 1)
                    self.assertEqual(1, len(processes.started))
                    sleep(2 * runners.slave.HEARTBEAT_INTERVAL)
                    self.assertEqual(0, self.slave.worker_count)
                    client.mocked_send('all', Message("ping", None, "master"))
                    sleep(runners.slave.HEARTBEAT_INTERVAL)
                    self.assertEqual(2, len(processes.started))

    def test_on_ping(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveClient", mocked_rpc_server()) as client:
            with mock.patch("locust.runners.slave.Process", mocked_process()) as processes:
                self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())
                sleep(0)
                self.assertEqual(2, len(client.outbox_all))
                client.mocked_send('all', Message("ping", None, "master"))
                sleep(0)
                self.assertEqual(3, len(client.outbox_all))

    def test_on_hatch(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveServer", mocked_rpc_server()) as server:
            with mock.patch("locust.rpc.rpc.SlaveClient", mocked_rpc_server()) as client:
                with mock.patch("locust.runners.slave.Process", mocked_process()) as processes:
                    self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())
                    for i in range(5):
                        server.mocked_send("all", Message("worker_ready", None, "fake_client%i" % i))

                    timeout = gevent.Timeout(2.0)
                    timeout.start()

                    try:
                        data = {
                            "hatch_rate": 10,
                            "num_clients": 43,
                            "num_requests": None,
                            "host": 'host',
                            "stop_timeout": None
                        }
                        client.mocked_send('all', Message("hatch", data, "master"))
                    except gevent.Timeout:
                        self.fail("Got Timeout exception. A locust seems to have been spawned, even though 0 was specified.")
                    finally:
                        timeout.cancel()

                    sleep(0)
                    self.assertEqual(5, len(processes.started))

    def test_stats_reporting(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.SlaveServer", mocked_rpc_server()) as server:
            with mock.patch("locust.rpc.rpc.SlaveClient", mocked_rpc_server()) as client:
                with mock.patch("locust.runners.slave.Process", mocked_process()) as processes:
                    self.slave = SlaveLocustRunner(MyTestLocust, config.locust_config())
                    server.mocked_send('all', Message("worker_ready", None, "fake_client0"))
                    self.slave.start_hatching(1, 1)

                    self.slave.stats.get("Task", "/", "GET").log(100, 23455)
                    self.slave.stats.get("Task", "/", "GET").log(800, 23455)
                    self.slave.stats.get("Task", "/", "GET").log(700, 23455)

                    sleep(runners.slave.SLAVE_STATS_INTERVAL + 0.1)
                    messages = [Message.unserialize(msg) for msg in client.outbox_all]
                    data = filter(lambda m: m.type == 'stats' and m.data['stats'], messages)[0].data

                    self.assertEqual({800: 1, 100: 1, 700: 1}, data['stats'][0]['response_times'])
                    self.assertEqual(3, data['stats'][0]['num_requests'])
                    self.assertEqual(1600, data['stats'][0]['total_response_time'])
                    self.assertEqual(1, data['worker_count'])


class TestWorkerRunner(LocustTestCase):

    def setUp(self):
        global_stats.reset_all()
        self._slave_report_event_handlers = [h for h in events.node_report._handlers]

    def tearDown(self):
        events.node_report._handlers = self._slave_report_event_handlers
        self.worker.quit()

    def test_on_ping(self):
        import mock

        class MyTestLocust(Locust):
            pass

        with mock.patch("locust.rpc.rpc.WorkerClient", mocked_rpc_server()) as client:
            self.worker = WorkerLocustRunner(MyTestLocust, config.locust_config())
            sleep(0)
            self.assertEqual(2, len(client.outbox_all))
            client.mocked_send('all', Message("ping", None, "master"))
            sleep(0)
            self.assertEqual(3, len(client.outbox_all))

    def test_on_hatch(self):
        import mock

        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                pass

        class MyTestLocust(Locust):
            task_set = MyTaskSet
            min_wait = 100
            max_wait = 100

        with mock.patch("locust.rpc.rpc.WorkerClient", mocked_rpc_server()) as client:
            self.worker = WorkerLocustRunner([MyTestLocust], config.locust_config())

            data = {
                "hatch_rate": 10,
                "num_clients": 10,
                "num_requests": None,
                "host": 'host',
                "stop_timeout": None
            }
            client.mocked_send('all', Message("hatch", data, "slave"))
            sleep(2)
            self.assertEqual(10, self.worker.user_count)

    def test_stats_reporting(self):
        import mock

        class MyTestLocust(Locust):
            pass


        with mock.patch("locust.rpc.rpc.WorkerClient", mocked_rpc_server()) as client:
            self.worker = WorkerLocustRunner([MyTestLocust], config.locust_config())

            self.worker.stats.get("Task", "/", "GET").log(100, 23455)
            self.worker.stats.get("Task", "/", "GET").log(800, 23455)
            self.worker.stats.get("Task", "/", "GET").log(700, 23455)

            sleep(runners.worker.WORKER_STATS_INTERVAL)
            data = Message.unserialize(client.outbox_all[-1]).data

            self.assertEqual({800: 1, 100: 1, 700: 1}, data['stats'][0]['response_times'])
            self.assertEqual(3, data['stats'][0]['num_requests'])
            self.assertEqual(1600, data['stats'][0]['total_response_time'])


class TestMessageSerializing(unittest.TestCase):
    def test_message_serialize(self):
        msg = Message("client_ready", None, "my_id")
        rebuilt = Message.unserialize(msg.serialize())
        self.assertEqual(msg.type, rebuilt.type)
        self.assertEqual(msg.data, rebuilt.data)
        self.assertEqual(msg.node_id, rebuilt.node_id)


class TestLocustRunner(LocustTestCase):
    def setUp(self):
        global_stats.reset_all()
        self._slave_report_event_handlers = [h for h in events.node_report._handlers]

    def tearDown(self):
        events.node_report._handlers = self._slave_report_event_handlers
        self.runner.stop()

    def test_spawn_zero_locusts(self):
        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                pass

        class MyTestLocust(Locust):
            task_set = MyTaskSet
            min_wait = 100
            max_wait = 100

        self.runner = LocustRunner([MyTestLocust], config.locust_config())

        timeout = gevent.Timeout(2.0)
        timeout.start()

        try:
            self.runner.start_hatching(0, 1, wait=True)
        except gevent.Timeout:
            self.fail("Got Timeout exception. A locust seems to have been spawned, even though 0 was specified.")
        finally:
            timeout.cancel()

    def test_exception_in_task(self):
        class HeyAnException(Exception):
            pass

        class MyLocust(Locust):
            class task_set(TaskSet):
                @task
                def will_error(self):
                    raise HeyAnException(":(")

        self.runner = LocustRunner([MyLocust], config.locust_config())

        l = MyLocust(config.locust_config())
        l._catch_exceptions = False

        self.assertRaises(HeyAnException, l.run)
        self.assertRaises(HeyAnException, l.run)
        self.assertEqual(1, len(self.runner.exceptions))

        hash_key, exception = self.runner.exceptions.popitem()
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

        self.runner = LocustRunner([MyLocust], config.locust_config())
        l = MyLocust(config.locust_config())

        # supress stderr
        with mock.patch("sys.stderr") as mocked:
            l.task_set._task_queue = [l.task_set.will_error, l.task_set.will_stop]
            self.assertRaises(LocustError, l.run) # make sure HeyAnException isn't raised
            l.task_set._task_queue = [l.task_set.will_error, l.task_set.will_stop]
            self.assertRaises(LocustError, l.run) # make sure HeyAnException isn't raised
        self.assertEqual(2, len(mocked.method_calls))

        # make sure exception was stored
        self.assertEqual(1, len(self.runner.exceptions))
        hash_key, exception = self.runner.exceptions.popitem()
        self.assertTrue("traceback" in exception)
        self.assertTrue("HeyAnException" in exception["traceback"])
        self.assertEqual(2, exception["count"])
