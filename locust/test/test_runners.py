import os
import time
import unittest
from collections import defaultdict
from contextlib import contextmanager

import gevent
import mock
from gevent import sleep
from gevent.pool import Group
from gevent.queue import Queue

import locust
from locust import (
    LoadTestShape,
    constant,
    runners,
)
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
        runner.spawn_users({BaseUser.__name__: 2}, wait=False)
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
        runner.spawn_users({BaseUser.__name__: 1}, wait=False)
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
        runner.spawn_users({BaseUser.__name__: 10}, wait=False)
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
        self.assertTrue(
            0 <= delta <= 0.05, "Expected user count to decrease to 2 instantaneously, instead it took %f" % delta
        )
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
        self.assertDictEqual({"MyUser1": 5, "MyUser2": 5}, runner.user_class_occurrences)

        runner.start(user_count=5, spawn_rate=5, wait=False)
        runner.spawning_greenlet.join()
        self.assertDictEqual({"MyUser1": 3, "MyUser2": 2}, runner.user_class_occurrences)

        runner.quit()

    def test_user_class_occurrences(self):
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
        self.assertDictEqual({"MyUser1": 5, "MyUser2": 5}, runner.user_class_occurrences)

        runner.start(user_count=5, spawn_rate=5, wait=False)
        runner.spawning_greenlet.join()
        self.assertDictEqual({"MyUser1": 3, "MyUser2": 2}, runner.user_class_occurrences)

        runner.quit()


class TestMasterWorkerRunners(LocustTestCase):
    def test_distributed_integration_run(self):
        """
        Full integration test that starts both a MasterRunner and three WorkerRunner instances
        and makes sure that their stats is sent to the Master.
        """

        class TestUser(User):
            wait_time = constant(0.1)

            @task
            def incr_stats(l):
                l.environment.events.request.fire(
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

        # check the test_stop event was called one time in master and zero times in workder
        self.assertEqual(
            1,
            test_stop_count["master"],
            "The test_stop event was not called exactly one time in the master node",
        )
        self.assertEqual(
            0,
            test_stop_count["worker"],
            "The test_stop event was called in the worker node",
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
            self.assertDictEqual(master.reported_user_class_occurrences, {"TestUser": 9})

            # Ensure new stage with more users has been reached
            sleep(2)
            for worker in workers:
                self.assertEqual(7, worker.user_count, "Shape test has not reached stage 2")
                self.assertEqual(
                    21, test_shape.get_current_user_count(), "Shape is not seeing stage 2 runner user count correctly"
                )
            self.assertDictEqual(master.reported_user_class_occurrences, {"TestUser": 21})

            # Ensure new stage with less users has been reached
            sleep(2)
            for worker in workers:
                self.assertEqual(1, worker.user_count, "Shape test has not reached stage 3")
                self.assertEqual(
                    3, test_shape.get_current_user_count(), "Shape is not seeing stage 3 runner user count correctly"
                )
            self.assertDictEqual(master.reported_user_class_occurrences, {"TestUser": 3})

            # Ensure test stops at the end
            sleep(2)
            for worker in workers:
                self.assertEqual(0, worker.user_count, "Shape test has not stopped")
                self.assertEqual(
                    0, test_shape.get_current_user_count(), "Shape is not seeing stopped runner user count correctly"
                )
            self.assertDictEqual(master.reported_user_class_occurrences, {"TestUser": 0})

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
                    return 5, 3
                elif run_time < 20:
                    return 10, 3
                elif run_time < 40:
                    return 15, 3
                elif run_time < 60:
                    return 5, 3
                else:
                    return None

        worker_additional_wait_before_ready_after_stop = 5
        with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3), _patch_env(
            "WORKER_ADDITIONAL_WAIT_BEFORE_READY_AFTER_STOP", str(worker_additional_wait_before_ready_after_stop)
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
                self.assertTrue(time.time() - ts <= 1)
                sleep()
            sleep(5 - (time.time() - ts))  # runtime = 5s
            self.assertEqual(STATE_RUNNING, master.state)
            w1 = {"TestUser1": 1, "TestUser2": 0, "TestUser3": 0}
            w2 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 0}
            w3 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 0}
            w4 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 1}
            w5 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 1}
            self.assertDictEqual(w1, workers[0].user_class_occurrences)
            self.assertDictEqual(w2, workers[1].user_class_occurrences)
            self.assertDictEqual(w3, workers[2].user_class_occurrences)
            self.assertDictEqual(w4, workers[3].user_class_occurrences)
            self.assertDictEqual(w5, workers[4].user_class_occurrences)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_class_occurrences)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_class_occurrences)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_class_occurrences)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_class_occurrences)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_class_occurrences)
            sleep(5)  # runtime = 10s

            # Second stage
            ts = time.time()
            while master.state != STATE_SPAWNING:
                self.assertTrue(time.time() - ts <= 1)
                sleep()
            sleep(5 - (time.time() - ts))  # runtime = 15s
            self.assertEqual(STATE_RUNNING, master.state)
            w1 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 0}
            w2 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 0}
            w3 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 0}
            w4 = {"TestUser1": 1, "TestUser2": 0, "TestUser3": 1}
            w5 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 2}
            self.assertDictEqual(w1, workers[0].user_class_occurrences)
            self.assertDictEqual(w2, workers[1].user_class_occurrences)
            self.assertDictEqual(w3, workers[2].user_class_occurrences)
            self.assertDictEqual(w4, workers[3].user_class_occurrences)
            self.assertDictEqual(w5, workers[4].user_class_occurrences)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_class_occurrences)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_class_occurrences)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_class_occurrences)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_class_occurrences)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_class_occurrences)
            sleep(5)  # runtime = 20s

            # Third stage
            ts = time.time()
            while master.state != STATE_SPAWNING:
                self.assertTrue(time.time() - ts <= 1)
                sleep()
            sleep(10 - (time.time() - ts))  # runtime = 30s
            ts = time.time()
            while master.state != STATE_RUNNING:
                self.assertTrue(time.time() - ts <= 1)
                sleep()
            self.assertEqual(STATE_RUNNING, master.state)
            w1 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w2 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w3 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w4 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w5 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            self.assertDictEqual(w1, workers[0].user_class_occurrences)
            self.assertDictEqual(w2, workers[1].user_class_occurrences)
            self.assertDictEqual(w3, workers[2].user_class_occurrences)
            self.assertDictEqual(w4, workers[3].user_class_occurrences)
            self.assertDictEqual(w5, workers[4].user_class_occurrences)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_class_occurrences)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_class_occurrences)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_class_occurrences)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_class_occurrences)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_class_occurrences)
            sleep(10 - (time.time() - ts))  # runtime = 40s

            # Fourth stage
            ts = time.time()
            while master.state != STATE_SPAWNING:
                self.assertTrue(time.time() - ts <= 1)
                sleep()
            sleep(5 - (time.time() - ts))  # runtime = 45s

            # Fourth stage - Excess TestUser1 have been stopped but
            #                TestUser2/TestUser3 have not reached stop timeout yet, so
            #                their number are unchanged
            self.assertEqual(master.state, STATE_SPAWNING)
            w1 = {"TestUser1": 1, "TestUser2": 1, "TestUser3": 1}
            w2 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 1}
            w3 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 1}
            w4 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 1}
            w5 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 1}
            self.assertDictEqual(w1, workers[0].user_class_occurrences)
            self.assertDictEqual(w2, workers[1].user_class_occurrences)
            self.assertDictEqual(w3, workers[2].user_class_occurrences)
            self.assertDictEqual(w4, workers[3].user_class_occurrences)
            self.assertDictEqual(w5, workers[4].user_class_occurrences)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_class_occurrences)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_class_occurrences)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_class_occurrences)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_class_occurrences)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_class_occurrences)
            sleep(1)  # runtime = 46s

            # Fourth stage - All users are now at the desired number
            ts = time.time()
            while master.state != STATE_RUNNING:
                self.assertTrue(time.time() - ts <= 1)
                sleep()
            delta = time.time() - ts
            w1 = {"TestUser1": 1, "TestUser2": 0, "TestUser3": 0}
            w2 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 0}
            w3 = {"TestUser1": 0, "TestUser2": 1, "TestUser3": 0}
            w4 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 1}
            w5 = {"TestUser1": 0, "TestUser2": 0, "TestUser3": 1}
            self.assertDictEqual(w1, workers[0].user_class_occurrences)
            self.assertDictEqual(w2, workers[1].user_class_occurrences)
            self.assertDictEqual(w3, workers[2].user_class_occurrences)
            self.assertDictEqual(w4, workers[3].user_class_occurrences)
            self.assertDictEqual(w5, workers[4].user_class_occurrences)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_class_occurrences)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_class_occurrences)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_class_occurrences)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_class_occurrences)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_class_occurrences)
            sleep(10 - delta)  # runtime = 56s

            # Sleep stop_timeout and make sure the test has stopped
            sleep(5)  # runtime = 61s
            self.assertEqual(STATE_STOPPING, master.state)
            sleep(stop_timeout)  # runtime = 66s

            # We wait for "stop_timeout" seconds to let the workers reconnect as "ready" with the master.
            # The reason for waiting an additional "stop_timeout" when we already waited for "stop_timeout"
            # above is that when a worker receives the stop message, it can take up to "stop_timeout"
            # for the worker to send the "client_stopped" message then an additional "stop_timeout" seconds
            # to send the "client_ready" message.
            ts = time.time()
            while len(master.clients.ready) != len(workers):
                self.assertTrue(
                    time.time() - ts <= stop_timeout + worker_additional_wait_before_ready_after_stop,
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
            self.assertDictEqual(w1, workers[0].user_class_occurrences)
            self.assertDictEqual(w2, workers[1].user_class_occurrences)
            self.assertDictEqual(w3, workers[2].user_class_occurrences)
            self.assertDictEqual(w4, workers[3].user_class_occurrences)
            self.assertDictEqual(w5, workers[4].user_class_occurrences)
            self.assertDictEqual(w1, master.clients[workers[0].client_id].user_class_occurrences)
            self.assertDictEqual(w2, master.clients[workers[1].client_id].user_class_occurrences)
            self.assertDictEqual(w3, master.clients[workers[2].client_id].user_class_occurrences)
            self.assertDictEqual(w4, master.clients[workers[3].client_id].user_class_occurrences)
            self.assertDictEqual(w5, master.clients[workers[4].client_id].user_class_occurrences)

            ts = time.time()
            while master.state != STATE_STOPPED:
                self.assertTrue(time.time() - ts <= 5, master.state)
                sleep()

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
            server.mocked_send(Message("client_ready", None, "zeh_fake_client1"))
            self.assertEqual(1, len(master.clients))
            self.assertTrue(
                "zeh_fake_client1" in master.clients, "Could not find fake client in master instance's clients dict"
            )
            server.mocked_send(Message("client_ready", None, "zeh_fake_client2"))
            server.mocked_send(Message("client_ready", None, "zeh_fake_client3"))
            server.mocked_send(Message("client_ready", None, "zeh_fake_client4"))
            self.assertEqual(4, len(master.clients))

            server.mocked_send(Message("quit", None, "zeh_fake_client3"))
            self.assertEqual(3, len(master.clients))

    def test_worker_stats_report_median(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", None, "fake_client"))

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
            server.mocked_send(Message("client_ready", None, "fake_client"))

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
            server.mocked_send(Message("client_ready", None, "fake_client"))
            sleep(6)
            # print(master.clients['fake_client'].__dict__)
            assert master.clients["fake_client"].state == STATE_MISSING

    def test_last_worker_quitting_stops_test(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", None, "fake_client1"))
            server.mocked_send(Message("client_ready", None, "fake_client2"))

            master.start(1, 2)
            server.mocked_send(Message("spawning", None, "fake_client1"))
            server.mocked_send(Message("spawning", None, "fake_client2"))

            server.mocked_send(Message("quit", None, "fake_client1"))
            sleep(0)
            self.assertEqual(1, len(master.clients.all))
            self.assertNotEqual(STATE_STOPPED, master.state, "Not all workers quit but test stopped anyway.")

            server.mocked_send(Message("quit", None, "fake_client2"))
            sleep(0)
            self.assertEqual(0, len(master.clients.all))
            self.assertEqual(STATE_STOPPED, master.state, "All workers quit but test didn't stop.")

    @mock.patch("locust.runners.HEARTBEAT_INTERVAL", new=0.1)
    def test_last_worker_missing_stops_test(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner()
            server.mocked_send(Message("client_ready", None, "fake_client1"))
            server.mocked_send(Message("client_ready", None, "fake_client2"))
            server.mocked_send(Message("client_ready", None, "fake_client3"))

            master.start(3, 3)
            server.mocked_send(Message("spawning", None, "fake_client1"))
            server.mocked_send(Message("spawning", None, "fake_client2"))
            server.mocked_send(Message("spawning", None, "fake_client3"))

            sleep(0.2)
            server.mocked_send(
                Message("heartbeat", {"state": STATE_RUNNING, "current_cpu_usage": 50, "count": 1}, "fake_client1")
            )
            server.mocked_send(
                Message("heartbeat", {"state": STATE_RUNNING, "current_cpu_usage": 50, "count": 1}, "fake_client2")
            )
            server.mocked_send(
                Message("heartbeat", {"state": STATE_RUNNING, "current_cpu_usage": 50, "count": 1}, "fake_client3")
            )

            sleep(0.2)
            self.assertEqual(0, len(master.clients.missing))
            self.assertEqual(3, master.worker_count)
            self.assertNotIn(
                master.state, [STATE_STOPPED, STATE_STOPPING], "Not all workers went missing but test stopped anyway."
            )

            server.mocked_send(
                Message("heartbeat", {"state": STATE_RUNNING, "current_cpu_usage": 50, "count": 1}, "fake_client1")
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
            server.mocked_send(Message("client_ready", None, "fake_client"))
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
                server.mocked_send(Message("client_ready", None, "fake_client"))
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
            server.mocked_send(Message("client_ready", None, "zeh_fake_client1"))
            self.assertEqual(1, len(master.clients))
            self.assertTrue(
                "zeh_fake_client1" in master.clients, "Could not find fake client in master instance's clients dict"
            )

            master.start(100, 20)
            self.assertEqual(5, len(server.outbox))
            for i, (_, msg) in enumerate(server.outbox.copy()):
                self.assertDictEqual({"TestUser": int((i + 1) * 20)}, msg.data["user_class_occurrences"])
                server.outbox.pop()

            # Normally, this attribute would be updated when the
            # master receives the report from the worker.
            master.clients["zeh_fake_client1"].user_class_occurrences = {"TestUser": 100}

            # let another worker connect
            server.mocked_send(Message("client_ready", None, "zeh_fake_client2"))
            self.assertEqual(2, len(master.clients))
            sleep(0.1)  # give time for messages to be sent to clients
            self.assertEqual(2, len(server.outbox))
            client_id, msg = server.outbox.pop()
            self.assertEqual({"TestUser": 50}, msg.data["user_class_occurrences"])
            client_id, msg = server.outbox.pop()
            self.assertEqual({"TestUser": 50}, msg.data["user_class_occurrences"])

    def test_sends_spawn_data_to_ready_running_spawning_workers(self):
        """Sends spawn job to running, ready, or spawning workers"""

        class TestUser(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])
            master.clients[1] = WorkerNode(1)
            master.clients[2] = WorkerNode(2)
            master.clients[3] = WorkerNode(3)
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
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))

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
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))

            master.start(7, 7)
            self.assertEqual(5, len(server.outbox))
            master.stop()
            self.assertEqual(1, run_count[0])

            run_count[0] = 0
            for i in range(5):
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))
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
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))

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
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))

            master.start(7, 7)
            self.assertEqual(5, len(server.outbox))

            num_users = sum(sum(msg.data["user_class_occurrences"].values()) for _, msg in server.outbox if msg.data)

            self.assertEqual(7, num_users, "Total number of locusts that would have been spawned is not 7")

    def test_spawn_fewer_locusts_than_workers(self):
        class TestUser(User):
            @task
            def my_task(self):
                pass

        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            master = self.get_runner(user_classes=[TestUser])

            for i in range(5):
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))

            master.start(2, 2)
            self.assertEqual(5, len(server.outbox))

            num_users = sum(sum(msg.data["user_class_occurrences"].values()) for _, msg in server.outbox if msg.data)

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
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))

            # Start the shape_worker
            self.environment.shape_class.reset_time()
            master.start_shape()
            sleep(0.5)

            # Wait for shape_worker to update user_count
            num_users = sum(sum(msg.data["user_class_occurrences"].values()) for _, msg in server.outbox if msg.data)
            self.assertEqual(
                1, num_users, "Total number of users in first stage of shape test is not 1: %i" % num_users
            )

            # Wait for shape_worker to update user_count again
            sleep(2)
            num_users = sum(sum(msg.data["user_class_occurrences"].values()) for _, msg in server.outbox if msg.data)
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
                server.mocked_send(Message("client_ready", None, "fake_client%i" % i))

            # Start the shape_worker
            self.environment.shape_class.reset_time()
            master.start_shape()
            sleep(0.5)

            # Wait for shape_worker to update user_count
            num_users = sum(sum(msg.data["user_class_occurrences"].values()) for _, msg in server.outbox if msg.data)
            self.assertEqual(
                5, num_users, "Total number of users in first stage of shape test is not 5: %i" % num_users
            )

            # Wait for shape_worker to update user_count again
            sleep(2)
            msgs = defaultdict(dict)
            for _, msg in server.outbox:
                if not msg.data:
                    continue
                msgs[msg.node_id][msg.data["timestamp"]] = sum(msg.data["user_class_occurrences"].values())
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
                server.mocked_send(Message("client_ready", None, "fake_client"))
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

            server.mocked_send(Message("client_ready", None, "fake_client1"))

            master.start(7, 7)
            self.assertEqual({"MyUser1": 3, "MyUser2": 4}, master.target_user_class_occurrences)
            self.assertEqual(7, master.target_user_count)
            self.assertEqual(7, master.spawn_rate)

            master.start(10, 10)
            self.assertEqual({"MyUser1": 5, "MyUser2": 5}, master.target_user_class_occurrences)
            self.assertEqual(10, master.target_user_count)
            self.assertEqual(10, master.spawn_rate)

            master.start(1, 3)
            self.assertEqual({"MyUser1": 1, "MyUser2": 0}, master.target_user_class_occurrences)
            self.assertEqual(1, master.target_user_count)
            self.assertEqual(3, master.spawn_rate)


@contextmanager
def _patch_env(name: str, value: str):
    prev_value = os.getenv(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if prev_value is None:
            os.unsetenv(name)
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
            test_start_run = [False]

            @environment.events.test_start.add_listener
            def on_test_start(_environment, **kw):
                test_start_run[0] = True

            worker = self.get_runner(environment=environment, user_classes=[MyTestUser])
            self.assertEqual(1, len(client.outbox))
            self.assertEqual("client_ready", client.outbox[0].type)
            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538584,
                        "user_class_occurrences": {"MyTestUser": 1},
                        "host": "",
                        "stop_timeout": 1,
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
            # make sure the test_start was never fired on the worker
            self.assertFalse(test_start_run[0])

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
                        "user_class_occurrences": {"MyTestUser": 1},
                        "host": "",
                        "stop_timeout": None,
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
                        "user_class_occurrences": {"MyUser": 10},
                        "host": "",
                        "stop_timeout": None,
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
                        "user_class_occurrences": {"MyUser": 9},
                        "host": "",
                        "stop_timeout": None,
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
                        "user_class_occurrences": {"MyUser": 2},
                        "host": "",
                        "stop_timeout": None,
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
                        "user_class_occurrences": {"MyUser": 2},
                        "host": "",
                        "stop_timeout": None,
                    },
                    "dummy_client_id",
                )
            )
            worker.spawning_greenlet.join()
            self.assertEqual(2, worker.user_count)

            worker.quit()

    def test_worker_messages_sent_to_master(self):
        """
        Ensure that worker includes both "user_count" and "user_class_occurrences"
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
                        "user_class_occurrences": {"MyUser": 10},
                        "host": "",
                        "stop_timeout": None,
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
            self.assertIn("user_class_occurrences", message.data)
            self.assertEqual(message.data["user_count"], 10)
            self.assertEqual(message.data["user_class_occurrences"]["MyUser"], 10)

            message = next((m for m in client.outbox if m.type == "spawning_complete"), None)
            self.assertIsNotNone(message)
            self.assertIn("user_count", message.data)
            self.assertIn("user_class_occurrences", message.data)
            self.assertEqual(message.data["user_count"], 10)
            self.assertEqual(message.data["user_class_occurrences"]["MyUser"], 10)

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
                        "user_class_occurrences": {"MyUser": 10},
                        "host": "",
                        "stop_timeout": None,
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
                        "user_class_occurrences": {"MyUser": 9},
                        "host": "",
                        "stop_timeout": None,
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
                        "user_class_occurrences": {"MyUser1": 10, "MyUser2": 10},
                        "host": "",
                        "stop_timeout": None,
                    },
                    "dummy_client_id",
                )
            )
            worker.spawning_greenlet.join()
            self.assertDictEqual(worker.user_class_occurrences, {"MyUser1": 10, "MyUser2": 10})
            self.assertDictEqual(worker.target_user_class_occurrences, {"MyUser1": 10, "MyUser2": 10})
            self.assertEqual(worker.target_user_count, 20)

            client.mocked_send(
                Message(
                    "spawn",
                    {
                        "timestamp": 1605538585,
                        "user_class_occurrences": {"MyUser1": 1, "MyUser2": 2},
                        "host": "",
                        "stop_timeout": None,
                    },
                    "dummy_client_id",
                )
            )
            worker.spawning_greenlet.join()
            self.assertDictEqual(worker.user_class_occurrences, {"MyUser1": 1, "MyUser2": 2})
            self.assertDictEqual(worker.target_user_class_occurrences, {"MyUser1": 1, "MyUser2": 2})
            self.assertEqual(worker.target_user_count, 3)

            worker.quit()


class TestMessageSerializing(unittest.TestCase):
    def test_message_serialize(self):
        msg = Message("client_ready", None, "my_id")
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
        ts = time.time()
        runner.start(10, 10, wait=False)
        runner.spawning_greenlet.join()
        delta = time.time() - ts
        self.assertTrue(
            0 <= delta <= 0.01, "Expected user count to increase to 10 instantaneously, instead it took %f" % delta
        )
        self.assertTrue(
            runner.user_count == 10, "User count has not decreased correctly to 2, it is : %i" % runner.user_count
        )

        ts = time.time()
        runner.start(2, 4, wait=False)
        runner.spawning_greenlet.join()
        delta = time.time() - ts
        self.assertTrue(1 <= delta <= 1.01, "Expected user count to decrease to 2 in 1s, instead it took %f" % delta)
        self.assertTrue(
            runner.user_count == 2, "User count has not decreased correctly to 2, it is : %i" % runner.user_count
        )
