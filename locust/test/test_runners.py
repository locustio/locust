import json
import os
import random
import time
import unittest
from collections import defaultdict
from contextlib import contextmanager
from operator import itemgetter

import gevent
import mock
import requests
from gevent import sleep
from gevent.pool import Group
from gevent.queue import Queue

import locust
from locust import (
    LoadTestShape,
    constant,
    runners,
    __version__,
)
from locust.argument_parser import parse_options
from locust.env import Environment
from locust.exception import (
    RPCError,
    StopUser,
)
from locust.main import create_environment
from locust.rpc import Message
from locust.runners import (
    LocalRunner,
    STATE_INIT,
    STATE_SPAWNING,
    STATE_RUNNING,
    STATE_MISSING,
    STATE_STOPPING,
    STATE_STOPPED,
    WorkerNode,
    WorkerRunner,
)
from locust.stats import RequestStats
from .testcases import LocustTestCase
from locust.user import (
    TaskSet,
    User,
    task,
)
from retry import retry

NETWORK_BROKEN = "network broken"


def mocked_rpc():
    class MockedRpcServerClient:
        queue = Queue()
        outbox = []

        def __init__(self, *args, **kwargs):
            pass

        @classmethod
        def mocked_send(cls, message):
            cls.queue.put(message.serialize())
            sleep(0)

        def recv(self):
            results = self.queue.get()
            msg = Message.unserialize(results)
            if msg.data == NETWORK_BROKEN:
                raise RPCError()
            return msg

        def send(self, message):
            self.outbox.append(message)

        def send_to_client(self, message):
            self.outbox.append((message.node_id, message))

        def recv_from_client(self):
            results = self.queue.get()
            msg = Message.unserialize(results)
            if msg.data == NETWORK_BROKEN:
                raise RPCError()
            return msg.node_id, msg

        def close(self):
            raise RPCError()

    return MockedRpcServerClient


class mocked_options:
    def __init__(self):
        self.spawn_rate = 5
        self.num_users = 5
        self.host = "/"
        self.tags = None
        self.exclude_tags = None
        self.master_host = "localhost"
        self.master_port = 5557
        self.master_bind_host = "*"
        self.master_bind_port = 5557
        self.heartbeat_liveness = 3
        self.heartbeat_interval = 1
        self.stop_timeout = None
        self.connection_broken = False

    def reset_stats(self):
        pass


class HeyAnException(Exception):
    pass


class TestLocustRunner(LocustTestCase):
    def test_cpu_warning(self):
        _monitor_interval = runners.CPU_MONITOR_INTERVAL
        runners.CPU_MONITOR_INTERVAL = 2.0
        try:

            class CpuUser(User):
                wait_time = constant(0.001)

                @task
                def cpu_task(self):
                    for i in range(1000000):
                        _ = 3 / 2

            environment = Environment(user_classes=[CpuUser])
            runner = LocalRunner(environment)
            self.assertFalse(runner.cpu_warning_emitted)
            runner.spawn_users({CpuUser.__name__: 1}, wait=False)
            sleep(2.5)
            runner.quit()
            self.assertTrue(runner.cpu_warning_emitted)
        finally:
            runners.CPU_MONITOR_INTERVAL = _monitor_interval

    def test_kill_locusts(self):
        triggered = [False]

        class BaseUser(User):
            wait_time = constant(1)

            @task
            class task_set(TaskSet):
                @task
                def trigger(self):
                    triggered[0] = True

        runner = Environment(user_classes=[BaseUser]).create_local_runner()
        users = runner.spawn_users({BaseUser.__name__: 2}, wait=False)
        self.assertEqual(2, len(users))
        self.assertEqual(2, len(runner.user_greenlets))
        g1 = list(runner.user_greenlets)[0]
        g2 = list(runner.user_greenlets)[1]
        runner.stop_users({BaseUser.__name__: 2})
        self.assertEqual(0, len(runner.user_greenlets))
        self.assertTrue(g1.dead)
        self.assertTrue(g2.dead)
        self.assertTrue(triggered[0])

    def test_start_event(self):
        class MyUser(User):
            wait_time = constant(2)
            task_run_count = 0

            @task
            def my_task(self):
                MyUser.task_run_count += 1

        test_start_run = [0]

        environment = Environment(user_classes=[MyUser])

        def on_test_start(*args, **kwargs):
            test_start_run[0] += 1

        environment.events.test_start.add_listener(on_test_start)

        runner = LocalRunner(environment)
        runner.start(user_count=3, spawn_rate=3, wait=False)
        runner.spawning_greenlet.get(timeout=3)

        self.assertEqual(1, test_start_run[0])
        self.assertEqual(3, MyUser.task_run_count)

    def test_stop_event(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        test_stop_run = [0]
        environment = Environment(user_classes=[User])

        def on_test_stop(*args, **kwargs):
            test_stop_run[0] += 1

        environment.events.test_stop.add_listener(on_test_stop)

        runner = LocalRunner(environment)
        runner.start(user_count=3, spawn_rate=3, wait=False)
        self.assertEqual(0, test_stop_run[0])
        runner.stop()
        self.assertEqual(1, test_stop_run[0])

    def test_stop_event_quit(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        test_stop_run = [0]
        environment = Environment(user_classes=[User])

        def on_test_stop(*args, **kwargs):
            test_stop_run[0] += 1

        environment.events.test_stop.add_listener(on_test_stop)

        runner = LocalRunner(environment)
        runner.start(user_count=3, spawn_rate=3, wait=False)
        self.assertEqual(0, test_stop_run[0])
        runner.quit()
        self.assertEqual(1, test_stop_run[0])

    def test_stop_event_stop_and_quit(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        test_stop_run = [0]
        environment = Environment(user_classes=[MyUser])

        def on_test_stop(*args, **kwargs):
            test_stop_run[0] += 1

        environment.events.test_stop.add_listener(on_test_stop)

        runner = LocalRunner(environment)
        runner.start(user_count=3, spawn_rate=3, wait=False)
        self.assertEqual(0, test_stop_run[0])
        runner.stop()
        runner.quit()
        self.assertEqual(1, test_stop_run[0])

    def test_change_user_count_during_spawning(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        environment = Environment(user_classes=[MyUser])
        runner = LocalRunner(environment)
        runner.start(user_count=10, spawn_rate=5, wait=False)
        sleep(0.6)
        runner.start(user_count=5, spawn_rate=5, wait=False)
        runner.spawning_greenlet.join()
        self.assertEqual(5, len(runner.user_greenlets))
        runner.quit()

    def test_reset_stats(self):
        class MyUser(User):
            @task
            class task_set(TaskSet):
                @task
                def my_task(self):
                    self.user.environment.events.request.fire(
                        request_type="GET",
                        name="/test",
                        response_time=666,
                        response_length=1337,
                        exception=None,
                        context={},
                    )
                    # Make sure each user only run this task once during the test
                    sleep(30)

        environment = Environment(user_classes=[MyUser], reset_stats=True)
        runner = LocalRunner(environment)
        runner.start(user_count=6, spawn_rate=1, wait=False)
        sleep(3)
        self.assertGreaterEqual(runner.stats.get("/test", "GET").num_requests, 3)
        sleep(3.25)
        self.assertLessEqual(runner.stats.get("/test", "GET").num_requests, 1)
        runner.quit()

    def test_no_reset_stats(self):
        class MyUser(User):
            @task
            class task_set(TaskSet):
                @task
                def my_task(self):
                    self.user.environment.events.request.fire(
                        request_type="GET",
                        name="/test",
                        response_time=666,
                        response_length=1337,
                        exception=None,
                        context={},
                    )
                    sleep(2)

        environment = Environment(reset_stats=False, user_classes=[MyUser])
        runner = LocalRunner(environment)
        runner.start(user_count=6, spawn_rate=12, wait=False)
        sleep(0.25)
        self.assertGreaterEqual(runner.stats.get("/test", "GET").num_requests, 3)
        sleep(0.3)
        self.assertEqual(6, runner.stats.get("/test", "GET").num_requests)
        runner.quit()

    def test_runner_reference_on_environment(self):
        env = Environment()
        runner = env.create_local_runner()
        self.assertEqual(env, runner.environment)
        self.assertEqual(runner, env.runner)

    def test_users_can_call_runner_quit_without_deadlocking(self):
        class BaseUser(User):
            stop_triggered = False

            @task
            def trigger(self):
                self.environment.runner.quit()

            def on_stop(self):
                BaseUser.stop_triggered = True

        runner = Environment(user_classes=[BaseUser]).create_local_runner()
        users = runner.spawn_users({BaseUser.__name__: 1}, wait=False)
        self.assertEqual(1, len(users))
        timeout = gevent.Timeout(0.5)
        timeout.start()
        try:
            runner.greenlet.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception, runner must have hung somehow.")
        finally:
            timeout.cancel()

        self.assertTrue(BaseUser.stop_triggered)

    def test_runner_quit_can_run_on_stop_for_multiple_users_concurrently(self):
        class BaseUser(User):
            stop_count = 0

            @task
            def trigger(self):
                pass

            def on_stop(self):
                gevent.sleep(0.1)
                BaseUser.stop_count += 1

        runner = Environment(user_classes=[BaseUser]).create_local_runner()
        users = runner.spawn_users({BaseUser.__name__: 10}, wait=False)
        self.assertEqual(10, len(users))
        timeout = gevent.Timeout(0.3)
        timeout.start()
        try:
            runner.quit()
        except gevent.Timeout:
            self.fail("Got Timeout exception, runner must have hung somehow.")
        finally:
            timeout.cancel()

        self.assertEqual(10, BaseUser.stop_count)  # verify that all users executed on_stop

    def test_stop_users_with_spawn_rate(self):
        """
        The spawn rate does not have an effect on the rate at which the users are stopped.
        It is expected that the excess users will be stopped as soon as possible in parallel
        (while respecting the stop_timeout).
        """

        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        environment = Environment(user_classes=[MyUser])
        runner = LocalRunner(environment)

        # Start load test, wait for users to start, then trigger ramp down
        ts = time.time()
        runner.start(10, 10, wait=False)
        runner.spawning_greenlet.join()
        delta = time.time() - ts
        self.assertTrue(
            0 <= delta <= 0.05, "Expected user count to increase to 10 instantaneously, instead it took %f" % delta
        )
        self.assertTrue(
            runner.user_count == 10, "User count has not decreased correctly to 2, it is : %i" % runner.user_count
        )

        ts = time.time()
        runner.start(2, 4, wait=False)
        runner.spawning_greenlet.join()
        delta = time.time() - ts
        self.assertTrue(0 <= delta <= 1.05, "Expected user count to decrease to 2 in 1s, instead it took %f" % delta)
        self.assertTrue(
            runner.user_count == 2, "User count has not decreased correctly to 2, it is : %i" % runner.user_count
        )

    def test_attributes_populated_when_calling_start(self):
        class MyUser1(User):
            wait_time = constant(0)

            @task
            def my_task(self):
                pass

        class MyUser2(User):
            wait_time = constant(0)

            @task
            def my_task(self):
                pass

        environment = Environment(user_classes=[MyUser1, MyUser2])
        runner = LocalRunner(environment)

        runner.start(user_count=10, spawn_rate=5, wait=False)
        runner.spawning_greenlet.join()
        self.assertDictEqual({"MyUser1": 5, "MyUser2": 5}, runner.user_classes_count)

        runner.start(user_count=5, spawn_rate=5, wait=False)
        runner.spawning_greenlet.join()
        self.assertDictEqual({"MyUser1": 3, "MyUser2": 2}, runner.user_classes_count)

        runner.quit()

    def test_user_classes_count(self):
        class MyUser1(User):
            wait_time = constant(0)

            @task
            def my_task(self):
                pass

        class MyUser2(User):
            wait_time = constant(0)

            @task
            def my_task(self):
                pass

        environment = Environment(user_classes=[MyUser1, MyUser2])
        runner = LocalRunner(environment)

        runner.start(user_count=10, spawn_rate=5, wait=False)
        runner.spawning_greenlet.join()
        self.assertDictEqual({"MyUser1": 5, "MyUser2": 5}, runner.user_classes_count)

        runner.start(user_count=5, spawn_rate=5, wait=False)
        runner.spawning_greenlet.join()
        self.assertDictEqual({"MyUser1": 3, "MyUser2": 2}, runner.user_classes_count)

        runner.quit()

    def test_custom_message(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        test_custom_msg = [False]
        test_custom_msg_data = [{}]

        def on_custom_msg(msg, **kw):
            test_custom_msg[0] = True
            test_custom_msg_data[0] = msg.data

        environment = Environment(user_classes=[MyUser])
        runner = LocalRunner(environment)

        runner.register_message("test_custom_msg", on_custom_msg)
        runner.send_message("test_custom_msg", {"test_data": 123})

        self.assertTrue(test_custom_msg[0])
        self.assertEqual(123, test_custom_msg_data[0]["test_data"])

    def test_undefined_custom_message(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        test_custom_msg = [False]

        def on_custom_msg(msg, **kw):
            test_custom_msg[0] = True

        environment = Environment(user_classes=[MyUser])
        runner = LocalRunner(environment)

        runner.register_message("test_custom_msg", on_custom_msg)
        runner.send_message("test_different_custom_msg")

        self.assertFalse(test_custom_msg[0])
        self.assertEqual(1, len(self.mocked_log.warning))
        msg = self.mocked_log.warning[0]
        self.assertIn("Unknown message type recieved", msg)

    def test_swarm_endpoint_is_non_blocking(self):
        class TestUser1(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        class TestUser2(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        stop_timeout = 0
        env = Environment(user_classes=[TestUser1, TestUser2], stop_timeout=stop_timeout)
        local_runner = env.create_local_runner()
        web_ui = env.create_web_ui("127.0.0.1", 0)

        gevent.sleep(0.1)

        ts = time.perf_counter()
        response = requests.post(
            "http://127.0.0.1:{}/swarm".format(web_ui.server.server_port),
            data={"user_count": 20, "spawn_rate": 5, "host": "https://localhost"},
        )
        self.assertEqual(200, response.status_code)
        self.assertTrue(0 <= time.perf_counter() - ts <= 1, "swarm endpoint is blocking")

        ts = time.perf_counter()
        while local_runner.state != STATE_RUNNING:
            self.assertTrue(time.perf_counter() - ts <= 4, local_runner.state)
            gevent.sleep(0.1)

        self.assertTrue(3 <= time.perf_counter() - ts <= 5)

        self.assertEqual(local_runner.user_count, 20)

        local_runner.stop()
        web_ui.stop()

    def test_can_call_stop_endpoint_if_currently_swarming(self):
        class TestUser1(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        class TestUser2(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        stop_timeout = 5
        env = Environment(user_classes=[TestUser1, TestUser2], stop_timeout=stop_timeout)
        local_runner = env.create_local_runner()
        web_ui = env.create_web_ui("127.0.0.1", 0)

        gevent.sleep(0.1)

        ts = time.perf_counter()
        response = requests.post(
            "http://127.0.0.1:{}/swarm".format(web_ui.server.server_port),
            data={"user_count": 20, "spawn_rate": 1, "host": "https://localhost"},
        )
        self.assertEqual(200, response.status_code)
        self.assertTrue(0 <= time.perf_counter() - ts <= 1, "swarm endpoint is blocking")

        gevent.sleep(5)

        self.assertEqual(local_runner.state, STATE_SPAWNING)
        self.assertLessEqual(local_runner.user_count, 10)

        ts = time.perf_counter()
        response = requests.get(
            "http://127.0.0.1:{}/stop".format(web_ui.server.server_port),
        )
        self.assertEqual(200, response.status_code)
        self.assertTrue(stop_timeout <= time.perf_counter() - ts <= stop_timeout + 5, "stop endpoint took too long")

        ts = time.perf_counter()
        while local_runner.state != STATE_STOPPED:
            self.assertTrue(time.perf_counter() - ts <= 2)
            gevent.sleep(0.1)

        self.assertLessEqual(local_runner.user_count, 0)

        local_runner.stop()
        web_ui.stop()

    def test_target_user_count_is_set_before_ramp_up(self):
        """Test for https://github.com/locustio/locust/issues/1883"""

        class MyUser1(User):
            wait_time = constant(0)

            @task
            def my_task(self):
                pass

        environment = Environment(user_classes=[MyUser1])
        runner = LocalRunner(environment)

        test_start_event_fired = [False]

        @environment.events.test_start.add_listener
        def on_test_start(*args, **kwargs):
            test_start_event_fired[0] = True
            self.assertEqual(runner.target_user_count, 3)

        runner.start(user_count=3, spawn_rate=1, wait=False)

        gevent.sleep(1)

        self.assertEqual(runner.target_user_count, 3)
        self.assertEqual(runner.user_count, 1)
        # However, target_user_classes_count is only updated at the end of the ramp-up/ramp-down
        # due to the way it is implemented.
        self.assertDictEqual({}, runner.target_user_classes_count)

        runner.spawning_greenlet.join()

        self.assertEqual(runner.target_user_count, 3)
        self.assertEqual(runner.user_count, 3)
        self.assertDictEqual({"MyUser1": 3}, runner.target_user_classes_count)

        runner.quit()

        self.assertTrue(test_start_event_fired[0])


class TestMasterWorkerRunners(LocustTestCase):
    def test_distributed_integration_run(self):
        """
        Full integration test that starts both a MasterRunner and three WorkerRunner instances
        and makes sure that their stats is sent to the Master.
        """

        class TestUser(User):
            wait_time = constant(0.1)

            @task
            def incr_stats(self):
                self.environment.events.request.fire(
                    request_type="GET",
                    name="/",
                    response_time=1337,
                    response_length=666,
                    exception=None,
                    context={},
                )

        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
            # start a Master runner
            master_env = Environment(user_classes=[TestUser])
            master = master_env.create_master_runner("*", 0)
            sleep(0)
            # start 3 Worker runners
            workers = []
            for i in range(3):
                worker_env = Environment(user_classes=[TestUser])
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            # give workers time to connect
            sleep(0.1)
            # issue start command that should trigger TestUsers to be spawned in the Workers
            master.start(6, spawn_rate=1000)
            sleep(0.1)
            # check that worker nodes have started locusts
            for worker in workers:
                self.assertEqual(2, worker.user_count)
            # give time for users to generate stats, and stats to be sent to master
            sleep(1)
            master.quit()
            # make sure users are killed
            for worker in workers:
                self.assertEqual(0, worker.user_count)

        # check that stats are present in master
        self.assertGreater(
            master_env.runner.stats.total.num_requests,
            20,
            "For some reason the master node's stats has not come in",
        )

    def test_distributed_rebalanced_integration_run(self):
        """
        Full integration test that starts both a MasterRunner and three WorkerRunner instances
        and makes sure that their stats is sent to the Master.
        """

        class TestUser(User):
            wait_time = constant(0.1)

            @task
            def incr_stats(self):
                self.environment.events.request.fire(
                    request_type="GET",
                    name="/",
                    response_time=1337,
                    response_length=666,
                    exception=None,
                    context={},
                )

        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
            # start a Master runner
            options = parse_options(["--enable-rebalancing"])
            master_env = Environment(user_classes=[TestUser], parsed_options=options)
            master = master_env.create_master_runner("*", 0)
            sleep(0)
            # start 3 Worker runners
            workers = []

            def add_worker():
                worker_env = Environment(user_classes=[TestUser])
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            for i in range(3):
                add_worker()

            # give workers time to connect
            sleep(0.1)
            # issue start command that should trigger TestUsers to be spawned in the Workers
            master.start(6, spawn_rate=1000)
            sleep(0.1)
            # check that worker nodes have started locusts
            for worker in workers:
                self.assertEqual(2, worker.user_count)
            # give time for users to generate stats, and stats to be sent to master
            # Add 1 more workers (should be 4 now)
            add_worker()

            @retry(AssertionError, tries=10, delay=0.5)
            def check_rebalanced_true():
                for worker in workers:
                    self.assertTrue(worker.user_count > 0)

            # Check that all workers have a user count > 0 at least
            check_rebalanced_true()
            # Add 2 more workers (should be 6 now)
            add_worker()
            add_worker()

            @retry(AssertionError, tries=10, delay=0.5)
            def check_rebalanced_equals():
                for worker in workers:
                    self.assertEqual(1, worker.user_count)

            # Check that all workers have a user count = 1 now
            check_rebalanced_equals()

            # Simulate that some workers are missing by "killing" them abrutly
            for i in range(3):
                workers[i].greenlet.kill(block=True)

            @retry(AssertionError, tries=10, delay=1)
            def check_master_worker_missing_count():
                self.assertEqual(3, len(master.clients.missing))

            # Check that master detected the missing workers
            check_master_worker_missing_count()

            @retry(AssertionError, tries=10, delay=1)
            def check_remaing_worker_new_user_count():
                for i in range(3, 6):
                    self.assertEqual(2, workers[i].user_count)

            # Check that remaining workers have a new count of user due to rebalancing.
            check_remaing_worker_new_user_count()
            sleep(1)

            # Finally quit and check states of remaining workers.
            master.quit()
            # make sure users are killed on remaining workers
            for i in range(3, 6):
                self.assertEqual(0, workers[i].user_count)

        # check that stats are present in master
        self.assertGreater(
            master_env.runner.stats.total.num_requests,
            20,
            "For some reason the master node's stats has not come in",
        )

    def test_distributed_run_with_custom_args(self):
        """
        Full integration test that starts both a MasterRunner and three WorkerRunner instances
        and makes sure that their stats is sent to the Master.
        """

        class TestUser(User):
            wait_time = constant(0.1)

            @task
            def incr_stats(self):
                self.environment.events.request.fire(
                    request_type="GET",
                    name=self.environment.parsed_options.my_str_argument,
                    response_time=self.environment.parsed_options.my_int_argument,
                    response_length=666,
                    exception=None,
                    context={},
                )

        @locust.events.init_command_line_parser.add_listener
        def _(parser, **kw):
            parser.add_argument("--my-int-argument", type=int)
            parser.add_argument("--my-str-argument", type=str, default="NOOOO")

        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
            # start a Master runner
            master_env = Environment(user_classes=[TestUser])
            master = master_env.create_master_runner("*", 0)
            master_env.parsed_options = parse_options(
                [
                    "--my-int-argument",
                    "42",
                    "--my-str-argument",
                    "cool-string",
                ]
            )
            sleep(0)
            # start 3 Worker runners
            workers = []
            for i in range(3):
                worker_env = Environment(user_classes=[TestUser])
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            # give workers time to connect
            sleep(0.1)
            # issue start command that should trigger TestUsers to be spawned in the Workers
            master.start(6, spawn_rate=1000)
            sleep(0.1)
            # check that worker nodes have started locusts
            for worker in workers:
                self.assertEqual(2, worker.user_count)
            # give time for users to generate stats, and stats to be sent to master
            sleep(1)
            master.quit()
            # make sure users are killed
            for worker in workers:
                self.assertEqual(0, worker.user_count)

        self.assertEqual(master_env.runner.stats.total.max_response_time, 42)
        self.assertEqual(master_env.runner.stats.get("cool-string", "GET").avg_response_time, 42)

    def test_test_stop_event(self):
        class TestUser(User):
            wait_time = constant(0.1)

            @task
            def my_task(l):
                pass

        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
            # start a Master runner
            master_env = Environment(user_classes=[TestUser])
            test_stop_count = {"master": 0, "worker": 0}

            @master_env.events.test_stop.add_listener
            def _(*args, **kwargs):
                test_stop_count["master"] += 1

            master = master_env.create_master_runner("*", 0)
            sleep(0)
            # start a Worker runner
            worker_env = Environment(user_classes=[TestUser])

            @worker_env.events.test_stop.add_listener
            def _(*args, **kwargs):
                test_stop_count["worker"] += 1

            worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)

            # give worker time to connect
            sleep(0.1)
            # issue start command that should trigger TestUsers to be spawned in the Workers
            master.start(2, spawn_rate=1000)
            sleep(0.1)
            # check that worker nodes have started locusts
            self.assertEqual(2, worker.user_count)
            # give time for users to generate stats, and stats to be sent to master
            sleep(0.1)
            master_env.events.quitting.fire(environment=master_env, reverse=True)
            master.quit()
            sleep(0.1)
            # make sure users are killed
            self.assertEqual(0, worker.user_count)

        # check the test_stop event was called one time in master and one time in worker
        self.assertEqual(
            1,
            test_stop_count["master"],
            "The test_stop event was not called exactly one time in the master node",
        )
        self.assertEqual(
            1,
            test_stop_count["worker"],
            "The test_stop event was not called exactly one time in the worker node",
        )

    def test_distributed_shape(self):
        """
        Full integration test that starts both a MasterRunner and three WorkerRunner instances
        and tests a basic LoadTestShape with scaling up and down users
        """

        class TestUser(User):
            @task
            def my_task(self):
                pass

        class TestShape(LoadTestShape):
            def tick(self):
                run_time = self.get_run_time()
                if run_time < 2:
                    return 9, 9
                elif run_time < 4:
                    return 21, 21
                elif run_time < 6:
                    return 3, 21
                else:
                    return None

        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
            test_shape = TestShape()
            master_env = Environment(user_classes=[TestUser], shape_class=test_shape)
            master_env.shape_class.reset_time()
            master = master_env.create_master_runner("*", 0)

            workers = []
            for i in range(3):
                worker_env = Environment(user_classes=[TestUser])
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            # Give workers time to connect
            sleep(0.1)

            # Start a shape test
            master.start_shape()
            sleep(1)

            # Ensure workers have connected and started the correct amount of users
            for worker in workers:
                self.assertEqual(3, worker.user_count, "Shape test has not reached stage 1")
                self.assertEqual(
                    9, test_shape.get_current_user_count(), "Shape is not seeing stage 1 runner user count correctly"
                )
            self.assertDictEqual(master.reported_user_classes_count, {"TestUser": 9})

            # Ensure new stage with more users has been reached
            sleep(2)
            for worker in workers:
                self.assertEqual(7, worker.user_count, "Shape test has not reached stage 2")
                self.assertEqual(
                    21, test_shape.get_current_user_count(), "Shape is not seeing stage 2 runner user count correctly"
                )
            self.assertDictEqual(master.reported_user_classes_count, {"TestUser": 21})

            # Ensure new stage with less users has been reached
            sleep(2)
            for worker in workers:
                self.assertEqual(1, worker.user_count, "Shape test has not reached stage 3")
                self.assertEqual(
                    3, test_shape.get_current_user_count(), "Shape is not seeing stage 3 runner user count correctly"
                )
            self.assertDictEqual(master.reported_user_classes_count, {"TestUser": 3})

            # Ensure test stops at the end
            sleep(2)
            for worker in workers:
                self.assertEqual(0, worker.user_count, "Shape test has not stopped")
                self.assertEqual(
                    0, test_shape.get_current_user_count(), "Shape is not seeing stopped runner user count correctly"
                )
            self.assertDictEqual(master.reported_user_classes_count, {"TestUser": 0})

            self.assertEqual("stopped", master.state)

    def test_distributed_shape_with_stop_timeout(self):
        """
        Full integration test that starts both a MasterRunner and five WorkerRunner instances
        and tests a basic LoadTestShape with scaling up and down users
        """

        class TestUser1(User):
            def start(self, group: Group):
                gevent.sleep(0.5)
                return super().start(group)

            @task
            def my_task(self):
                gevent.sleep(0)

        class TestUser2(User):
            def start(self, group: Group):
                gevent.sleep(0.5)
                return super().start(group)

            @task
            def my_task(self):
                gevent.sleep(600)

        class TestUser3(User):
            def start(self, group: Group):
                gevent.sleep(0.5)
                return super().start(group)

            @task
            def my_task(self):
                gevent.sleep(600)

        class TestShape(LoadTestShape):
            def tick(self):
                run_time = self.get_run_time()
                if run_time < 10:
                    return 15, 3
                elif run_time < 30:
                    return 5, 10
                else:
                    return None

        locust_worker_additional_wait_before_ready_after_stop = 5
        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3), _patch_env(
            "LOCUST_WORKER_ADDITIONAL_WAIT_BEFORE_READY_AFTER_STOP",
            str(locust_worker_additional_wait_before_ready_after_stop),
        ):
            stop_timeout = 5
            master_env = Environment(
                user_classes=[TestUser1, TestUser2, TestUser3], shape_class=TestShape(), stop_timeout=stop_timeout
            )
            master_env.shape_class.reset_time()
            master = master_env.create_master_runner("*", 0)

            workers = []
            for i in range(5):
                worker_env = Environment(user_classes=[TestUser1, TestUser2, TestUser3])
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            # Give workers time to connect
            sleep(0.1)

            self.assertEqual(STATE_INIT, master.state)
            self.assertEqual(5, len(master.clients.ready))

            # Re-order `workers` so that it is sorted by `id`.
            # This is required because the dispatch is done
            # on the sorted workers.
            workers = sorted(workers, key=lambda w: w.client_id)

            # Start a shape test
            master.start_shape()

            # First stage
            ts = time.time()
            while master.state != STATE_SPAWNING:
                self.assertTrue(time.time() - ts <= 1, master.state)
                sleep()
            sleep(5 - (time.time() - ts))  # runtime = 5s
            ts = time.time()
            while master.state != STATE_RUNNING:
                self.assertTrue(time.time() - ts <= 1, master.state)
                sleep()
            self.assertEqual(STATE_RUNNING, master.state)
            w1 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w2 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w3 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w4 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w5 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            self.assertDictEqual(w1, workers[0].user_classes_count)
            self.assertDictEqual(w2, workers[1].user_classes_count)
            self.assertDictEqual(w3, workers[2].user_classes_count)
            self.assertDictEqual(w4, workers[3].user_classes_count)
            self.assertDictEqual(w5, workers[4].user_classes_count)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_classes_count)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_classes_count)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_classes_count)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_classes_count)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_classes_count)
            sleep(5 - (time.time() - ts))  # runtime = 10s

            # Fourth stage
            ts = time.time()
            while master.state != STATE_SPAWNING:
                self.assertTrue(time.time() - ts <= 1, master.state)
                sleep()
            sleep(5 - (time.time() - ts))  # runtime = 15s

            # Fourth stage - Excess TestUser1 have been stopped but
            #                TestUser2/TestUser3 have not reached stop timeout yet, so
            #                their number are unchanged
            ts = time.time()
            while master.state != STATE_RUNNING:
                self.assertTrue(time.time() - ts <= 1, master.state)
                sleep()
            delta = time.time() - ts
            w1 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w2 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 1}
            w3 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 1}
            w4 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w5 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 1}
            self.assertDictEqual(w1, workers[0].user_classes_count)
            self.assertDictEqual(w2, workers[1].user_classes_count)
            self.assertDictEqual(w3, workers[2].user_classes_count)
            self.assertDictEqual(w4, workers[3].user_classes_count)
            self.assertDictEqual(w5, workers[4].user_classes_count)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_classes_count)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_classes_count)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_classes_count)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_classes_count)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_classes_count)
            sleep(1 - delta)  # runtime = 16s

            # Fourth stage - All users are now at the desired number
            ts = time.time()
            while master.state != STATE_RUNNING:
                self.assertTrue(time.time() - ts <= 1, master.state)
                sleep()
            delta = time.time() - ts
            w1 = {"TestUser1": 1, "TestUser2": 0, "TestUser3": 0}
            w2 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 0}
            w3 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 1}
            w4 = {"TestUser1": 1, "TestUser2": 0, "TestUser3": 0}
            w5 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 0}
            self.assertDictEqual(w1, workers[0].user_classes_count)
            self.assertDictEqual(w2, workers[1].user_classes_count)
            self.assertDictEqual(w3, workers[2].user_classes_count)
            self.assertDictEqual(w4, workers[3].user_classes_count)
            self.assertDictEqual(w5, workers[4].user_classes_count)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_classes_count)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_classes_count)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_classes_count)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_classes_count)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_classes_count)
            sleep(10 - delta)  # runtime = 26s

            # Sleep stop_timeout and make sure the test has stopped
            sleep(5)  # runtime = 31s
            self.assertEqual(STATE_STOPPING, master.state)
            sleep(stop_timeout)  # runtime = 36s

            # We wait for "stop_timeout" seconds to let the workers reconnect as "ready" with the master.
            # The reason for waiting an additional "stop_timeout" when we already waited for "stop_timeout"
            # above is that when a worker receives the stop message, it can take up to "stop_timeout"
            # for the worker to send the "client_stopped" message then an additional "stop_timeout" seconds
            # to send the "client_ready" message.
            ts = time.time()
            while len(master.clients.ready) != len(workers):
                self.assertTrue(
                    time.time() - ts <= stop_timeout + locust_worker_additional_wait_before_ready_after_stop,
                    f"expected {len(workers)} workers to be ready but only {len(master.clients.ready)} workers are",
                )
                sleep()
            sleep(1)

            # Check that no users are running
            w1 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 0}
            w2 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 0}
            w3 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 0}
            w4 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 0}
            w5 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 0}
            self.assertDictEqual(w1, workers[0].user_classes_count)
            self.assertDictEqual(w2, workers[1].user_classes_count)
            self.assertDictEqual(w3, workers[2].user_classes_count)
            self.assertDictEqual(w4, workers[3].user_classes_count)
            self.assertDictEqual(w5, workers[4].user_classes_count)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_classes_count)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_classes_count)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_classes_count)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_classes_count)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_classes_count)

            ts = time.time()
            while master.state != STATE_STOPPED:
                self.assertTrue(time.time() - ts <= 5, master.state)
                sleep()

            master.stop()

    @unittest.skip
    def test_distributed_shape_fuzzy_test(self):
        """
        Incredibility useful test to find issues with dispatch logic. This test allowed to find
        multiple small corner cases with the new dispatch logic of locust v2.

        The test is disabled by default because it takes a lot of time to run and has randomness to it.
        However, it is advised to run it a few times (you can run it in parallel) when modifying the dispatch logic.
        """

        class BaseUser(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        class TestUser01(BaseUser):
            pass

        class TestUser02(BaseUser):
            pass

        class TestUser03(BaseUser):
            pass

        class TestUser04(BaseUser):
            pass

        class TestUser05(BaseUser):
            pass

        class TestUser06(BaseUser):
            pass

        class TestUser07(BaseUser):
            pass

        class TestUser08(BaseUser):
            pass

        class TestUser09(BaseUser):
            pass

        class TestUser10(BaseUser):
            pass

        class TestUser11(BaseUser):
            pass

        class TestUser12(BaseUser):
            pass

        class TestUser13(BaseUser):
            pass

        class TestUser14(BaseUser):
            pass

        class TestUser15(BaseUser):
            pass

        class TestShape(LoadTestShape):
            def __init__(self):
                super().__init__()

                self.stages = []
                runtime = 0
                for _ in range(100):
                    runtime += random.uniform(3, 15)
                    self.stages.append((runtime, random.randint(1, 100), random.uniform(0.1, 10)))

            def tick(self):
                run_time = self.get_run_time()
                for stage in self.stages:
                    if run_time < stage[0]:
                        return stage[1], stage[2]

        user_classes = [
            TestUser01,
            TestUser02,
            TestUser03,
            TestUser04,
            TestUser05,
            TestUser06,
            TestUser07,
            TestUser08,
            TestUser09,
            TestUser10,
            TestUser11,
            TestUser12,
            TestUser13,
            TestUser14,
            TestUser15,
        ]

        chosen_user_classes = random.sample(user_classes, k=random.randint(1, len(user_classes)))

        for user_class in chosen_user_classes:
            user_class.weight = random.uniform(1, 20)

        locust_worker_additional_wait_before_ready_after_stop = 5
        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3), _patch_env(
            "LOCUST_WORKER_ADDITIONAL_WAIT_BEFORE_READY_AFTER_STOP",
            str(locust_worker_additional_wait_before_ready_after_stop),
        ):
            stop_timeout = 5
            master_env = Environment(
                user_classes=chosen_user_classes, shape_class=TestShape(), stop_timeout=stop_timeout
            )
            master_env.shape_class.reset_time()
            master = master_env.create_master_runner("*", 0)

            workers = []
            for i in range(random.randint(1, 30)):
                worker_env = Environment(user_classes=chosen_user_classes)
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            # Give workers time to connect
            sleep(0.1)

            self.assertEqual(STATE_INIT, master.state)
            self.assertEqual(len(workers), len(master.clients.ready))

            # Start a shape test
            master.start_shape()

            ts = time.time()
            while master.state != STATE_STOPPED:
                self.assertTrue(time.time() - ts <= master_env.shape_class.stages[-1][0] + 60, master.state)
                print(
                    "{:.2f}/{:.2f} | {} | {:.0f} | ".format(
                        time.time() - ts,
                        master_env.shape_class.stages[-1][0],
                        master.state,
                        sum(master.reported_user_classes_count.values()),
                    )
                    + json.dumps(dict(sorted(master.reported_user_classes_count.items(), key=itemgetter(0))))
                )
                sleep(1)

            master.stop()

    def test_distributed_shape_stop_and_restart(self):
        """
        Test stopping and then restarting a LoadTestShape
        """

        class TestUser(User):
            @task
            def my_task(self):
                pass

        class TestShape(LoadTestShape):
            def tick(self):
                run_time = self.get_run_time()
                if run_time < 10:
                    return 4, 4
                else:
                    return None

        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
            master_env = Environment(user_classes=[TestUser], shape_class=TestShape())
            master_env.shape_class.reset_time()
            master = master_env.create_master_runner("*", 0)

            workers = []
            for i in range(2):
                worker_env = Environment(user_classes=[TestUser])
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            # Give workers time to connect
            sleep(0.1)

            # Start a shape test and ensure workers have connected and started the correct amount of users
            master.start_shape()
            sleep(1)
            for worker in workers:
                self.assertEqual(2, worker.user_count, "Shape test has not started correctly")

            # Stop the test and ensure all user count is 0
            master.stop()
            sleep(1)
            for worker in workers:
                self.assertEqual(0, worker.user_count, "Shape test has not stopped")

            # Then restart the test again and ensure workers have connected and started the correct amount of users
            master.start_shape()
            sleep(1)
            for worker in workers:
                self.assertEqual(2, worker.user_count, "Shape test has not started again correctly")
            master.stop()

    def test_distributed_shape_statuses_transition(self):
        """
        Full integration test that starts both a MasterRunner and five WorkerRunner instances
        The goal of this test is to validate the status on the master is correctly transitioned for each of the
        test phases.
        """

        class TestUser1(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        class TestShape(LoadTestShape):
            def tick(self):
                run_time = self.get_run_time()
                if run_time < 5:
                    return 5, 2.5
                elif run_time < 10:
                    return 10, 2.5
                elif run_time < 15:
                    return 15, 2.5
                else:
                    return None

        locust_worker_additional_wait_before_ready_after_stop = 2
        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3), _patch_env(
            "LOCUST_WORKER_ADDITIONAL_WAIT_BEFORE_READY_AFTER_STOP",
            str(locust_worker_additional_wait_before_ready_after_stop),
        ):
            stop_timeout = 0
            master_env = Environment(user_classes=[TestUser1], shape_class=TestShape(), stop_timeout=stop_timeout)
            master_env.shape_class.reset_time()
            master = master_env.create_master_runner("*", 0)

            workers = []
            for i in range(5):
                worker_env = Environment(user_classes=[TestUser1])
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            # Give workers time to connect
            sleep(0.1)

            self.assertEqual(STATE_INIT, master.state)
            self.assertEqual(5, len(master.clients.ready))

            statuses = []

            ts = time.perf_counter()

            master.start_shape()

            while master.state != STATE_STOPPED:
                # +5s buffer to let master stop
                self.assertTrue(
                    time.perf_counter() - ts <= 30 + locust_worker_additional_wait_before_ready_after_stop + 5,
                    master.state,
                )
                statuses.append((time.perf_counter() - ts, master.state, master.user_count))
                sleep(0.1)

            self.assertEqual(statuses[0][1], STATE_INIT)

            stage = 1
            tolerance = 1  # in s
            for (t1, state1, user_count1), (t2, state2, user_count2) in zip(statuses[:-1], statuses[1:]):
                if state1 == STATE_SPAWNING and state2 == STATE_RUNNING and stage == 1:
                    self.assertTrue(2.5 - tolerance <= t2 <= 2.5 + tolerance)
                elif state1 == STATE_RUNNING and state2 == STATE_SPAWNING and stage == 1:
                    self.assertTrue(5 - tolerance <= t2 <= 5 + tolerance)
                    stage += 1
                elif state1 == STATE_SPAWNING and state2 == STATE_RUNNING and stage == 2:
                    self.assertTrue(7.5 - tolerance <= t2 <= 7.5 + tolerance)
                elif state1 == STATE_RUNNING and state2 == STATE_SPAWNING and stage == 2:
                    self.assertTrue(10 - tolerance <= t2 <= 10 + tolerance)
                    stage += 1
                elif state1 == STATE_SPAWNING and state2 == STATE_RUNNING and stage == 3:
                    self.assertTrue(12.5 - tolerance <= t2 <= 12.5 + tolerance)
                elif state1 == STATE_RUNNING and state2 == STATE_SPAWNING and stage == 3:
                    self.assertTrue(15 - tolerance <= t2 <= 15 + tolerance)
                    stage += 1
                elif state1 == STATE_RUNNING and state2 == STATE_STOPPED and stage == 3:
                    self.assertTrue(15 - tolerance <= t2 <= 15 + tolerance)

    def test_swarm_endpoint_is_non_blocking(self):
        class TestUser1(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        class TestUser2(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
            stop_timeout = 0
            master_env = Environment(user_classes=[TestUser1, TestUser2], stop_timeout=stop_timeout)
            master = master_env.create_master_runner("*", 0)
            web_ui = master_env.create_web_ui("127.0.0.1", 0)

            workers = []
            for i in range(2):
                worker_env = Environment(user_classes=[TestUser1, TestUser2])
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            # Give workers time to connect
            sleep(0.1)

            self.assertEqual(STATE_INIT, master.state)
            self.assertEqual(len(master.clients.ready), len(workers))

            ts = time.perf_counter()
            response = requests.post(
                "http://127.0.0.1:{}/swarm".format(web_ui.server.server_port),
                data={"user_count": 20, "spawn_rate": 5, "host": "https://localhost"},
            )
            self.assertEqual(200, response.status_code)
            self.assertTrue(0 <= time.perf_counter() - ts <= 1, "swarm endpoint is blocking")

            ts = time.perf_counter()
            while master.state != STATE_RUNNING:
                self.assertTrue(time.perf_counter() - ts <= 4, master.state)
                gevent.sleep(0.1)

            self.assertTrue(3 <= time.perf_counter() - ts <= 5)

            self.assertEqual(master.user_count, 20)

            master.stop()
            web_ui.stop()

    def test_can_call_stop_endpoint_if_currently_swarming(self):
        class TestUser1(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        class TestUser2(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
            stop_timeout = 5
            master_env = Environment(user_classes=[TestUser1, TestUser2], stop_timeout=stop_timeout)
            master = master_env.create_master_runner("*", 0)
            web_ui = master_env.create_web_ui("127.0.0.1", 0)

            workers = []
            for i in range(2):
                worker_env = Environment(user_classes=[TestUser1, TestUser2])
                worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)
                workers.append(worker)

            # Give workers time to connect
            sleep(0.1)

            self.assertEqual(STATE_INIT, master.state)
            self.assertEqual(len(master.clients.ready), len(workers))

            ts = time.perf_counter()
            response = requests.post(
                "http://127.0.0.1:{}/swarm".format(web_ui.server.server_port),
                data={"user_count": 20, "spawn_rate": 1, "host": "https://localhost"},
            )
            self.assertEqual(200, response.status_code)
            self.assertTrue(0 <= time.perf_counter() - ts <= 1, "swarm endpoint is blocking")

            gevent.sleep(5)

            self.assertEqual(master.state, STATE_SPAWNING)
            self.assertLessEqual(master.user_count, 10)

            ts = time.perf_counter()
            response = requests.get(
                "http://127.0.0.1:{}/stop".format(web_ui.server.server_port),
            )
            self.assertEqual(200, response.status_code)
            self.assertTrue(stop_timeout <= time.perf_counter() - ts <= stop_timeout + 5, "stop endpoint took too long")

            ts = time.perf_counter()
            while master.state != STATE_STOPPED:
                self.assertTrue(time.perf_counter() - ts <= 2)
                gevent.sleep(0.1)

            self.assertLessEqual(master.user_count, 0)

            master.stop()
            web_ui.stop()

    def test_target_user_count_is_set_before_ramp_up(self):
        """Test for https://github.com/locustio/locust/issues/1883"""

        class MyUser1(User):
            wait_time = constant(0)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
            # start a Master runner
            master_env = Environment(user_classes=[MyUser1])
            master = master_env.create_master_runner("*", 0)

            test_start_event_fired = [False]

            @master_env.events.test_start.add_listener
            def on_test_start(*args, **kwargs):
                test_start_event_fired[0] = True
                self.assertEqual(master.target_user_count, 3)

            sleep(0)

            # start 1 worker runner
            worker_env = Environment(user_classes=[MyUser1])
            worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)

            # give worker time to connect
            sleep(0.1)

            gevent.spawn(master.start, 3, spawn_rate=1)

            sleep(1)

            self.assertEqual(master.target_user_count, 3)
            self.assertEqual(master.user_count, 1)
            # However, target_user_classes_count is only updated at the end of the ramp-up/ramp-down
            # due to the way it is implemented.
            self.assertDictEqual({}, master.target_user_classes_count)

            sleep(2)

            self.assertEqual(master.target_user_count, 3)
            self.assertEqual(master.user_count, 3)
            self.assertDictEqual({"MyUser1": 3}, master.target_user_classes_count)

            master.quit()

            # make sure users are killed
            self.assertEqual(0, worker.user_count)

            self.assertTrue(test_start_event_fired[0])


class TestMasterRunner(LocustTestCase):
    def setUp(self):
        super().setUp()
        self.environment = Environment(events=locust.events, catch_exceptions=False)

    def tearDown(self):
        super().tearDown()

    def get_runner(self, user_classes=None):
        if user_classes is not None:
            self.environment.user_classes = user_classes
        return self.environment.create_master_runner("*", 5557)

    def test_worker_connect(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", __version__, "zeh_fake_client1"))
            self.assertEqual(1, len(master.clients))
            self.assertTrue(
                "zeh_fake_client1" in master.clients, "Could not find fake client in master instance's clients dict"
            )
            server.mocked_send(Message("client_ready", __version__, "zeh_fake_client2"))
            server.mocked_send(Message("client_ready", __version__, "zeh_fake_client3"))
            server.mocked_send(Message("client_ready", __version__, "zeh_fake_client4"))
            self.assertEqual(4, len(master.clients))

            server.mocked_send(Message("quit", None, "zeh_fake_client3"))
            self.assertEqual(3, len(master.clients))

    def test_worker_connect_with_special_versions(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", None, "1.x_style_client_should_not_be_allowed"))
            self.assertEqual(1, len(self.mocked_log.error))
            self.assertEqual(0, len(master.clients))
            server.mocked_send(Message("client_ready", "abcd", "other_version_mismatch_should_just_give_a_warning"))
            self.assertEqual(1, len(self.mocked_log.warning))
            self.assertEqual(1, len(master.clients))
            server.mocked_send(Message("client_ready", -1, "version_check_bypass_should_not_warn"))
            self.assertEqual(1, len(self.mocked_log.warning))
            self.assertEqual(2, len(master.clients))
            server.mocked_send(
                Message("client_ready", __version__ + "1", "difference_in_patch_version_should_not_warn")
            )
            self.assertEqual(3, len(master.clients))
            self.assertEqual(1, len(self.mocked_log.warning))

    def test_worker_stats_report_median(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", __version__, "fake_client"))

            master.stats.get("/", "GET").log(100, 23455)
            master.stats.get("/", "GET").log(800, 23455)
            master.stats.get("/", "GET").log(700, 23455)

            data = {"user_count": 1}
            self.environment.events.report_to_master.fire(client_id="fake_client", data=data)
            master.stats.clear_all()

            server.mocked_send(Message("stats", data, "fake_client"))
            s = master.stats.get("/", "GET")
            self.assertEqual(700, s.median_response_time)

    def test_worker_stats_report_with_none_response_times(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", __version__, "fake_client"))

            master.stats.get("/mixed", "GET").log(0, 23455)
            master.stats.get("/mixed", "GET").log(800, 23455)
            master.stats.get("/mixed", "GET").log(700, 23455)
            master.stats.get("/mixed", "GET").log(None, 23455)
            master.stats.get("/mixed", "GET").log(None, 23455)
            master.stats.get("/mixed", "GET").log(None, 23455)
            master.stats.get("/mixed", "GET").log(None, 23455)
            master.stats.get("/onlyNone", "GET").log(None, 23455)

            data = {"user_count": 1}
            self.environment.events.report_to_master.fire(client_id="fake_client", data=data)
            master.stats.clear_all()

            server.mocked_send(Message("stats", data, "fake_client"))
            s1 = master.stats.get("/mixed", "GET")
            self.assertEqual(700, s1.median_response_time)
            self.assertEqual(500, s1.avg_response_time)
            s2 = master.stats.get("/onlyNone", "GET")
            self.assertEqual(0, s2.median_response_time)
            self.assertEqual(0, s2.avg_response_time)

    def test_master_marks_downed_workers_as_missing(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", __version__, "fake_client"))
            sleep(6)
            # print(master.clients['fake_client'].__dict__)
            assert master.clients["fake_client"].state == STATE_MISSING

    def test_last_worker_quitting_stops_test(self):
        class TestUser(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])
            server.mocked_send(Message("client_ready", __version__, "fake_client1"))
            server.mocked_send(Message("client_ready", __version__, "fake_client2"))

            master.start(1, 2)
            server.mocked_send(Message("spawning", None, "fake_client1"))
            server.mocked_send(Message("spawning", None, "fake_client2"))

            server.mocked_send(Message("quit", None, "fake_client1"))
            sleep(0.1)
            self.assertEqual(1, len(master.clients.all))
            self.assertNotEqual(STATE_STOPPED, master.state, "Not all workers quit but test stopped anyway.")

            server.mocked_send(Message("quit", None, "fake_client2"))
            sleep(0.1)
            self.assertEqual(0, len(master.clients.all))
            self.assertEqual(STATE_STOPPED, master.state, "All workers quit but test didn't stop.")

    @mock.patch("locust.runners.HEARTBEAT_INTERVAL", new=0.1)
    def test_last_worker_missing_stops_test(self):
        class TestUser(User):
            @task
            def my_task(self):
                gevent.sleep(600)

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])
            server.mocked_send(Message("client_ready", __version__, "fake_client1"))
            server.mocked_send(Message("client_ready", __version__, "fake_client2"))
            server.mocked_send(Message("client_ready", __version__, "fake_client3"))

            master.start(3, 3)
            server.mocked_send(Message("spawning", None, "fake_client1"))
            server.mocked_send(Message("spawning", None, "fake_client2"))
            server.mocked_send(Message("spawning", None, "fake_client3"))

            sleep(0.2)
            server.mocked_send(
                Message(
                    "heartbeat",
                    {"state": STATE_RUNNING, "current_cpu_usage": 50, "current_memory_usage": 200, "count": 1},
                    "fake_client1",
                )
            )
            server.mocked_send(
                Message(
                    "heartbeat",
                    {"state": STATE_RUNNING, "current_cpu_usage": 50, "current_memory_usage": 200, "count": 1},
                    "fake_client2",
                )
            )
            server.mocked_send(
                Message(
                    "heartbeat",
                    {"state": STATE_RUNNING, "current_cpu_usage": 50, "current_memory_usage": 200, "count": 1},
                    "fake_client3",
                )
            )

            sleep(0.2)
            self.assertEqual(0, len(master.clients.missing))
            self.assertEqual(3, master.worker_count)
            self.assertNotIn(
                master.state, [STATE_STOPPED, STATE_STOPPING], "Not all workers went missing but test stopped anyway."
            )

            server.mocked_send(
                Message(
                    "heartbeat",
                    {"state": STATE_RUNNING, "current_cpu_usage": 50, "current_memory_usage": 200, "count": 1},
                    "fake_client1",
                )
            )

            sleep(0.4)
            self.assertEqual(2, len(master.clients.missing))
            self.assertEqual(1, master.worker_count)
            self.assertNotIn(
                master.state, [STATE_STOPPED, STATE_STOPPING], "Not all workers went missing but test stopped anyway."
            )

            sleep(0.2)
            self.assertEqual(3, len(master.clients.missing))
            self.assertEqual(0, master.worker_count)
            self.assertEqual(STATE_STOPPED, master.state, "All workers went missing but test didn't stop.")

    def test_master_total_stats(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", __version__, "fake_client"))
            stats = RequestStats()
            stats.log_request("GET", "/1", 100, 3546)
            stats.log_request("GET", "/1", 800, 56743)
            stats2 = RequestStats()
            stats2.log_request("GET", "/2", 700, 2201)
            server.mocked_send(
                Message(
                    "stats",
                    {
                        "stats": stats.serialize_stats(),
                        "stats_total": stats.total.serialize(),
                        "errors": stats.serialize_errors(),
                        "user_count": 1,
                    },
                    "fake_client",
                )
            )
            server.mocked_send(
                Message(
                    "stats",
                    {
                        "stats": stats2.serialize_stats(),
                        "stats_total": stats2.total.serialize(),
                        "errors": stats2.serialize_errors(),
                        "user_count": 2,
                    },
                    "fake_client",
                )
            )
            self.assertEqual(700, master.stats.total.median_response_time)

    def test_master_total_stats_with_none_response_times(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", __version__, "fake_client"))
            stats = RequestStats()
            stats.log_request("GET", "/1", 100, 3546)
            stats.log_request("GET", "/1", 800, 56743)
            stats.log_request("GET", "/1", None, 56743)
            stats2 = RequestStats()
            stats2.log_request("GET", "/2", 700, 2201)
            stats2.log_request("GET", "/2", None, 2201)
            stats3 = RequestStats()
            stats3.log_request("GET", "/3", None, 2201)
            server.mocked_send(
                Message(
                    "stats",
                    {
                        "stats": stats.serialize_stats(),
                        "stats_total": stats.total.serialize(),
                        "errors": stats.serialize_errors(),
                        "user_count": 1,
                    },
                    "fake_client",
                )
            )
            server.mocked_send(
                Message(
                    "stats",
                    {
                        "stats": stats2.serialize_stats(),
                        "stats_total": stats2.total.serialize(),
                        "errors": stats2.serialize_errors(),
                        "user_count": 2,
                    },
                    "fake_client",
                )
            )
            server.mocked_send(
                Message(
                    "stats",
                    {
                        "stats": stats3.serialize_stats(),
                        "stats_total": stats3.total.serialize(),
                        "errors": stats3.serialize_errors(),
                        "user_count": 2,
                    },
                    "fake_client",
                )
            )
            self.assertEqual(700, master.stats.total.median_response_time)

    def test_master_current_response_times(self):
        start_time = 1
        with mock.patch("time.time") as mocked_time:
            mocked_time.return_value = start_time
            with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
                master = self.get_runner()
                self.environment.stats.reset_all()
                mocked_time.return_value += 1.0234
                server.mocked_send(Message("client_ready", __version__, "fake_client"))
                stats = RequestStats()
                stats.log_request("GET", "/1", 100, 3546)
                stats.log_request("GET", "/1", 800, 56743)
                server.mocked_send(
                    Message(
                        "stats",
                        {
                            "stats": stats.serialize_stats(),
                            "stats_total": stats.total.get_stripped_report(),
                            "errors": stats.serialize_errors(),
                            "user_count": 1,
                        },
                        "fake_client",
                    )
                )
                mocked_time.return_value += 1
                stats2 = RequestStats()
                stats2.log_request("GET", "/2", 400, 2201)
                server.mocked_send(
                    Message(
                        "stats",
                        {
                            "stats": stats2.serialize_stats(),
                            "stats_total": stats2.total.get_stripped_report(),
                            "errors": stats2.serialize_errors(),
                            "user_count": 2,
                        },
                        "fake_client",
                    )
                )
                mocked_time.return_value += 4
                self.assertEqual(400, master.stats.total.get_current_response_time_percentile(0.5))
                self.assertEqual(800, master.stats.total.get_current_response_time_percentile(0.95))

                # let 10 second pass, do some more requests, send it to the master and make
                # sure the current response time percentiles only accounts for these new requests
                mocked_time.return_value += 10.10023
                stats.log_request("GET", "/1", 20, 1)
                stats.log_request("GET", "/1", 30, 1)
                stats.log_request("GET", "/1", 3000, 1)
                server.mocked_send(
                    Message(
                        "stats",
                        {
                            "stats": stats.serialize_stats(),
                            "stats_total": stats.total.get_stripped_report(),
                            "errors": stats.serialize_errors(),
                            "user_count": 2,
                        },
                        "fake_client",
                    )
                )
                self.assertEqual(30, master.stats.total.get_current_response_time_percentile(0.5))
                self.assertEqual(3000, master.stats.total.get_current_response_time_percentile(0.95))

    @mock.patch("locust.runners.HEARTBEAT_INTERVAL", new=600)
    def test_rebalance_locust_users_on_worker_connect(self):
        class TestUser(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])
            server.mocked_send(Message("client_ready", __version__, "zeh_fake_client1"))
            self.assertEqual(1, len(master.clients))
            self.assertTrue(
                "zeh_fake_client1" in master.clients, "Could not find fake client in master instance's clients dict"
            )

            master.start(100, 20)
            self.assertEqual(5, len(server.outbox))
            for i, (_, msg) in enumerate(server.outbox.copy()):
                self.assertDictEqual({"TestUser": int((i + 1) * 20)}, msg.data["user_classes_count"])
                server.outbox.pop()

            # Normally, this attribute would be updated when the
            # master receives the report from the worker.
            master.clients["zeh_fake_client1"].user_classes_count = {"TestUser": 100}

            # let another worker connect
            server.mocked_send(Message("client_ready", __version__, "zeh_fake_client2"))
            self.assertEqual(2, len(master.clients))
            sleep(0.1)  # give time for messages to be sent to clients
            self.assertEqual(2, len(server.outbox))
            client_id, msg = server.outbox.pop()
            self.assertEqual({"TestUser": 50}, msg.data["user_classes_count"])
            client_id, msg = server.outbox.pop()
            self.assertEqual({"TestUser": 50}, msg.data["user_classes_count"])

    def test_sends_spawn_data_to_ready_running_spawning_workers(self):
        """Sends spawn job to running, ready, or spawning workers"""

        class TestUser(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])
            master.clients[1] = WorkerNode("1")
            master.clients[2] = WorkerNode("2")
            master.clients[3] = WorkerNode("3")
            master.clients[1].state = STATE_INIT
            master.clients[2].state = STATE_SPAWNING
            master.clients[3].state = STATE_RUNNING
            master.start(user_count=5, spawn_rate=5)

            self.assertEqual(3, len(server.outbox))

    def test_start_event(self):
        """
        Tests that test_start event is fired
        """

        class TestUser(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])

            run_count = [0]

            @self.environment.events.test_start.add_listener
            def on_test_start(*a, **kw):
                run_count[0] += 1

            for i in range(5):
                server.mocked_send(Message("client_ready", __version__, "fake_client%i" % i))

            master.start(7, 7)
            self.assertEqual(5, len(server.outbox))
            self.assertEqual(1, run_count[0])

            # change number of users and check that test_start isn't fired again
            master.start(7, 7)
            self.assertEqual(1, run_count[0])

            # stop and start to make sure test_start is fired again
            master.stop()
            master.start(3, 3)
            self.assertEqual(2, run_count[0])

            master.quit()

    def test_stop_event(self):
        """
        Tests that test_stop event is fired
        """

        class TestUser(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])

            run_count = [0]

            @self.environment.events.test_stop.add_listener
            def on_test_stop(*a, **kw):
                run_count[0] += 1

            for i in range(5):
                server.mocked_send(Message("client_ready", __version__, "fake_client%i" % i))

            master.start(7, 7)
            self.assertEqual(5, len(server.outbox))
            master.stop()
            self.assertEqual(1, run_count[0])

            run_count[0] = 0
            for i in range(5):
                server.mocked_send(Message("client_ready", __version__, "fake_client%i" % i))
            master.start(7, 7)
            master.stop()
            master.quit()
            self.assertEqual(1, run_count[0])

    def test_stop_event_quit(self):
        """
        Tests that test_stop event is fired when quit() is called directly
        """

        class TestUser(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])

            run_count = [0]

            @self.environment.events.test_stop.add_listener
            def on_test_stop(*a, **kw):
                run_count[0] += 1

            for i in range(5):
                server.mocked_send(Message("client_ready", __version__, "fake_client%i" % i))

            master.start(7, 7)
            self.assertEqual(5, len(server.outbox))
            master.quit()
            self.assertEqual(1, run_count[0])

    def test_spawn_zero_locusts(self):
        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                pass

        class MyTestUser(User):
            tasks = [MyTaskSet]
            wait_time = constant(0.1)

        environment = Environment(user_classes=[MyTestUser])
        runner = LocalRunner(environment)

        timeout = gevent.Timeout(2.0)
        timeout.start()

        try:
            runner.start(0, 1, wait=True)
            runner.spawning_greenlet.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception. A locust seems to have been spawned, even though 0 was specified.")
        finally:
            timeout.cancel()

    def test_spawn_uneven_locusts(self):
        """
        Tests that we can accurately spawn a certain number of locusts, even if it's not an
        even number of the connected workers
        """

        class TestUser(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])

            for i in range(5):
                server.mocked_send(Message("client_ready", __version__, "fake_client%i" % i))

            master.start(7, 7)
            self.assertEqual(5, len(server.outbox))

            num_users = sum(sum(msg.data["user_classes_count"].values()) for _, msg in server.outbox if msg.data)

            self.assertEqual(7, num_users, "Total number of locusts that would have been spawned is not 7")

    def test_spawn_fewer_locusts_than_workers(self):
        class TestUser(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])

            for i in range(5):
                server.mocked_send(Message("client_ready", __version__, "fake_client%i" % i))

            master.start(2, 2)
            self.assertEqual(5, len(server.outbox))

            num_users = sum(sum(msg.data["user_classes_count"].values()) for _, msg in server.outbox if msg.data)

            self.assertEqual(2, num_users, "Total number of locusts that would have been spawned is not 2")

    def test_custom_shape_scale_up(self):
        class MyUser(User):
            @task
            def my_task(self):
                pass

        class TestShape(LoadTestShape):
            def tick(self):
                run_time = self.get_run_time()
                if run_time < 2:
                    return 1, 1
                elif run_time < 4:
                    return 2, 2
                else:
                    return None

        self.environment.shape_class = TestShape()

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[MyUser])
            for i in range(5):
                server.mocked_send(Message("client_ready", __version__, "fake_client%i" % i))

            # Start the shape_worker
            self.environment.shape_class.reset_time()
            master.start_shape()
            sleep(0.5)

            # Wait for shape_worker to update user_count
            num_users = sum(sum(msg.data["user_classes_count"].values()) for _, msg in server.outbox if msg.data)
            self.assertEqual(
                1, num_users, "Total number of users in first stage of shape test is not 1: %i" % num_users
            )

            # Wait for shape_worker to update user_count again
            sleep(2)
            num_users = sum(sum(msg.data["user_classes_count"].values()) for _, msg in server.outbox if msg.data)
            self.assertEqual(
                3, num_users, "Total number of users in second stage of shape test is not 3: %i" % num_users
            )

            # Wait to ensure shape_worker has stopped the test
            sleep(3)
            self.assertEqual("stopped", master.state, "The test has not been stopped by the shape class")

    def test_custom_shape_scale_down(self):
        class MyUser(User):
            @task
            def my_task(self):
                pass

        class TestShape(LoadTestShape):
            def tick(self):
                run_time = self.get_run_time()
                if run_time < 2:
                    return 5, 5
                elif run_time < 4:
                    return 1, 5
                else:
                    return None

        self.environment.shape_class = TestShape()

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[MyUser])
            for i in range(5):
                server.mocked_send(Message("client_ready", __version__, "fake_client%i" % i))

            # Start the shape_worker
            self.environment.shape_class.reset_time()
            master.start_shape()
            sleep(0.5)

            # Wait for shape_worker to update user_count
            num_users = sum(sum(msg.data["user_classes_count"].values()) for _, msg in server.outbox if msg.data)
            self.assertEqual(
                5, num_users, "Total number of users in first stage of shape test is not 5: %i" % num_users
            )

            # Wait for shape_worker to update user_count again
            sleep(2)
            msgs = defaultdict(dict)
            for _, msg in server.outbox:
                if not msg.data:
                    continue
                msgs[msg.node_id][msg.data["timestamp"]] = sum(msg.data["user_classes_count"].values())
            # Count users for the last received messages
            num_users = sum(v[max(v.keys())] for v in msgs.values())
            self.assertEqual(
                1, num_users, "Total number of users in second stage of shape test is not 1: %i" % num_users
            )

            # Wait to ensure shape_worker has stopped the test
            sleep(3)
            self.assertEqual("stopped", master.state, "The test has not been stopped by the shape class")

    def test_exception_in_task(self):
        class MyUser(User):
            @task
            def will_error(self):
                raise HeyAnException(":(")

        self.environment.user_classes = [MyUser]
        runner = self.environment.create_local_runner()

        l = MyUser(self.environment)

        self.assertRaises(HeyAnException, l.run)
        self.assertRaises(HeyAnException, l.run)
        self.assertEqual(1, len(runner.exceptions))

        hash_key, exception = runner.exceptions.popitem()
        self.assertTrue("traceback" in exception)
        self.assertTrue("HeyAnException" in exception["traceback"])
        self.assertEqual(2, exception["count"])

    def test_exception_is_caught(self):
        """Test that exceptions are stored, and execution continues"""

        class MyTaskSet(TaskSet):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                self._task_queue = [self.will_error, self.will_stop]

            @task(1)
            def will_error(self):
                raise HeyAnException(":(")

            @task(1)
            def will_stop(self):
                raise StopUser()

        class MyUser(User):
            wait_time = constant(0.01)
            tasks = [MyTaskSet]

        # set config to catch exceptions in locust users
        self.environment.catch_exceptions = True
        self.environment.user_classes = [MyUser]
        runner = LocalRunner(self.environment)
        l = MyUser(self.environment)

        # make sure HeyAnException isn't raised
        l.run()
        l.run()
        # make sure we got two entries in the error log
        self.assertEqual(2, len(self.mocked_log.error))

        # make sure exception was stored
        self.assertEqual(1, len(runner.exceptions))
        hash_key, exception = runner.exceptions.popitem()
        self.assertTrue("traceback" in exception)
        self.assertTrue("HeyAnException" in exception["traceback"])
        self.assertEqual(2, exception["count"])

    def test_master_reset_connection(self):
        """Test that connection will be reset when network issues found"""
        with mock.patch("locust.runners.FALLBACK_INTERVAL", new=0.1):
            with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
                master = self.get_runner()
                self.assertEqual(0, len(master.clients))
                server.mocked_send(Message("client_ready", NETWORK_BROKEN, "fake_client"))
                self.assertTrue(master.connection_broken)
                server.mocked_send(Message("client_ready", __version__, "fake_client"))
                sleep(0.2)
                self.assertFalse(master.connection_broken)
                self.assertEqual(1, len(master.clients))
                master.quit()

    def test_attributes_populated_when_calling_start(self):
        class MyUser1(User):
            @task
            def my_task(self):
                pass

        class MyUser2(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[MyUser1, MyUser2])

            server.mocked_send(Message("client_ready", __version__, "fake_client1"))

            master.start(7, 7)
            self.assertEqual({"MyUser1": 4, "MyUser2": 3}, master.target_user_classes_count)
            self.assertEqual(7, master.target_user_count)
            self.assertEqual(7, master.spawn_rate)

            master.start(10, 10)
            self.assertEqual({"MyUser1": 5, "MyUser2": 5}, master.target_user_classes_count)
            self.assertEqual(10, master.target_user_count)
            self.assertEqual(10, master.spawn_rate)

            master.start(1, 3)
            self.assertEqual({"MyUser1": 1, "MyUser2": 0}, master.target_user_classes_count)
            self.assertEqual(1, master.target_user_count)
            self.assertEqual(3, master.spawn_rate)

    def test_custom_message_send(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            for i in range(5):
                master.clients[i] = WorkerNode(str(i))
            master.send_message("test_custom_msg", {"test_data": 123})

            self.assertEqual(5, len(server.outbox))
            for _, msg in server.outbox:
                self.assertEqual("test_custom_msg", msg.type)
                self.assertEqual(123, msg.data["test_data"])

    def test_custom_message_receive(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            test_custom_msg = [False]
            test_custom_msg_data = [{}]

            def on_custom_msg(msg, **kw):
                test_custom_msg[0] = True
                test_custom_msg_data[0] = msg.data

            master = self.get_runner()
            master.register_message("test_custom_msg", on_custom_msg)

            server.mocked_send(Message("test_custom_msg", {"test_data": 123}, "dummy_id"))

            self.assertTrue(test_custom_msg[0])
            self.assertEqual(123, test_custom_msg_data[0]["test_data"])

    def test_undefined_custom_message_receive(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            test_custom_msg = [False]

            def on_custom_msg(msg, **kw):
                test_custom_msg[0] = True

            master = self.get_runner()
            master.register_message("test_custom_msg", on_custom_msg)

            server.mocked_send(Message("unregistered_custom_msg", {}, "dummy_id"))

            self.assertFalse(test_custom_msg[0])
            self.assertEqual(1, len(self.mocked_log.warning))
            msg = self.mocked_log.warning[0]
            self.assertIn("Unknown message type recieved from worker", msg)

    def test_wait_for_workers_report_after_ramp_up(self):
        def assert_cache_hits():
            self.assertEqual(master._wait_for_workers_report_after_ramp_up.cache_info().hits, 0)
            master._wait_for_workers_report_after_ramp_up()
            self.assertEqual(master._wait_for_workers_report_after_ramp_up.cache_info().hits, 1)

        master = self.get_runner()

        master._wait_for_workers_report_after_ramp_up.cache_clear()
        self.assertEqual(master._wait_for_workers_report_after_ramp_up(), 0.1)
        assert_cache_hits()

        master._wait_for_workers_report_after_ramp_up.cache_clear()
        with _patch_env("LOCUST_WAIT_FOR_WORKERS_REPORT_AFTER_RAMP_UP", "5.7"):
            self.assertEqual(master._wait_for_workers_report_after_ramp_up(), 5.7)
            assert_cache_hits()

        master._wait_for_workers_report_after_ramp_up.cache_clear()
        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=1.5), _patch_env(
            "LOCUST_WAIT_FOR_WORKERS_REPORT_AFTER_RAMP_UP", "5.7 * WORKER_REPORT_INTERVAL"
        ):
            self.assertEqual(master._wait_for_workers_report_after_ramp_up(), 5.7 * 1.5)
            assert_cache_hits()

        master._wait_for_workers_report_after_ramp_up.cache_clear()


@contextmanager
def _patch_env(name: str, value: str):
    prev_value = os.getenv(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if prev_value is None:
            del os.environ[name]
        else:
            os.environ[name] = prev_value


class TestWorkerRunner(LocustTestCase):
    def setUp(self):
        super().setUp()
        # self._report_to_master_event_handlers = [h for h in events.report_to_master._handlers]

    def tearDown(self):
        # events.report_to_master._handlers = self._report_to_master_event_handlers
        super().tearDown()

    def get_runner(self, environment=None, user_classes=None):
        if environment is None:
            environment = self.environment
        user_classes = user_classes or []
        environment.user_classes = user_classes
        return WorkerRunner(environment, master_host="localhost", master_port=5557)

    def test_worker_stop_timeout(self):
        class MyTestUser(User):
            _test_state = 0

            @task
            def the_task(self):
                MyTestUser._test_state = 1
                gevent.sleep(0.2)
                MyTestUser._test_state = 2

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            worker = self.get_runner(environment=environment, user_classes=[MyTestUser])
            self.assertEqual(1, len(client.outbox))
            self.assertEqual("client_ready", client.outbox[0].type)
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538584,
                        "user_classes_count": {"MyTestUser": 1},
                        "host": "",
                        "stop_timeout": 1,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            # wait for worker to spawn locusts
            self.assertIn("spawning", [m.type for m in client.outbox])
            worker.spawning_greenlet.join()
            self.assertEqual(1, len(worker.user_greenlets))
            # check that locust has started running
            gevent.sleep(0.01)
            self.assertEqual(1, MyTestUser._test_state)
            # send stop message
            client.mocked_send(Message("stop", None, "dummy_client_id"))
            worker.user_greenlets.join()
            # check that locust user got to finish
            self.assertEqual(2, MyTestUser._test_state)

    def test_worker_without_stop_timeout(self):
        class MyTestUser(User):
            _test_state = 0

            @task
            def the_task(self):
                MyTestUser._test_state = 1
                gevent.sleep(0.2)
                MyTestUser._test_state = 2

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment(stop_timeout=None)
            worker = self.get_runner(environment=environment, user_classes=[MyTestUser])
            self.assertEqual(1, len(client.outbox))
            self.assertEqual("client_ready", client.outbox[0].type)
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538584,
                        "user_classes_count": {"MyTestUser": 1},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            # print("outbox:", client.outbox)
            # wait for worker to spawn locusts
            self.assertIn("spawning", [m.type for m in client.outbox])
            worker.spawning_greenlet.join()
            self.assertEqual(1, len(worker.user_greenlets))
            # check that locust has started running
            gevent.sleep(0.01)
            self.assertEqual(1, MyTestUser._test_state)
            # send stop message
            client.mocked_send(Message("stop", None, "dummy_client_id"))
            worker.user_greenlets.join()
            # check that locust user did not get to finish
            self.assertEqual(1, MyTestUser._test_state)

    def test_spawn_message_with_older_timestamp_is_rejected(self):
        class MyUser(User):
            wait_time = constant(1)

            def start(self, group: Group):
                # We do this so that the spawning does not finish
                # too quickly
                gevent.sleep(0.1)
                return super().start(group)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            worker = self.get_runner(environment=environment, user_classes=[MyUser])

            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538584,
                        "user_classes_count": {"MyUser": 10},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            sleep(0.6)
            self.assertEqual(STATE_SPAWNING, worker.state)
            worker.spawning_greenlet.join()
            self.assertEqual(10, worker.user_count)

            # Send same timestamp as the first message
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538584,
                        "user_classes_count": {"MyUser": 9},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            worker.spawning_greenlet.join()
            # Still 10 users
            self.assertEqual(10, worker.user_count)

            # Send older timestamp than the first message
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538583,
                        "user_classes_count": {"MyUser": 2},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            worker.spawning_greenlet.join()
            # Still 10 users
            self.assertEqual(10, worker.user_count)

            # Send newer timestamp than the first message
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538585,
                        "user_classes_count": {"MyUser": 2},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            worker.spawning_greenlet.join()
            self.assertEqual(2, worker.user_count)

            worker.quit()

    def test_worker_messages_sent_to_master(self):
        """
        Ensure that worker includes both "user_count" and "user_classes_count"
        when reporting to the master.
        """

        class MyUser(User):
            wait_time = constant(1)

            def start(self, group: Group):
                # We do this so that the spawning does not finish
                # too quickly
                gevent.sleep(0.1)
                return super().start(group)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            worker = self.get_runner(environment=environment, user_classes=[MyUser])

            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538584,
                        "user_classes_count": {"MyUser": 10},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            sleep(0.6)
            self.assertEqual(STATE_SPAWNING, worker.state)
            worker.spawning_greenlet.join()
            self.assertEqual(10, worker.user_count)

            sleep(2)

            message = next((m for m in reversed(client.outbox) if m.type == "stats"), None)
            self.assertIsNotNone(message)
            self.assertIn("user_count", message.data)
            self.assertIn("user_classes_count", message.data)
            self.assertEqual(message.data["user_count"], 10)
            self.assertEqual(message.data["user_classes_count"]["MyUser"], 10)

            message = next((m for m in client.outbox if m.type == "spawning_complete"), None)
            self.assertIsNotNone(message)
            self.assertIn("user_count", message.data)
            self.assertIn("user_classes_count", message.data)
            self.assertEqual(message.data["user_count"], 10)
            self.assertEqual(message.data["user_classes_count"]["MyUser"], 10)

            worker.quit()

    def test_worker_heartbeat_messages_sent_to_master(self):
        """
        Validate content of the heartbeat payload sent to the master.
        """

        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            worker = self.get_runner(environment=environment, user_classes=[MyUser])

            t0 = time.perf_counter()
            while len([m for m in client.outbox if m.type == "heartbeat"]) == 0:
                self.assertLessEqual(time.perf_counter() - t0, 3)
                sleep(0.1)

            message = next((m for m in reversed(client.outbox) if m.type == "heartbeat"))
            self.assertEqual(len(message.data), 3)
            self.assertIn("state", message.data)
            self.assertIn("current_cpu_usage", message.data)
            self.assertIn("current_memory_usage", message.data)

            worker.quit()

    def test_change_user_count_during_spawning(self):
        class MyUser(User):
            wait_time = constant(1)

            def start(self, group: Group):
                # We do this so that the spawning does not finish
                # too quickly
                gevent.sleep(0.1)
                return super().start(group)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            worker = self.get_runner(environment=environment, user_classes=[MyUser])

            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538584,
                        "user_classes_count": {"MyUser": 10},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            sleep(0.6)
            self.assertEqual(STATE_SPAWNING, worker.state)
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538585,
                        "user_classes_count": {"MyUser": 9},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            sleep(0)
            worker.spawning_greenlet.join()
            self.assertEqual(9, len(worker.user_greenlets))
            worker.quit()

    def test_computed_properties(self):
        class MyUser1(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        class MyUser2(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            worker = self.get_runner(environment=environment, user_classes=[MyUser1, MyUser2])

            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538584,
                        "user_classes_count": {"MyUser1": 10, "MyUser2": 10},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            worker.spawning_greenlet.join()
            self.assertDictEqual(worker.user_classes_count, {"MyUser1": 10, "MyUser2": 10})
            self.assertDictEqual(worker.target_user_classes_count, {"MyUser1": 10, "MyUser2": 10})
            self.assertEqual(worker.target_user_count, 20)

            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538585,
                        "user_classes_count": {"MyUser1": 1, "MyUser2": 2},
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            worker.spawning_greenlet.join()
            self.assertDictEqual(worker.user_classes_count, {"MyUser1": 1, "MyUser2": 2})
            self.assertDictEqual(worker.target_user_classes_count, {"MyUser1": 1, "MyUser2": 2})
            self.assertEqual(worker.target_user_count, 3)

            worker.quit()

    def test_custom_message_send(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            worker = self.get_runner(environment=environment, user_classes=[MyUser])
            client.outbox.clear()
            worker.send_message("test_custom_msg", {"test_data": 123})
            self.assertEqual("test_custom_msg", client.outbox[0].type)
            self.assertEqual(123, client.outbox[0].data["test_data"])
            worker.quit()

    def test_custom_message_receive(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            test_custom_msg = [False]
            test_custom_msg_data = [{}]

            def on_custom_msg(msg, **kw):
                test_custom_msg[0] = True
                test_custom_msg_data[0] = msg.data

            worker = self.get_runner(environment=environment, user_classes=[MyUser])
            worker.register_message("test_custom_msg", on_custom_msg)

            client.mocked_send(Message("test_custom_msg", {"test_data": 123}, "dummy_client_id"))

            self.assertTrue(test_custom_msg[0])
            self.assertEqual(123, test_custom_msg_data[0]["test_data"])
            worker.quit()

    def test_undefined_custom_message_receive(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()

            test_custom_msg = [False]

            def on_custom_msg(msg, **kw):
                test_custom_msg[0] = True

            worker = self.get_runner(environment=environment, user_classes=[MyUser])
            worker.register_message("test_custom_msg", on_custom_msg)

            client.mocked_send(Message("unregistered_custom_msg", {}, "dummy_id"))

            self.assertFalse(test_custom_msg[0])
            self.assertEqual(1, len(self.mocked_log.warning))
            msg = self.mocked_log.warning[0]
            self.assertIn("Unknown message type recieved", msg)

    def test_start_event(self):
        class MyTestUser(User):
            _test_state = 0

            @task
            def the_task(self):
                MyTestUser._test_state = 1
                gevent.sleep(0.2)
                MyTestUser._test_state = 2

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            run_count = [0]

            @environment.events.test_start.add_listener
            def on_test_start(*args, **kw):
                run_count[0] += 1

            worker = self.get_runner(environment=environment, user_classes=[MyTestUser])
            self.assertEqual(1, len(client.outbox))
            self.assertEqual("client_ready", client.outbox[0].type)
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538585,
                        "user_classes_count": {"MyTestUser": 1},
                        "spawn_rate": 1,
                        "num_users": 1,
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            # wait for worker to spawn locusts
            self.assertIn("spawning", [m.type for m in client.outbox])
            worker.spawning_greenlet.join()
            self.assertEqual(1, len(worker.user_greenlets))
            self.assertEqual(1, run_count[0])

            # check that locust has started running
            gevent.sleep(0.01)
            self.assertEqual(1, MyTestUser._test_state)

            # change number of users and check that test_start isn't fired again
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538586,
                        "user_classes_count": {"MyTestUser": 1},
                        "spawn_rate": 1,
                        "num_users": 1,
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            self.assertEqual(1, run_count[0])

            # stop and start to make sure test_start is fired again
            client.mocked_send(Message("stop", None, "dummy_client_id"))
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538587,
                        "user_classes_count": {"MyTestUser": 1},
                        "spawn_rate": 1,
                        "num_users": 1,
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            gevent.sleep(0.01)
            self.assertEqual(2, run_count[0])

            client.mocked_send(Message("stop", None, "dummy_client_id"))

    def test_stop_event(self):
        class MyTestUser(User):
            _test_state = 0

            @task
            def the_task(self):
                MyTestUser._test_state = 1
                gevent.sleep(0.2)
                MyTestUser._test_state = 2

        with mock.patch("locust.rpc.rpc.Client", mocked_rpc()) as client:
            environment = Environment()
            run_count = [0]

            @environment.events.test_stop.add_listener
            def on_test_stop(*args, **kw):
                run_count[0] += 1

            worker = self.get_runner(environment=environment, user_classes=[MyTestUser])
            self.assertEqual(1, len(client.outbox))
            self.assertEqual("client_ready", client.outbox[0].type)
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538585,
                        "user_classes_count": {"MyTestUser": 1},
                        "spawn_rate": 1,
                        "num_users": 1,
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )

            # wait for worker to spawn locusts
            self.assertIn("spawning", [m.type for m in client.outbox])
            worker.spawning_greenlet.join()
            self.assertEqual(1, len(worker.user_greenlets))

            # check that locust has started running
            gevent.sleep(0.01)
            self.assertEqual(1, MyTestUser._test_state)

            # stop and make sure test_stop is fired
            client.mocked_send(Message("stop", None, "dummy_client_id"))
            gevent.sleep(0.01)
            self.assertEqual(1, run_count[0])

            # stop while stopped and make sure the event isn't fired again
            client.mocked_send(Message("stop", None, "dummy_client_id"))
            gevent.sleep(0.01)
            self.assertEqual(1, run_count[0])

            # start and stop to check that the event is fired again
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538586,
                        "user_classes_count": {"MyTestUser": 1},
                        "spawn_rate": 1,
                        "num_users": 1,
                        "host": "",
                        "stop_timeout": None,
                        "parsed_options": {},
                    },
                    "dummy_client_id",
                )
            )
            client.mocked_send(Message("stop", None, "dummy_client_id"))
            gevent.sleep(0.01)
            self.assertEqual(2, run_count[0])


class TestMessageSerializing(unittest.TestCase):
    def test_message_serialize(self):
        msg = Message("client_ready", __version__, "my_id")
        rebuilt = Message.unserialize(msg.serialize())
        self.assertEqual(msg.type, rebuilt.type)
        self.assertEqual(msg.data, rebuilt.data)
        self.assertEqual(msg.node_id, rebuilt.node_id)


class TestStopTimeout(LocustTestCase):
    def test_stop_timeout(self):
        short_time = 0.05

        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                MyTaskSet.state = "first"
                gevent.sleep(short_time)
                MyTaskSet.state = "second"  # should only run when run time + stop_timeout is > short_time
                gevent.sleep(short_time)
                MyTaskSet.state = "third"  # should only run when run time + stop_timeout is > short_time * 2

        class MyTestUser(User):
            tasks = [MyTaskSet]

        environment = Environment(user_classes=[MyTestUser])
        runner = environment.create_local_runner()
        runner.start(1, 1, wait=False)
        gevent.sleep(short_time / 2)
        runner.quit()
        self.assertEqual("first", MyTaskSet.state)

        # exit with timeout
        environment = Environment(user_classes=[MyTestUser], stop_timeout=short_time / 2)
        runner = environment.create_local_runner()
        runner.start(1, 1, wait=False)
        gevent.sleep(short_time)
        runner.quit()
        self.assertEqual("second", MyTaskSet.state)

        # allow task iteration to complete, with some margin
        environment = Environment(user_classes=[MyTestUser], stop_timeout=short_time * 3)
        runner = environment.create_local_runner()
        runner.start(1, 1, wait=False)
        gevent.sleep(short_time)
        timeout = gevent.Timeout(short_time * 2)
        timeout.start()
        try:
            runner.quit()
            runner.greenlet.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception. Some locusts must have kept running after iteration finish")
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

        class MyTestUser(User):
            tasks = [MyTaskSet]

        environment = create_environment([MyTestUser], mocked_options())
        environment.stop_timeout = short_time
        runner = environment.create_local_runner()
        runner.start(1, 1)
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

        class MyTestUser(User):
            tasks = [MyTaskSet]
            wait_time = constant(1)

        environment = Environment(user_classes=[MyTestUser], stop_timeout=short_time)
        runner = environment.create_local_runner()
        runner.start(1, 1)
        gevent.sleep(short_time)  # sleep to make sure locust has had time to start waiting
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

        class MyTestUser(User):
            tasks = [MyTaskSet]

        environment = create_environment([MyTestUser], mocked_options())
        environment.stop_timeout = short_time
        runner = environment.create_local_runner()
        runner.start(1, 1, wait=True)
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

    def test_stop_timeout_with_interrupt_no_reschedule(self):
        state = [0]

        class MySubTaskSet(TaskSet):
            @task
            def a_task(self):
                gevent.sleep(0.1)
                state[0] = 1
                self.interrupt(reschedule=False)

        class MyTestUser(User):
            tasks = [MySubTaskSet]
            wait_time = constant(3)

        environment = create_environment([MyTestUser], mocked_options())
        environment.stop_timeout = 0.3
        runner = environment.create_local_runner()
        runner.start(1, 1, wait=True)
        gevent.sleep(0)
        timeout = gevent.Timeout(0.11)
        timeout.start()
        try:
            runner.quit()
            runner.greenlet.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception. Interrupted locusts should exit immediately during stop_timeout.")
        finally:
            timeout.cancel()
        self.assertEqual(1, state[0])

    def test_kill_locusts_with_stop_timeout(self):
        short_time = 0.05

        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                MyTaskSet.state = "first"
                gevent.sleep(short_time)
                MyTaskSet.state = "second"  # should only run when run time + stop_timeout is > short_time
                gevent.sleep(short_time)
                MyTaskSet.state = "third"  # should only run when run time + stop_timeout is > short_time * 2

        class MyTestUser(User):
            tasks = [MyTaskSet]

        environment = create_environment([MyTestUser], mocked_options())
        runner = environment.create_local_runner()
        runner.start(1, 1)
        gevent.sleep(short_time / 2)
        runner.stop_users({MyTestUser.__name__: 1})
        self.assertEqual("first", MyTaskSet.state)
        runner.quit()
        environment.runner = None

        environment.stop_timeout = short_time / 2  # exit with timeout
        runner = environment.create_local_runner()
        runner.start(1, 1)
        gevent.sleep(short_time)
        runner.stop_users({MyTestUser.__name__: 1})
        self.assertEqual("second", MyTaskSet.state)
        runner.quit()
        environment.runner = None

        environment.stop_timeout = short_time * 3  # allow task iteration to complete, with some margin
        runner = environment.create_local_runner()
        runner.start(1, 1)
        gevent.sleep(short_time)
        timeout = gevent.Timeout(short_time * 2)
        timeout.start()
        try:
            runner.stop_users({MyTestUser.__name__: 1})
            runner.user_greenlets.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception. Some locusts must have kept running after iteration finish")
        finally:
            timeout.cancel()
        self.assertEqual("third", MyTaskSet.state)

    def test_users_can_call_runner_quit_with_stop_timeout(self):
        class BaseUser(User):
            wait_time = constant(1)

            @task
            def trigger(self):
                self.environment.runner.quit()

        runner = Environment(user_classes=[BaseUser]).create_local_runner()
        runner.environment.stop_timeout = 1
        runner.spawn_users({BaseUser.__name__: 1}, wait=False)
        timeout = gevent.Timeout(0.5)
        timeout.start()
        try:
            runner.greenlet.join()
        except gevent.Timeout:
            self.fail("Got Timeout exception, runner must have hung somehow.")
        finally:
            timeout.cancel()

    def test_gracefully_handle_exceptions_in_listener(self):
        class MyUser(User):
            wait_time = constant(1)

            @task
            def my_task(self):
                pass

        test_stop_run = [0]
        environment = Environment(user_classes=[MyUser])

        def on_test_stop_ok(*args, **kwargs):
            test_stop_run[0] += 1

        def on_test_stop_fail(*args, **kwargs):
            assert False

        environment.events.test_stop.add_listener(on_test_stop_ok)
        environment.events.test_stop.add_listener(on_test_stop_fail)
        environment.events.test_stop.add_listener(on_test_stop_ok)

        runner = LocalRunner(environment)
        runner.start(user_count=3, spawn_rate=3, wait=False)
        self.assertEqual(0, test_stop_run[0])
        runner.stop()
        self.assertEqual(2, test_stop_run[0])

    def test_stop_timeout_with_ramp_down(self):
        """
        The spawn rate does not have an effect on the rate at which the users are stopped.
        It is expected that the excess users will be stopped as soon as possible in parallel
        (while respecting the stop_timeout).
        """

        class MyTaskSet(TaskSet):
            @task
            def my_task(self):
                gevent.sleep(1)

        class MyTestUser(User):
            tasks = [MyTaskSet]

        environment = Environment(user_classes=[MyTestUser], stop_timeout=2)
        runner = environment.create_local_runner()

        # Start load test, wait for users to start, then trigger ramp down
        ts = time.perf_counter()
        runner.start(10, 10, wait=False)
        runner.spawning_greenlet.join()
        delta = time.perf_counter() - ts
        self.assertTrue(
            0 <= delta <= 0.05, "Expected user count to increase to 10 instantaneously, instead it took %f" % delta
        )
        self.assertTrue(
            runner.user_count == 10, "User count has not decreased correctly to 2, it is : %i" % runner.user_count
        )

        ts = time.perf_counter()
        runner.start(2, 4, wait=False)
        runner.spawning_greenlet.join()
        delta = time.perf_counter() - ts
        self.assertTrue(2 <= delta <= 2.05, "Expected user count to decrease to 2 in 2s, instead it took %f" % delta)
        self.assertTrue(
            runner.user_count == 2, "User count has not decreased correctly to 2, it is : %i" % runner.user_count
        )
