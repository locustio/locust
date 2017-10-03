"""Slave Locust runner. Represent distributed worker sceduler process"""
import logging
import uuid
import time
import socket
import sys
from multiprocessing import Process
from contextlib import contextmanager

import gevent
from gevent import GreenletExit
from gevent.pool import Group

from locust import stats
from locust.rpc import Message, rpc
from locust import events
from .distributed import DistributedLocustRunner, Node, NodesDict, STATE
from .worker import WorkerLocustRunner

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 3
SLAVE_STATS_INTERVAL = 2
WORKER_INIT_TIMEOUT = 30
WORKER_GREENLET_RATE = 10

class SlaveLocustRunner(DistributedLocustRunner):
    """Master Locust runner. Represent master -> slave communication"""

    class SlaveClientHandler(object):
        """Handler for SlaveClient zmq rpc client"""

        def __init__(self, slave):
            self.slave = slave

        def on_hatch(self, msg):
            self.slave.state = STATE.HATCHING
            self.slave.options.num_requests = msg.data["num_requests"]
            self.slave.start_hatching(msg.data["num_clients"], msg.data["hatch_rate"])

        def on_new_config(self, msg):
            self.slave.options.update_config(msg.data)

        def on_stop(self, msg):
            logger.info("Got stop message from master, stopping...")
            events.locust_stop_hatching.fire()
            self.slave.server.send_all(Message("stop", None, None))
            self.slave.client.send_all(Message("slave_stopped", None, self.slave.slave_id))
            self.slave.client.send_all(Message("slave_ready", None, self.slave.slave_id))

        def on_quit(self, msg):
            logger.info("Got quit message from master, shutting down...")
            events.quitting.fire()

        def on_ping(self, msg):
            self.slave.client.send_all(Message("pong", None, self.slave.slave_id))
            if self.slave.scheduled:
                with self.slave.zmq_listener_pause():
                    for _ in range(len(self.slave.scheduled)):
                        self.slave.scheduled.pop()
                        self.slave.spawn_worker()


    class SlaveServerHandler(object):
        """Handler for SlaveServer zmq rpc client. Represent worker -> slave communication"""

        def __init__(self, slave):
            self.slave = slave

        def on_worker_ready(self, msg):
            id = msg.node_id.encode('ascii')
            self.slave.workers[id] = Node(id)
            if len(self.slave.task_pool) > 0:
                task = self.slave.task_pool.pop()
                self.slave.server.send_to(id, Message("hatch", task, None))
                self.slave.workers[id].task = task

        def on_hatching(self, msg):
            self.slave.workers[msg.node_id].state = STATE.HATCHING
            state = [node.state == STATE.HATCHING for node in self.slave.workers.values()]
            if all(state):
                self.slave.client.send_all(Message("hatching", None, self.slave.slave_id))

        def on_hatch_complete(self, msg):
            self.slave.workers[msg.node_id].state = STATE.RUNNING
            self.slave.workers[msg.node_id].user_count = msg.data["count"]
            state = [node.state == STATE.RUNNING for node in self.slave.workers.values()]
            if all(state):
                self.slave.state = STATE.RUNNING
                data = {"count": sum([w.user_count for w in self.slave.workers.values()])}
                self.slave.client.send_all(Message("hatch_complete", data, self.slave.slave_id))

        def on_quit(self, msg):
            if msg.node_id in self.slave.workers:
                del self.slave.workers[msg.node_id]
                logger.info(
                    "worker %r quit. Currently %i workers connected.",
                    msg.node_id,
                    len(self.slave.workers.ready)
                )

        def on_exception(self, msg):
            self.slave.client.send_all(Message("exception", msg.data, self.slave.slave_id))

        def on_stats(self, msg):
            events.node_report.fire(node_id=msg.node_id, data=msg.data)

        def on_pong(self, msg):
            self.slave.workers[msg.node_id].ping_answ = True


    @classmethod
    def spawn(self, locust_classes, options, parent):
        parent.server.close()
        try:
            parent.greenlet.kill(block=True)
        except GreenletExit:
            pass
        gevent.reinit()
        events.clear_events_handlers()
        stats.subscribe_stats()
        runner = SlaveLocustRunner(locust_classes, options)
        runner.greenlet.join()
        sys.exit(0)

    def __init__(self, locust_classes, options):
        super(SlaveLocustRunner, self).__init__(locust_classes, options)

        self.state = STATE.INIT
        self.slave_id = socket.gethostname().replace(' ', '_') + "_" + uuid.uuid4().hex
        self.greenlet = Group()
        self.task_pool = []
        self.scheduled = []
        self.worker_listener = None

        self.client = rpc.SlaveClient(self.master_host, self.master_port, self.slave_id)
        self.client.bind_handler(self.SlaveClientHandler(self))

        self.server = rpc.SlaveServer(self.master_bind_port)
        self.server.bind_handler(self.SlaveServerHandler(self))

        self.workers = NodesDict()

        # listener that gathers info on how many locust users the slaves has spawned
        def on_worker_report(node_id, data):
            self.workers[node_id].user_count = data["user_count"]
        events.node_report += on_worker_report

        # register listener that adds the current number of
        # spawned locusts and workers to the report that is sent to the master node
        def on_report_to_master(node_id, data):
            data["user_count"] = sum([n.user_count for n in self.workers.values()])
            data["worker_count"] = len(self.workers)
        events.report_to_master += on_report_to_master

        # register listener that sends quit message to slave nodes
        def on_quitting():
            self.quit()
        events.quitting += on_quitting

        self.greenlet.spawn(self.master_listener).link_exception(callback=self.noop)

        gevent.sleep(0.5)
        self.client.send_all(Message("slave_ready", None, self.slave_id))
        self.greenlet.spawn(self.stats_reporter).link_exception(callback=self.noop)
        self.greenlet.spawn(self.heartbeat).link_exception(callback=self.noop)

    @property
    def worker_count(self):
        return len(self.workers)

    def spawn_worker(self):
        pid = Process(target=WorkerLocustRunner.spawn, args=(
            self.locust_classes,
            self.options,
            self
        ))
        pid.start()

    def wait_for_workers(self, n=0):
        counter = 0
        while counter <= WORKER_INIT_TIMEOUT:
            if len(self.workers) >= n:
                return
            gevent.sleep(2)
            counter += 2
        raise Exception("Only {} workers connected from expected {}".format(
            len(self.workers), n
        ))

    def quit(self):
        self.server.send_all(Message("quit", None, None))
        self.client.send_all(Message("quit", None, None))
        self.greenlet.kill(block=True)
        self.server.close()
        self.client.close()

    def master_listener(self):
        while True:
            self.client.recv()

    def workers_listener(self):
        while True:
            self.server.recv()

    def stats_reporter(self):
        while True:
            data = {'worker_count': self.worker_count}
            events.report_to_master.fire(node_id=self.slave_id, data=data)
            self.client.send_all(Message("stats", data, self.slave_id))
            gevent.sleep(SLAVE_STATS_INTERVAL)

    def heartbeat(self):
        while True:
            gen = (w for w in self.workers.copy().itervalues() if not w.ping_answ)
            for dead_worker in gen:
                logger.info("Worker does not respond. Killing it %s", dead_worker.id)
                self.server.send_to(dead_worker.id, Message("quit", None, None))
                self.task_pool.append(dead_worker.task)
                del self.workers[dead_worker.id]
                self.scheduled.append('worker')

            for worker in self.workers.itervalues():
                worker.ping_answ = False
                self.server.send_all(Message("ping", None, None))
            gevent.sleep(HEARTBEAT_INTERVAL)

    def start_hatching(self, locust_count, hatch_rate):
        with self.zmq_listener_pause():
            self.state = STATE.HATCHING
            worker_num = locust_count // WORKER_GREENLET_RATE + 1

            if self.state != STATE.RUNNING and self.state != STATE.HATCHING:
                self.stats.clear_all()
                events.master_start_hatching.fire()

            for _ in range(worker_num):
                self.spawn_worker()

        self.wait_for_workers(worker_num)

        leftover = locust_count - (locust_count / worker_num) * worker_num
        adjust = lambda x: 1 if x <= leftover else 0
        calc = lambda x: locust_count / worker_num + adjust(x)
        worker_locust_count = [calc(x) for x in range(1, worker_num + 1)]
        worker_hatch_rate = hatch_rate / float(worker_num)
        if self.options.num_requests:
            worker_num_requests = int(self.options.num_requests / worker_num)
        else:
            worker_num_requests = None

        logger.info("Sending hatch jobs to %d ready workers", worker_num)

        for client_rate, slave_id in zip(worker_locust_count, self.workers.keys()):
            data = {
                "hatch_rate": worker_hatch_rate,
                "num_clients": client_rate,
                "num_requests": worker_num_requests
            }
            self.server.send_to(slave_id, Message("hatch", data, None))
            self.workers[slave_id].task = data

        self.stats.start_time = time.time()
        self.state = STATE.HATCHING

    @contextmanager
    def zmq_listener_pause(self):
        if self.worker_listener:
            self.worker_listener.kill(block=True)
        yield
        self.worker_listener = self.greenlet.spawn(self.workers_listener)
        self.worker_listener.link_exception(callback=self.noop)
