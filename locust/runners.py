# -*- coding: utf-8 -*-
import logging
import random
import socket
import traceback
import warnings
from uuid import uuid4
from time import time

import gevent
import psutil
from gevent.pool import Group

from .rpc import Message, rpc
from .stats import RequestStats, setup_distributed_stats_event_listeners

from .exception import RPCError

logger = logging.getLogger(__name__)


STATE_INIT, STATE_HATCHING, STATE_RUNNING, STATE_CLEANUP, STATE_STOPPING, STATE_STOPPED, STATE_MISSING = ["ready", "hatching", "running", "cleanup", "stopping", "stopped", "missing"]
WORKER_REPORT_INTERVAL = 3.0
CPU_MONITOR_INTERVAL = 5.0
HEARTBEAT_INTERVAL = 1
HEARTBEAT_LIVENESS = 3
FALLBACK_INTERVAL = 5


class LocustRunner(object):
    def __init__(self, environment, locust_classes):
        environment.runner = self
        self.environment = environment
        self.locust_classes = locust_classes
        self.locusts = Group()
        self.greenlet = Group()
        self.state = STATE_INIT
        self.hatching_greenlet = None
        self.stepload_greenlet = None
        self.current_cpu_usage = 0
        self.cpu_warning_emitted = False
        self.greenlet.spawn(self.monitor_cpu)
        self.exceptions = {}
        self.stats = RequestStats()
        
        # set up event listeners for recording requests
        def on_request_success(request_type, name, response_time, response_length, **kwargs):
            self.stats.log_request(request_type, name, response_time, response_length)
        
        def on_request_failure(request_type, name, response_time, response_length, exception, **kwargs):
            self.stats.log_request(request_type, name, response_time, response_length)
            self.stats.log_error(request_type, name, exception)
        
        self.environment.events.request_success.add_listener(on_request_success)
        self.environment.events.request_failure.add_listener(on_request_failure)
        self.connection_broken = False

        # register listener that resets stats when hatching is complete
        def on_hatch_complete(user_count):
            self.state = STATE_RUNNING
            if environment.reset_stats:
                logger.info("Resetting stats\n")
                self.stats.reset_all()
        self.environment.events.hatch_complete.add_listener(on_hatch_complete)
    
    def __del__(self):
        # don't leave any stray greenlets if runner is removed
        if self.greenlet and len(self.greenlet) > 0:
            self.greenlet.kill(block=False)
    
    @property
    def errors(self):
        return self.stats.errors
    
    @property
    def user_count(self):
        return len(self.locusts)

    def cpu_log_warning(self):
        """Called at the end of the test to repeat the warning & return the status"""
        if self.cpu_warning_emitted:
            logger.warning("Loadgen CPU usage was too high at some point during the test! See https://docs.locust.io/en/stable/running-locust-distributed.html for how to distribute the load over multiple CPU cores or machines")
            return True
        return False

    def weight_locusts(self, amount):
        """
        Distributes the amount of locusts for each WebLocust-class according to it's weight
        returns a list "bucket" with the weighted locusts
        """
        bucket = []
        weight_sum = sum([locust.weight for locust in self.locust_classes])
        residuals = {}
        for locust in self.locust_classes:
            if self.environment.host is not None:
                locust.host = self.environment.host

            # create locusts depending on weight
            percent = locust.weight / float(weight_sum)
            num_locusts = int(round(amount * percent))
            bucket.extend([locust for x in range(num_locusts)])
            # used to keep track of the amount of rounding was done if we need
            # to add/remove some instances from bucket
            residuals[locust] = amount * percent - round(amount * percent)
        if len(bucket) < amount:
            # We got too few locust classes in the bucket, so we need to create a few extra locusts,
            # and we do this by iterating over each of the Locust classes - starting with the one
            # where the residual from the rounding was the largest - and creating one of each until
            # we get the correct amount
            for locust in [l for l, r in sorted(residuals.items(), key=lambda x:x[1], reverse=True)][:amount-len(bucket)]:
                bucket.append(locust)
        elif len(bucket) > amount:
            # We've got too many locusts due to rounding errors so we need to remove some
            for locust in [l for l, r in sorted(residuals.items(), key=lambda x:x[1])][:len(bucket)-amount]:
                bucket.remove(locust)

        return bucket

    def spawn_locusts(self, spawn_count, hatch_rate, wait=False):
        bucket = self.weight_locusts(spawn_count)
        spawn_count = len(bucket)
        if self.state == STATE_INIT or self.state == STATE_STOPPED:
            self.state = STATE_HATCHING
        
        existing_count = len(self.locusts)
        logger.info("Hatching and swarming %i users at the rate %g users/s (%i users already running)..." % (spawn_count, hatch_rate, existing_count))
        occurrence_count = dict([(l.__name__, 0) for l in self.locust_classes])
        
        def hatch():
            sleep_time = 1.0 / hatch_rate
            hatch_count = 0
            while True:
                if not bucket:
                    logger.info("All locusts hatched: %s (%i already running)" % (
                        ", ".join(["%s: %d" % (name, count) for name, count in occurrence_count.items()]), 
                        existing_count,
                    ))
                    if not sorted([g.args[0].id for g in self.locusts]) == list(range(len(self.locusts))):
                        logger.warning("Locust IDs are not consecutive.")
                    self.environment.events.hatch_complete.fire(user_count=len(self.locusts))
                    return

                locust_class = bucket.pop(random.randint(0, len(bucket)-1))
                occurrence_count[locust_class.__name__] += 1
                new_locust = locust_class(self.environment)
                new_locust.id = existing_count + hatch_count
                new_locust.start(self.locusts)
                hatch_count += 1
                if len(self.locusts) % 10 == 0:
                    logger.debug("%i locusts hatched" % len(self.locusts))
                if bucket:
                    gevent.sleep(sleep_time)
        
        hatch()
        if wait:
            self.locusts.join()
            logger.info("All locusts dead\n")

    def kill_locusts(self, kill_count):
        """
        Kill a kill_count of weighted locusts from the Group() object in self.locusts
        """
        bucket = self.weight_locusts(kill_count)
        kill_count = len(bucket)
        logger.info("Killing %i locusts" % kill_count)
        to_kill = []
        for g in self.locusts:
            for l in bucket:
                user = g.args[0]
                if l == type(user):
                    to_kill.append(user)
                    bucket.remove(l)
                    break

        to_kill_ids = sorted([user.id for user in to_kill])
        remaining_count = len(self.locusts) - kill_count
        for g in self.locusts:
            if g.args[0].id >= remaining_count:
                g.args[0].id = to_kill_ids.pop()

        self.kill_locust_instances(to_kill)
        if not sorted([g.args[0].id for g in self.locusts]) == list(range(len(self.locusts))):
            logger.warning("Locust IDs are not consecutive.")

        self.environment.events.hatch_complete.fire(user_count=self.user_count)
    
    
    def kill_locust_instances(self, users):
        if self.environment.stop_timeout:
            dying = Group()
            for user in users:
                if not user.stop(self.locusts, force=False):
                    # Locust.stop() returns False if the greenlet was not killed, so we'll need
                    # to add it's greenlet to our dying Group so we can wait for it to finish it's task
                    dying.add(user._greenlet)
            if not dying.join(timeout=self.environment.stop_timeout):
                logger.info("Not all locusts finished their tasks & terminated in %s seconds. Killing them..." % self.environment.stop_timeout)
            dying.kill(block=True)
        else:
            for user in users:
                user.stop(self.locusts, force=True)
        
    def monitor_cpu(self):
        process = psutil.Process()
        while True:
            self.current_cpu_usage = process.cpu_percent()
            if self.current_cpu_usage > 90 and not self.cpu_warning_emitted:
                logging.warning("Loadgen CPU usage above 90%! This may constrain your throughput and may even give inconsistent response time measurements! See https://docs.locust.io/en/stable/running-locust-distributed.html for how to distribute the load over multiple CPU cores or machines")
                self.cpu_warning_emitted = True
            gevent.sleep(CPU_MONITOR_INTERVAL)

    def start(self, locust_count, hatch_rate, wait=False):
        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            self.stats.clear_all()
            self.exceptions = {}
            self.cpu_warning_emitted = False
            self.worker_cpu_warning_emitted = False

        # Dynamically changing the locust count
        if self.state != STATE_INIT and self.state != STATE_STOPPED:
            self.state = STATE_HATCHING
            if self.user_count > locust_count:
                # Kill some locusts
                kill_count = self.user_count - locust_count
                self.kill_locusts(kill_count)
            elif self.user_count < locust_count:
                # Spawn some locusts
                spawn_count = locust_count - self.user_count
                self.spawn_locusts(spawn_count=spawn_count, hatch_rate=hatch_rate)
            else:
                self.environment.events.hatch_complete.fire(user_count=self.user_count)
        else:
            self.hatch_rate = hatch_rate
            self.spawn_locusts(locust_count, hatch_rate=hatch_rate, wait=wait)

    def start_stepload(self, locust_count, hatch_rate, step_locust_count, step_duration):
        if locust_count < step_locust_count:
            logger.error("Invalid parameters: total locust count of %d is smaller than step locust count of %d" % (locust_count, step_locust_count))
            return
        self.total_clients = locust_count
        
        if self.stepload_greenlet:
            logger.info("There is an ongoing swarming in Step Load mode, will stop it now.")
            self.stepload_greenlet.kill()
        logger.info("Start a new swarming in Step Load mode: total locust count of %d, hatch rate of %d, step locust count of %d, step duration of %d " % (locust_count, hatch_rate, step_locust_count, step_duration))
        self.state = STATE_INIT
        self.stepload_greenlet = self.greenlet.spawn(self.stepload_worker, hatch_rate, step_locust_count, step_duration)

    def stepload_worker(self, hatch_rate, step_clients_growth, step_duration):
        current_num_clients = 0
        while self.state == STATE_INIT or self.state == STATE_HATCHING or self.state == STATE_RUNNING:
            current_num_clients += step_clients_growth
            if current_num_clients > int(self.total_clients):
                logger.info('Step Load is finished.')
                break
            self.start(current_num_clients, hatch_rate)
            logger.info('Step loading: start hatch job of %d locust.' % (current_num_clients))
            gevent.sleep(step_duration)

    def stop(self):
        self.state = STATE_CLEANUP
        # if we are currently hatching locusts we need to kill the hatching greenlet first
        if self.hatching_greenlet and not self.hatching_greenlet.ready():
            self.hatching_greenlet.kill(block=True)
        self.kill_locust_instances([g.args[0] for g in self.locusts])
        self.state = STATE_STOPPED
        self.cpu_log_warning()
    
    def quit(self):
        self.stop()
        self.greenlet.kill(block=True)

    def log_exception(self, node_id, msg, formatted_tb):
        key = hash(formatted_tb)
        row = self.exceptions.setdefault(key, {"count": 0, "msg": msg, "traceback": formatted_tb, "nodes": set()})
        row["count"] += 1
        row["nodes"].add(node_id)
        self.exceptions[key] = row


class LocalLocustRunner(LocustRunner):
    def __init__(self, environment, locust_classes):
        super(LocalLocustRunner, self).__init__(environment, locust_classes)

        # register listener thats logs the exception for the local runner
        def on_locust_error(locust_instance, exception, tb):
            formatted_tb = "".join(traceback.format_tb(tb))
            self.log_exception("local", str(exception), formatted_tb)
        self.environment.events.locust_error.add_listener(on_locust_error)

    def start(self, locust_count, hatch_rate, wait=False):
        if hatch_rate > 100:
            logger.warning("Your selected hatch rate is very high (>100), and this is known to sometimes cause issues. Do you really need to ramp up that fast?")
        
        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            # if we're not already running we'll fire the test_start event
            self.environment.events.test_start.fire(environment=self.environment)
        
        if self.hatching_greenlet:
            # kill existing hatching_greenlet before we start a new one
            self.hatching_greenlet.kill(block=True)
        self.hatching_greenlet = self.greenlet.spawn(lambda: super(LocalLocustRunner, self).start(locust_count, hatch_rate, wait=wait))
    
    def stop(self):
        super().stop()
        self.environment.events.test_stop.fire(environment=self.environment)


class DistributedLocustRunner(LocustRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setup_distributed_stats_event_listeners(self.environment.events, self.stats)

class WorkerNode(object):
    def __init__(self, id, state=STATE_INIT, heartbeat_liveness=HEARTBEAT_LIVENESS):
        self.id = id
        self.state = state
        self.user_count = 0
        self.heartbeat = heartbeat_liveness
        self.cpu_usage = 0
        self.cpu_warning_emitted = False

class MasterLocustRunner(DistributedLocustRunner):
    def __init__(self, *args, master_bind_host, master_bind_port, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_cpu_warning_emitted = False
        self.target_user_count = None
        self.master_bind_host = master_bind_host
        self.master_bind_port = master_bind_port

        class WorkerNodesDict(dict):
            def get_by_state(self, state):
                return [c for c in self.values() if c.state == state]
            
            @property
            def all(self):
                return self.values()

            @property
            def ready(self):
                return self.get_by_state(STATE_INIT)
            
            @property
            def hatching(self):
                return self.get_by_state(STATE_HATCHING)
            
            @property
            def running(self):
                return self.get_by_state(STATE_RUNNING)
        
        self.clients = WorkerNodesDict()
        self.server = rpc.Server(master_bind_host, master_bind_port)
        self.greenlet.spawn(self.heartbeat_worker)
        self.greenlet.spawn(self.client_listener)

        # listener that gathers info on how many locust users the worker has spawned
        def on_worker_report(client_id, data):
            if client_id not in self.clients:
                logger.info("Discarded report from unrecognized worker %s", client_id)
                return

            self.clients[client_id].user_count = data["user_count"]
        self.environment.events.worker_report.add_listener(on_worker_report)
        
        # register listener that sends quit message to worker nodes
        def on_quitting():
            self.quit()
        self.environment.events.quitting.add_listener(on_quitting)
    
    @property
    def user_count(self):
        return sum([c.user_count for c in self.clients.values()])
    
    def cpu_log_warning(self):
        warning_emitted = LocustRunner.cpu_log_warning(self)
        if self.worker_cpu_warning_emitted:
            logger.warning("CPU usage threshold was exceeded on workers during the test!")
            warning_emitted = True
        return warning_emitted

    def start(self, locust_count, hatch_rate):
        self.target_user_count = locust_count
        num_workers = len(self.clients.ready) + len(self.clients.running) + len(self.clients.hatching)
        if not num_workers:
            logger.warning("You are running in distributed mode but have no worker servers connected. "
                           "Please connect workers prior to swarming.")
            return

        self.hatch_rate = hatch_rate
        worker_num_clients = locust_count // (num_workers or 1)
        worker_hatch_rate = float(hatch_rate) / (num_workers or 1)
        remaining = locust_count % num_workers

        logger.info("Sending hatch jobs of %d locusts and %.2f hatch rate to %d ready clients" % (worker_num_clients, worker_hatch_rate, num_workers))

        if worker_hatch_rate > 100:
            logger.warning("Your selected hatch rate is very high (>100/worker), and this is known to sometimes cause issues. Do you really need to ramp up that fast?")

        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            self.stats.clear_all()
            self.exceptions = {}
            self.environment.events.test_start.fire(environment=self.environment)
        
        for client in (self.clients.ready + self.clients.running + self.clients.hatching):
            data = {
                "hatch_rate": worker_hatch_rate,
                "num_clients": worker_num_clients,
                "host": self.environment.host,
                "stop_timeout": self.environment.stop_timeout,
            }

            if remaining > 0:
                data["num_clients"] += 1
                remaining -= 1

            self.server.send_to_client(Message("hatch", data, client.id))
        
        self.state = STATE_HATCHING

    def stop(self):
        self.state = STATE_STOPPING
        for client in self.clients.all:
            self.server.send_to_client(Message("stop", None, client.id))
        self.environment.events.test_stop.fire(environment=self.environment)
    
    def quit(self):
        if self.state in [STATE_INIT, STATE_STOPPED, STATE_STOPPING]:
            # fire test_stop event if state isn't already stopped
            self.environment.events.test_stop.fire(environment=self.environment)
            
        for client in self.clients.all:
            self.server.send_to_client(Message("quit", None, client.id))
        gevent.sleep(0.5) # wait for final stats report from all workers
        self.greenlet.kill(block=True)
    
    def heartbeat_worker(self):
        while True:
            gevent.sleep(HEARTBEAT_INTERVAL)
            if self.connection_broken:
                self.reset_connection()
                continue
            for client in self.clients.all:
                if client.heartbeat < 0 and client.state != STATE_MISSING:
                    logger.info('Worker %s failed to send heartbeat, setting state to missing.' % str(client.id))
                    client.state = STATE_MISSING
                    client.user_count = 0
                else:
                    client.heartbeat -= 1

    def broadcast_timeslots(self):
        index = 0
        num_clients = self.worker_count
        for client in self.clients.all:
            timeslot_ratio = index/num_clients
            self.server.send_to_client(Message("timeslot_ratio", timeslot_ratio, client.id))
            index += 1

    def reset_connection(self):
        logger.info("Reset connection to slave")
        try:
            self.server.close()
            self.server = rpc.Server(self.master_bind_host, self.master_bind_port)
        except RPCError as e:
            logger.error("Temporay failure when resetting connection: %s, will retry later." % ( e ) )

    def client_listener(self):
        while True:
            try: 
                client_id, msg = self.server.recv_from_client()
            except RPCError as e:
                logger.error("RPCError found when receiving from client: %s" % ( e ) )
                self.connection_broken = True
                gevent.sleep(FALLBACK_INTERVAL)
                continue
            self.connection_broken = False
            msg.node_id = client_id
            if msg.type == "client_ready":
                id = msg.node_id
                self.clients[id] = WorkerNode(id, heartbeat_liveness=HEARTBEAT_LIVENESS)
                logger.info("Client %r reported as ready. Currently %i clients ready to swarm." % (id, len(self.clients.ready + self.clients.running + self.clients.hatching)))
                if self.state == STATE_RUNNING or self.state == STATE_HATCHING:
                    # balance the load distribution when new client joins
                    self.start(self.target_user_count, self.hatch_rate)
                ## emit a warning if the worker's clock seem to be out of sync with our clock
                #if abs(time() - msg.data["time"]) > 5.0:
                #    warnings.warn("The worker node's clock seem to be out of sync. For the statistics to be correct the different locust servers need to have synchronized clocks.")
                self.broadcast_timeslots()
            elif msg.type == "client_stopped":
                del self.clients[msg.node_id]
                logger.info("Removing %s client from running clients" % (msg.node_id))
            elif msg.type == "heartbeat":
                if msg.node_id in self.clients:
                    c = self.clients[msg.node_id]
                    c.heartbeat = HEARTBEAT_LIVENESS
                    c.state = msg.data['state']
                    c.cpu_usage = msg.data['current_cpu_usage']
                    if not c.cpu_warning_emitted and c.cpu_usage > 90:
                        self.worker_cpu_warning_emitted = True # used to fail the test in the end
                        c.cpu_warning_emitted = True          # used to suppress logging for this node
                        logger.warning("Worker %s exceeded cpu threshold (will only log this once per worker)" % (msg.node_id))
            elif msg.type == "stats":
                self.environment.events.worker_report.fire(client_id=msg.node_id, data=msg.data)
            elif msg.type == "hatching":
                self.clients[msg.node_id].state = STATE_HATCHING
            elif msg.type == "hatch_complete":
                self.clients[msg.node_id].state = STATE_RUNNING
                self.clients[msg.node_id].user_count = msg.data["count"]
                if len(self.clients.hatching) == 0:
                    count = sum(c.user_count for c in self.clients.values())
                    self.environment.events.hatch_complete.fire(user_count=count)
            elif msg.type == "quit":
                if msg.node_id in self.clients:
                    del self.clients[msg.node_id]
                    logger.info("Client %r quit. Currently %i clients connected." % (msg.node_id, len(self.clients.ready)))
                self.broadcast_timeslots()
            elif msg.type == "exception":
                self.log_exception(msg.node_id, msg.data["msg"], msg.data["traceback"])

            if not self.state == STATE_INIT and all(map(lambda x: x.state != STATE_RUNNING and x.state != STATE_HATCHING, self.clients.all)):
                self.state = STATE_STOPPED

    @property
    def worker_count(self):
        return len(self.clients.ready) + len(self.clients.hatching) + len(self.clients.running)

class WorkerLocustRunner(DistributedLocustRunner):
    def __init__(self, *args, master_host, master_port, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = socket.gethostname() + "_" + uuid4().hex
        self.master_host = master_host
        self.master_port = master_port
        self.timeslot_ratio = 0
        self.client = rpc.Client(master_host, master_port, self.client_id)
        self.greenlet.spawn(self.heartbeat)
        self.greenlet.spawn(self.worker)
        self.client.send(Message("client_ready", None, self.client_id))
        self.worker_state = STATE_INIT
        self.greenlet.spawn(self.stats_reporter)
        
        # register listener for when all locust users have hatched, and report it to the master node
        def on_hatch_complete(user_count):
            self.client.send(Message("hatch_complete", {"count":user_count}, self.client_id))
            self.worker_state = STATE_RUNNING
        self.environment.events.hatch_complete.add_listener(on_hatch_complete)
        
        # register listener that adds the current number of spawned locusts to the report that is sent to the master node 
        def on_report_to_master(client_id, data):
            data["user_count"] = self.user_count
        self.environment.events.report_to_master.add_listener(on_report_to_master)
        
        # register listener that sends quit message to master
        def on_quitting():
            self.client.send(Message("quit", None, self.client_id))
        self.environment.events.quitting.add_listener(on_quitting)

        # register listener thats sends locust exceptions to master
        def on_locust_error(locust_instance, exception, tb):
            formatted_tb = "".join(traceback.format_tb(tb))
            self.client.send(Message("exception", {"msg" : str(exception), "traceback" : formatted_tb}, self.client_id))
        self.environment.events.locust_error.add_listener(on_locust_error)

    def heartbeat(self):
        while True:
            try:
                self.client.send(Message('heartbeat', {'state': self.worker_state, 'current_cpu_usage': self.current_cpu_usage}, self.client_id))
            except RPCError as e:
                logger.error("RPCError found when sending heartbeat: %s" % ( e ) )
                self.reset_connection()
            gevent.sleep(HEARTBEAT_INTERVAL)

    def reset_connection(self):
        logger.info("Reset connection to master")
        try:
            self.client.close()
            self.client = rpc.Client(self.master_host, self.master_port, self.client_id)
        except RPCError as e:
            logger.error("Temporary failure when resetting connection: %s, will retry later." % ( e ) )

    def worker(self):
        while True:
            try:
                msg = self.client.recv()
            except RPCError as e:
                logger.error("RPCError found when receiving from master: %s" % ( e ) )
                continue
            if msg.type == "hatch":
                self.worker_state = STATE_HATCHING
                self.client.send(Message("hatching", None, self.client_id))
                job = msg.data
                self.hatch_rate = job["hatch_rate"]
                self.environment.host = job["host"]
                self.environment.stop_timeout = job["stop_timeout"]
                if self.hatching_greenlet:
                    # kill existing hatching greenlet before we launch new one
                    self.hatching_greenlet.kill(block=True)
                self.hatching_greenlet = self.greenlet.spawn(lambda: self.start(locust_count=job["num_clients"], hatch_rate=job["hatch_rate"]))
            elif msg.type == "stop":
                self.stop()
                self.client.send(Message("client_stopped", None, self.client_id))
                self.client.send(Message("client_ready", None, self.client_id))
                self.worker_state = STATE_INIT
            elif msg.type == "quit":
                logger.info("Got quit message from master, shutting down...")
                self.stop()
                self._send_stats() # send a final report, in case there were any samples not yet reported
                self.greenlet.kill(block=True)
            elif msg.type == "timeslot_ratio":
                self.timeslot_ratio = msg.data

    def stats_reporter(self):
        while True:
            try:
                self._send_stats()
            except RPCError as e:
                logger.error("Temporary connection lost to master server: %s, will retry later." % (e))            
            gevent.sleep(WORKER_REPORT_INTERVAL)

    def _send_stats(self):
        data = {}
        self.environment.events.report_to_master.fire(client_id=self.client_id, data=data)
        self.client.send(Message("stats", data, self.client_id))
