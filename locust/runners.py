# -*- coding: utf-8 -*-
import logging
import random
import socket
import sys
import traceback
import warnings
from uuid import uuid4
from time import time

import gevent
import psutil
from gevent.pool import Group

from .log import greenlet_exception_logger
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


greenlet_exception_handler = greenlet_exception_logger(logger)


class Runner(object):
    """
    Orchestrates the load test by starting and stopping the users.
    
    Use one of the :meth:`create_local_runner <locust.env.Environment.create_local_runner>`, 
    :meth:`create_master_runner <locust.env.Environment.create_master_runner>` or 
    :meth:`create_worker_runner <locust.env.Environment.create_worker_runner>` methods on
    the :class:`Environment <locust.env.Environment>` instance to create a runner of the 
    desired type.
    """
    def __init__(self, environment):
        self.environment = environment
        self.user_greenlets = Group()
        self.greenlet = Group()
        self.state = STATE_INIT
        self.hatching_greenlet = None
        self.stepload_greenlet = None
        self.current_cpu_usage = 0
        self.cpu_warning_emitted = False
        self.greenlet.spawn(self.monitor_cpu).link_exception(greenlet_exception_handler)
        self.exceptions = {}
        self.target_user_count = None
        
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
    def user_classes(self):
        return self.environment.user_classes
    
    @property
    def stats(self) -> RequestStats:
        return self.environment.stats
    
    @property
    def errors(self):
        return self.stats.errors
    
    @property
    def user_count(self):
        """
        :returns: Number of currently running users
        """
        return len(self.user_greenlets)

    def cpu_log_warning(self):
        """Called at the end of the test to repeat the warning & return the status"""
        if self.cpu_warning_emitted:
            logger.warning("CPU usage was too high at some point during the test! See https://docs.locust.io/en/stable/running-locust-distributed.html for how to distribute the load over multiple CPU cores or machines")
            return True
        return False

    def weight_users(self, amount):
        """
        Distributes the amount of users for each WebLocust-class according to it's weight
        returns a list "bucket" with the weighted users
        """
        bucket = []
        weight_sum = sum([user.weight for user in self.user_classes])
        residuals = {}
        for user in self.user_classes:
            if self.environment.host is not None:
                user.host = self.environment.host

            # create users depending on weight
            percent = user.weight / float(weight_sum)
            num_users = int(round(amount * percent))
            bucket.extend([user for x in range(num_users)])
            # used to keep track of the amount of rounding was done if we need
            # to add/remove some instances from bucket
            residuals[user] = amount * percent - round(amount * percent)
        if len(bucket) < amount:
            # We got too few User classes in the bucket, so we need to create a few extra users,
            # and we do this by iterating over each of the User classes - starting with the one
            # where the residual from the rounding was the largest - and creating one of each until
            # we get the correct amount
            for user in [l for l, r in sorted(residuals.items(), key=lambda x:x[1], reverse=True)][:amount-len(bucket)]:
                bucket.append(user)
        elif len(bucket) > amount:
            # We've got too many users due to rounding errors so we need to remove some
            for user in [l for l, r in sorted(residuals.items(), key=lambda x:x[1])][:len(bucket)-amount]:
                bucket.remove(user)

        return bucket

    def spawn_users(self, spawn_count, hatch_rate, wait=False):
        bucket = self.weight_users(spawn_count)
        spawn_count = len(bucket)
        if self.state == STATE_INIT or self.state == STATE_STOPPED:
            self.state = STATE_HATCHING
        
        existing_count = len(self.user_greenlets)
        logger.info("Hatching and swarming %i users at the rate %g users/s (%i users already running)..." % (spawn_count, hatch_rate, existing_count))
        occurrence_count = dict([(l.__name__, 0) for l in self.user_classes])
        
        def hatch():
            sleep_time = 1.0 / hatch_rate
            while True:
                if not bucket:
                    logger.info("All users hatched: %s (%i already running)" % (
                        ", ".join(["%s: %d" % (name, count) for name, count in occurrence_count.items()]), 
                        existing_count,
                    ))
                    self.environment.events.hatch_complete.fire(user_count=len(self.user_greenlets))
                    return

                user_class = bucket.pop(random.randint(0, len(bucket)-1))
                occurrence_count[user_class.__name__] += 1
                new_user = user_class(self.environment)
                new_user.start(self.user_greenlets)
                if len(self.user_greenlets) % 10 == 0:
                    logger.debug("%i users hatched" % len(self.user_greenlets))
                if bucket:
                    gevent.sleep(sleep_time)
        
        hatch()
        if wait:
            self.user_greenlets.join()
            logger.info("All users stopped\n")

    def stop_users(self, user_count):
        """
        Stop a stop_count of weighted users from the Group() object in self.users
        """
        bucket = self.weight_users(user_count)
        user_count = len(bucket)
        logger.info("Stopping %i users" % user_count)
        to_stop = []
        for g in self.user_greenlets:
            for l in bucket:
                user = g.args[0]
                if l == type(user):
                    to_stop.append(user)
                    bucket.remove(l)
                    break
        self.stop_user_instances(to_stop)
        self.environment.events.hatch_complete.fire(user_count=self.user_count)
    
    
    def stop_user_instances(self, users):
        if self.environment.stop_timeout:
            stopping = Group()
            for user in users:
                if not user.stop(self.user_greenlets, force=False):
                    # User.stop() returns False if the greenlet was not stopped, so we'll need
                    # to add it's greenlet to our stopping Group so we can wait for it to finish it's task
                    stopping.add(user._greenlet)
            if not stopping.join(timeout=self.environment.stop_timeout):
                logger.info("Not all users finished their tasks & terminated in %s seconds. Stopping them..." % self.environment.stop_timeout)
            stopping.kill(block=True)
        else:
            for user in users:
                user.stop(self.user_greenlets, force=True)
        
    def monitor_cpu(self):
        process = psutil.Process()
        while True:
            self.current_cpu_usage = process.cpu_percent()
            if self.current_cpu_usage > 90 and not self.cpu_warning_emitted:
                logging.warning("CPU usage above 90%! This may constrain your throughput and may even give inconsistent response time measurements! See https://docs.locust.io/en/stable/running-locust-distributed.html for how to distribute the load over multiple CPU cores or machines")
                self.cpu_warning_emitted = True
            gevent.sleep(CPU_MONITOR_INTERVAL)

    def start(self, user_count, hatch_rate, wait=False):
        """
        Start running a load test
        
        :param user_count: Number of users to start
        :param hatch_rate: Number of users to spawn per second
        :param wait: If True calls to this method will block until all users are spawned.
                     If False (the default), a greenlet that spawns the users will be 
                     started and the call to this method will return immediately.
        """
        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            self.stats.clear_all()
            self.exceptions = {}
            self.cpu_warning_emitted = False
            self.worker_cpu_warning_emitted = False
            self.target_user_count = user_count

        # Dynamically changing the user count
        if self.state != STATE_INIT and self.state != STATE_STOPPED:
            self.state = STATE_HATCHING
            if self.user_count > user_count:
                # Stop some users
                stop_count = self.user_count - user_count
                self.stop_users(stop_count)
            elif self.user_count < user_count:
                # Spawn some users
                spawn_count = user_count - self.user_count
                self.spawn_users(spawn_count=spawn_count, hatch_rate=hatch_rate)
            else:
                self.environment.events.hatch_complete.fire(user_count=self.user_count)
        else:
            self.hatch_rate = hatch_rate
            self.spawn_users(user_count, hatch_rate=hatch_rate, wait=wait)

    def start_stepload(self, user_count, hatch_rate, step_user_count, step_duration):
        if user_count < step_user_count:
            logger.error("Invalid parameters: total user count of %d is smaller than step user count of %d" % (user_count, step_user_count))
            return
        self.total_users = user_count
        
        if self.stepload_greenlet:
            logger.info("There is an ongoing swarming in Step Load mode, will stop it now.")
            self.stepload_greenlet.kill()
        logger.info("Start a new swarming in Step Load mode: total user count of %d, hatch rate of %d, step user count of %d, step duration of %d " % (user_count, hatch_rate, step_user_count, step_duration))
        self.state = STATE_INIT
        self.stepload_greenlet = self.greenlet.spawn(self.stepload_worker, hatch_rate, step_user_count, step_duration)
        self.stepload_greenlet.link_exception(greenlet_exception_handler)

    def stepload_worker(self, hatch_rate, step_users_growth, step_duration):
        current_num_users = 0
        while self.state == STATE_INIT or self.state == STATE_HATCHING or self.state == STATE_RUNNING:
            current_num_users += step_users_growth
            if current_num_users > int(self.total_users):
                logger.info('Step Load is finished.')
                break
            self.start(current_num_users, hatch_rate)
            logger.info('Step loading: start hatch job of %d user.' % (current_num_users))
            gevent.sleep(step_duration)

    def stop(self):
        """
        Stop a running load test by stopping all running users
        """
        self.state = STATE_CLEANUP
        # if we are currently hatching users we need to kill the hatching greenlet first
        if self.hatching_greenlet and not self.hatching_greenlet.ready():
            self.hatching_greenlet.kill(block=True)
        self.stop_user_instances([g.args[0] for g in self.user_greenlets])
        self.state = STATE_STOPPED
        self.cpu_log_warning()
    
    def quit(self):
        """
        Stop any running load test and kill all greenlets for the runner
        """
        self.stop()
        self.greenlet.kill(block=True)

    def log_exception(self, node_id, msg, formatted_tb):
        key = hash(formatted_tb)
        row = self.exceptions.setdefault(key, {"count": 0, "msg": msg, "traceback": formatted_tb, "nodes": set()})
        row["count"] += 1
        row["nodes"].add(node_id)
        self.exceptions[key] = row


class LocalRunner(Runner):
    """
    Runner for running single process load test
    """
    def __init__(self, environment):
        """
        :param environment: Environment instance
        """
        super(LocalRunner, self).__init__(environment)

        # register listener thats logs the exception for the local runner
        def on_user_error(user_instance, exception, tb):
            formatted_tb = "".join(traceback.format_tb(tb))
            self.log_exception("local", str(exception), formatted_tb)
        self.environment.events.user_error.add_listener(on_user_error)

    def start(self, user_count, hatch_rate, wait=False):
        self.target_user_count = user_count
        if hatch_rate > 100:
            logger.warning("Your selected hatch rate is very high (>100), and this is known to sometimes cause issues. Do you really need to ramp up that fast?")
        
        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            # if we're not already running we'll fire the test_start event
            self.environment.events.test_start.fire(environment=self.environment)
        
        if self.hatching_greenlet:
            # kill existing hatching_greenlet before we start a new one
            self.hatching_greenlet.kill(block=True)
        self.hatching_greenlet = self.greenlet.spawn(lambda: super(LocalRunner, self).start(user_count, hatch_rate, wait=wait))
        self.hatching_greenlet.link_exception(greenlet_exception_handler)
    
    def stop(self):
        if self.state == STATE_STOPPED:
            return
        super().stop()
        self.environment.events.test_stop.fire(environment=self.environment)


class DistributedRunner(Runner):
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

class MasterRunner(DistributedRunner):
    """
    Runner used to run distributed load tests across multiple processes and/or machines.
    
    MasterRunner doesn't spawn any user greenlets itself. Instead it expects
    :class:`WorkerRunners <WorkerRunner>` to connect to it, which it will then direct
    to start and stop user greenlets. Stats sent back from the
    :class:`WorkerRunners <WorkerRunner>` will aggregated.
    """
    def __init__(self, environment, master_bind_host, master_bind_port):
        """
        :param environment: Environment instance
        :param master_bind_host: Host/interface to use for incoming worker connections
        :param master_bind_port: Port to use for incoming worker connections
        """
        super().__init__(environment)
        self.worker_cpu_warning_emitted = False
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

            @property
            def missing(self):
                return self.get_by_state(STATE_MISSING)
        
        self.clients = WorkerNodesDict()
        try:
            self.server = rpc.Server(master_bind_host, master_bind_port)
        except RPCError as e:
            if e.args[0] == "Socket bind failure: Address already in use":
                port_string = master_bind_host + ":" + master_bind_port if master_bind_host != "*" else master_bind_port
                logger.error(f"The Locust master port ({port_string}) was busy. Close any applications using that port - perhaps an old instance of Locust master is still running? ({e.args[0]})")
                sys.exit(1)
            else:
                raise

        self.greenlet.spawn(self.heartbeat_worker).link_exception(greenlet_exception_handler)
        self.greenlet.spawn(self.client_listener).link_exception(greenlet_exception_handler)

        # listener that gathers info on how many users the worker has spawned
        def on_worker_report(client_id, data):
            if client_id not in self.clients:
                logger.info("Discarded report from unrecognized worker %s", client_id)
                return

            self.clients[client_id].user_count = data["user_count"]
        self.environment.events.worker_report.add_listener(on_worker_report)
        
        # register listener that sends quit message to worker nodes
        def on_quitting(environment, **kw):
            self.quit()
        self.environment.events.quitting.add_listener(on_quitting)
    
    @property
    def user_count(self):
        return sum([c.user_count for c in self.clients.values()])
    
    def cpu_log_warning(self):
        warning_emitted = Runner.cpu_log_warning(self)
        if self.worker_cpu_warning_emitted:
            logger.warning("CPU usage threshold was exceeded on workers during the test!")
            warning_emitted = True
        return warning_emitted

    def start(self, user_count, hatch_rate):
        self.target_user_count = user_count
        num_workers = len(self.clients.ready) + len(self.clients.running) + len(self.clients.hatching)
        if not num_workers:
            logger.warning("You are running in distributed mode but have no worker servers connected. "
                           "Please connect workers prior to swarming.")
            return

        self.hatch_rate = hatch_rate
        worker_num_users = user_count // (num_workers or 1)
        worker_hatch_rate = float(hatch_rate) / (num_workers or 1)
        remaining = user_count % num_workers

        logger.info("Sending hatch jobs of %d users and %.2f hatch rate to %d ready clients" % (worker_num_users, worker_hatch_rate, num_workers))

        if worker_hatch_rate > 100:
            logger.warning("Your selected hatch rate is very high (>100/worker), and this is known to sometimes cause issues. Do you really need to ramp up that fast?")

        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            self.stats.clear_all()
            self.exceptions = {}
            self.environment.events.test_start.fire(environment=self.environment)
        
        for client in (self.clients.ready + self.clients.running + self.clients.hatching):
            data = {
                "hatch_rate": worker_hatch_rate,
                "num_users": worker_num_users,
                "host": self.environment.host,
                "stop_timeout": self.environment.stop_timeout,
            }

            if remaining > 0:
                data["num_users"] += 1
                remaining -= 1

            self.server.send_to_client(Message("hatch", data, client.id))
        
        self.state = STATE_HATCHING

    def stop(self):
        if self.state not in [STATE_INIT, STATE_STOPPED, STATE_STOPPING]:
            self.state = STATE_STOPPING
            for client in self.clients.all:
                self.server.send_to_client(Message("stop", None, client.id))
            self.environment.events.test_stop.fire(environment=self.environment)
    
    def quit(self):
        if self.state not in [STATE_INIT, STATE_STOPPED, STATE_STOPPING]:
            # fire test_stop event if state isn't already stopped
            self.environment.events.test_stop.fire(environment=self.environment)
            
        for client in self.clients.all:
            self.server.send_to_client(Message("quit", None, client.id))
        gevent.sleep(0.5) # wait for final stats report from all workers
        self.greenlet.kill(block=True)

    def check_stopped(self):
        if not self.state == STATE_INIT and all(map(lambda x: x.state != STATE_RUNNING and x.state != STATE_HATCHING, self.clients.all)):
            self.state = STATE_STOPPED

    
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
                    if self.worker_count - len(self.clients.missing) <= 0:
                        logger.info("The last worker went missing, stopping test.")
                        self.stop()
                        self.check_stopped()
                else:
                    client.heartbeat -= 1

    def reset_connection(self):
        logger.info("Reset connection to worker")
        try:
            self.server.close()
            self.server = rpc.Server(self.master_bind_host, self.master_bind_port)
        except RPCError as e:
            logger.error("Temporary failure when resetting connection: %s, will retry later." % ( e ) )

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
                    if self.worker_count - len(self.clients.missing) <= 0:
                        logger.info("The last worker quit, stopping test.")
                        self.stop()
                        if self.environment.parsed_options and self.environment.parsed_options.headless:
                            self.quit()
            elif msg.type == "exception":
                self.log_exception(msg.node_id, msg.data["msg"], msg.data["traceback"])

            self.check_stopped()


    @property
    def worker_count(self):
        return len(self.clients.ready) + len(self.clients.hatching) + len(self.clients.running)

class WorkerRunner(DistributedRunner):
    """
    Runner used to run distributed load tests across multiple processes and/or machines.
    
    WorkerRunner connects to a :class:`MasterRunner` from which it'll receive
    instructions to start and stop user greenlets. The WorkerRunner will periodically
    take the stats generated by the running users and send back to the :class:`MasterRunner`.
    """
    
    def __init__(self, environment, master_host, master_port):
        """
        :param environment: Environment instance
        :param master_host: Host/IP to use for connection to the master
        :param master_port: Port to use for connecting to the master
        """
        super().__init__(environment)
        self.worker_state = STATE_INIT
        self.client_id = socket.gethostname() + "_" + uuid4().hex
        self.master_host = master_host
        self.master_port = master_port
        self.client = rpc.Client(master_host, master_port, self.client_id)
        self.greenlet.spawn(self.heartbeat).link_exception(greenlet_exception_handler)
        self.greenlet.spawn(self.worker).link_exception(greenlet_exception_handler)
        self.client.send(Message("client_ready", None, self.client_id))
        self.greenlet.spawn(self.stats_reporter).link_exception(greenlet_exception_handler)
        
        # register listener for when all users have hatched, and report it to the master node
        def on_hatch_complete(user_count):
            self.client.send(Message("hatch_complete", {"count":user_count}, self.client_id))
            self.worker_state = STATE_RUNNING
        self.environment.events.hatch_complete.add_listener(on_hatch_complete)
        
        # register listener that adds the current number of spawned users to the report that is sent to the master node
        def on_report_to_master(client_id, data):
            data["user_count"] = self.user_count
        self.environment.events.report_to_master.add_listener(on_report_to_master)
        
        # register listener that sends quit message to master
        def on_quitting(environment, **kw):
            self.client.send(Message("quit", None, self.client_id))
        self.environment.events.quitting.add_listener(on_quitting)

        # register listener thats sends user exceptions to master
        def on_user_error(user_instance, exception, tb):
            formatted_tb = "".join(traceback.format_tb(tb))
            self.client.send(Message("exception", {"msg" : str(exception), "traceback" : formatted_tb}, self.client_id))
        self.environment.events.user_error.add_listener(on_user_error)

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
                self.target_user_count = job["num_users"]
                self.environment.host = job["host"]
                self.environment.stop_timeout = job["stop_timeout"]
                if self.hatching_greenlet:
                    # kill existing hatching greenlet before we launch new one
                    self.hatching_greenlet.kill(block=True)
                self.hatching_greenlet = self.greenlet.spawn(lambda: self.start(user_count=job["num_users"], hatch_rate=job["hatch_rate"]))
                self.hatching_greenlet.link_exception(greenlet_exception_handler)
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
