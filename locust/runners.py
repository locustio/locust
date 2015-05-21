# coding=UTF-8
import socket
import traceback
import warnings
import random
import logging
import collections
from time import time
from hashlib import md5

import gevent
from gevent import GreenletExit
from gevent.pool import Group

import events
from stats import global_stats

from rpc import rpc, Message

logger = logging.getLogger(__name__)

# global locust runner singleton
locust_runner = None

STATE_INIT, STATE_HATCHING, STATE_RUNNING, STATE_STOPPED = ["ready", "hatching", "running", "stopped"]
SLAVE_REPORT_INTERVAL = 3.0


class LocustIdTracker(object):

    class LocustIdAssigner(object):

        def __init__(self):
            self.free_ids = []
            self.assigned_ids = []
            self.total_ids = 0

        def request_ids(self, count):
            if count > len(self.free_ids):
                # If we don't have enough free ids, create more.
                num_ids_to_add = count - len(self.free_ids)
                self.free_ids.extend(range(self.total_ids, self.total_ids + num_ids_to_add))
                self.total_ids = self.total_ids + num_ids_to_add
            assigning_ids = self.free_ids[:count]
            self.free_ids = self.free_ids[count:]
            self.assigned_ids.extend(assigning_ids)
            self.assigned_ids.sort()
            return assigning_ids

        def release_ids(self, ids):
            for id in ids:
                self.assigned_ids.remove(id)
                self.free_ids.append(id)
            self.free_ids.sort()

        def release_id(self, id):
            self.assigned_ids.remove(id)
            self.free_ids.append(id)
            self.free_ids.sort()

    class LocustSlaveIdTracker(object):

        def __init__(self, locust_classes):
            self.ids = {}
            for locust_class in locust_classes:
                self.ids[locust_class] = []

        def count_for_class(self, locust_class):
            return len(self.ids[locust_class])

        def allocate_ids(self, locust_class, ids):
            self.ids[locust_class].extend(ids)
            self.ids[locust_class].sort()

        def free_ids(self, locust_class, ids):
            for id in ids[locust_class]:
                self.ids[locust_class].remove(id)

        def release_ids(self, locust_class, count):
            released_ids = self.ids[locust_class][count:]
            self.ids[locust_class] = self.ids[locust_class][:count]
            return released_ids

    def __init__(self, slave_count, locust_classes):
        self.locust_id_assigners = {}
        for locust_class in locust_classes:
            self.locust_id_assigners[locust_class] = LocustIdTracker.LocustIdAssigner()
        self.slave_trackers = [LocustIdTracker.LocustSlaveIdTracker(locust_classes) for _ in range(slave_count)]
        self.locust_classes = locust_classes

    def set_user_count(self, count):
        users_per_slave = count / len(self.slave_trackers)
        total_weight = sum(locust_class.weight for locust_class in self.locust_classes)
        locusts_per_slave = {}
        for locust_class in self.locust_classes:
            locusts_per_slave[locust_class] = int(round(locust_class.weight / float(total_weight) * users_per_slave))
        slave_changes = []
        for slave_tracker in self.slave_trackers:
            locust_changes = {}
            for locust_class, count in locusts_per_slave.iteritems():
                locust_count_difference = count - slave_tracker.count_for_class(locust_class)
                if locust_count_difference > 0:
                    # allocate more ids
                    allocated_ids = self.locust_id_assigners[locust_class].request_ids(locust_count_difference)
                    slave_tracker.allocate_ids(locust_class, allocated_ids)
                    locust_changes[locust_class.__name__] = {'type': 'increase', 'ids': allocated_ids}
                elif locust_count_difference < 0:
                    # release ids
                    released_ids = slave_tracker.release_ids(locust_class, locust_count_difference)
                    self.locust_id_assigners[locust_class].release_ids(released_ids)
                    locust_changes[locust_class.__name__] = {'type': 'decrease', 'ids': released_ids}
                #else: pass # No change!
            slave_changes.append(locust_changes)
        return slave_changes


class LocustRunner(object):
    def __init__(self, locust_classes, options):
        self.locust_classes = locust_classes
        self.hatch_rate = options.hatch_rate
        self.num_clients = options.num_clients
        self.num_requests = options.num_requests
        self.host = options.host
        self.locusts = Group()
        self.state = STATE_INIT
        self.hatching_greenlet = None
        self.exceptions = {}
        self.stats = global_stats
        self.id_tracker = None

        # register listener that resets stats when hatching is complete
        def on_hatch_complete(user_count):
            self.state = STATE_RUNNING
            #logger.info("Resetting stats\n")
            #self.stats.reset_all()
        events.hatch_complete += on_hatch_complete

    @property
    def request_stats(self):
        return self.stats.entries

    @property
    def errors(self):
        return self.stats.errors

    @property
    def user_count(self):
        return len(self.locusts)

    def weight_locusts(self, amount, stop_timeout = None):
        """
        Distributes the amount of locusts for each WebLocust-class according to it's weight
        returns a list "bucket" with the weighted locusts
        """
        bucket = []
        weight_sum = sum((locust.weight for locust in self.locust_classes if locust.task_set))
        for locust in self.locust_classes:
            if not locust.task_set:
                warnings.warn("Notice: Found Locust class (%s) got no task_set. Skipping..." % locust.__name__)
                continue

            if self.host is not None:
                locust.host = self.host
            if stop_timeout is not None:
                locust.stop_timeout = stop_timeout

            # create locusts depending on weight
            percent = locust.weight / float(weight_sum)
            num_locusts = int(round(amount * percent))
            bucket.extend([locust for x in xrange(0, num_locusts)])
        return bucket

    def spawn_locusts(self, spawn_count=None, stop_timeout=None, wait=False, id_changes={}):
        if spawn_count is None:
            spawn_count = self.num_clients

        if self.num_requests is not None:
            self.stats.max_requests = self.num_requests

        bucket = self.weight_locusts(spawn_count, stop_timeout)
        spawn_count = len(bucket)
        if self.state == STATE_INIT or self.state == STATE_STOPPED:
            self.state = STATE_HATCHING
            self.num_clients = spawn_count
        else:
            self.num_clients += spawn_count

        logger.info("Hatching and swarming %i clients at the rate %g clients/s..." % (spawn_count, self.hatch_rate))
        occurence_count = dict([(l.__name__, 0) for l in self.locust_classes])

        def hatch():
            sleep_time = 1.0 / self.hatch_rate
            while True:
                if bucket:
                    locust = bucket.pop(random.randint(0, len(bucket)-1))
                    occurence_count[locust.__name__] += 1
                    id_change = id_changes[locust.__name__]

                if not bucket:
                    logger.info("All locusts hatched: %s" % ", ".join(["%s: %d" % (name, count) for name, count in occurence_count.iteritems()]))
                    events.hatch_complete.fire(user_count=self.num_clients)

                def start_locust(_, id):
                    try:
                        if locust.__init__.__func__.func_code.co_argcount > 1:
                            instance = locust(id)
                        else:
                            instance = locust()
                        instance.run()
                    except GreenletExit:
                        instance.die()
                        pass
                new_locust = self.locusts.spawn(start_locust, locust, id_change['ids'].pop())
                if len(self.locusts) % 10 == 0:
                    logger.debug("%i locusts hatched" % len(self.locusts))

                if not bucket:
                    return

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
        self.num_clients -= kill_count
        logger.info("Killing %i locusts" % kill_count)
        dying = []
        for g in self.locusts:
            for l in bucket:
                if l == g.args[0]:
                    dying.append(g)
                    bucket.remove(l)
                    break
        for g in dying:
            self.locusts.killone(g)
        events.hatch_complete.fire(user_count=self.num_clients)

    def start_hatching(self, locust_count=None, hatch_rate=None, wait=False, id_changes={}):
        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            self.stats.clear_all()
            self.stats.start_time = time()
            self.exceptions = {}
            events.locust_start_hatching.fire()

        # Dynamically changing the locust count
        if self.state != STATE_INIT and self.state != STATE_STOPPED:
            self.state = STATE_HATCHING
            if self.num_clients > locust_count:
                # Kill some locusts
                kill_count = self.num_clients - locust_count
                self.kill_locusts(kill_count)
            elif self.num_clients < locust_count:
                # Spawn some locusts
                if hatch_rate:
                    self.hatch_rate = hatch_rate
                spawn_count = locust_count - self.num_clients
                self.spawn_locusts(spawn_count=spawn_count, id_changes=id_changes)
            else:
                events.hatch_complete.fire(user_count=self.num_clients)
        else:
            if hatch_rate:
                self.hatch_rate = hatch_rate
            if locust_count is not None:
                self.spawn_locusts(locust_count, wait=wait, id_changes=id_changes)
            else:
                self.spawn_locusts(wait=wait, id_changes=id_changes)

    def stop(self):
        # if we are currently hatching locusts we need to kill the hatching greenlet first
        if self.id_tracker != None:
            self.id_tracker.set_user_count(0)
        if self.hatching_greenlet and not self.hatching_greenlet.ready():
            self.hatching_greenlet.kill(block=True)
        self.state = STATE_STOPPED
        events.locust_stop_hatching.fire()
        events.stopping.fire()
        self.locusts.kill(block=True)

    def log_exception(self, node_id, msg, formatted_tb):
        key = hash(formatted_tb)
        row = self.exceptions.setdefault(key, {"count": 0, "msg": msg, "traceback": formatted_tb, "nodes": set()})
        row["count"] += 1
        row["nodes"].add(node_id)
        self.exceptions[key] = row

class LocalLocustRunner(LocustRunner):
    def __init__(self, locust_classes, options):
        super(LocalLocustRunner, self).__init__(locust_classes, options)

        # register listener thats logs the exception for the local runner
        def on_locust_error(locust_instance, exception, tb, **kwargs):
            formatted_tb = "".join(traceback.format_tb(tb))
            self.log_exception("local", str(exception), formatted_tb)
        events.locust_error += on_locust_error

    def start_hatching(self, locust_count=None, hatch_rate=None, wait=False):
        if self.id_tracker == None:
            self.id_tracker = LocustIdTracker(1, self.locust_classes)
        id_changes = self.id_tracker.set_user_count(locust_count)
        self.hatching_greenlet = gevent.spawn(lambda: super(LocalLocustRunner, self).start_hatching(locust_count, hatch_rate, wait=wait, id_changes=id_changes[0]))
        self.greenlet = self.hatching_greenlet

class DistributedLocustRunner(LocustRunner):
    def __init__(self, locust_classes, options):
        super(DistributedLocustRunner, self).__init__(locust_classes, options)
        self.master_host = options.master_host
        self.master_port = options.master_port
        self.master_bind_host = options.master_bind_host
        self.master_bind_port = options.master_bind_port

    def noop(self, *args, **kwargs):
        """ Used to link() greenlets to in order to be compatible with gevent 1.0 """
        pass

class SlaveNode(object):
    def __init__(self, id, state=STATE_INIT):
        self.id = id
        self.state = state
        self.user_count = 0


class MasterLocustRunner(DistributedLocustRunner):

    def __init__(self, locust_classes, options, *args, **kwargs):
        super(MasterLocustRunner, self).__init__(locust_classes, options, *args, **kwargs)

        class SlaveNodesDict(dict):
            def get_by_state(self, state):
                return [c for c in self.itervalues() if c.state == state]

            @property
            def ready(self):
                return self.get_by_state(STATE_INIT)

            @property
            def hatching(self):
                return self.get_by_state(STATE_HATCHING)

            @property
            def running(self):
                return self.get_by_state(STATE_RUNNING)

        self.clients = SlaveNodesDict()
        self.server = rpc.Server(self.master_bind_host, self.master_bind_port)
        self.greenlet = Group()
        self.greenlet.spawn(self.client_listener).link_exception(callback=self.noop)

        # listener that gathers info on how many locust users the slaves has spawned
        def on_slave_report(client_id, data):
            if client_id not in self.clients:
                logger.info("Discarded report from unrecognized slave %s", client_id)
                return

            self.clients[client_id].user_count = data["user_count"]
        events.slave_report += on_slave_report

        # register listener that sends quit message to slave nodes
        def on_quitting():
            self.quit()
        events.quitting += on_quitting

    @property
    def user_count(self):
        return sum([c.user_count for c in self.clients.itervalues()])

    def start_hatching(self, locust_count, hatch_rate):
        num_slaves = len(self.clients.ready) + len(self.clients.running)
        if self.id_tracker == None:
            self.id_tracker = LocustIdTracker(num_slaves, self.locust_classes)
        if not num_slaves:
            logger.warning("You are running in distributed mode but have no slave servers connected. "
                           "Please connect slaves prior to swarming.")
            return

        id_changes = self.id_tracker.set_user_count(locust_count)
        self.num_clients = locust_count
        slave_num_clients = locust_count / (num_slaves or 1)
        slave_hatch_rate = float(hatch_rate) / (num_slaves or 1)
        remaining = locust_count % num_slaves

        logger.info("Sending hatch jobs to %d ready clients", num_slaves)

        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            self.stats.clear_all()
            self.exceptions = {}
            events.master_start_hatching.fire()

        count = 0
        sorted_keys = sorted(self.clients.keys())
        for client_key in sorted_keys:
            client = self.clients[client_key]
            data = {
                "hatch_rate":slave_hatch_rate,
                "num_clients":slave_num_clients,
                "num_requests": self.num_requests,
                "host":self.host,
                "stop_timeout":None,
                "id_changes":id_changes[count]
            }
            count = count + 1

            if remaining > 0:
                data["num_clients"] += 1
                remaining -= 1

            self.server.send(Message("hatch", data, None))

        self.stats.start_time = time()
        self.state = STATE_HATCHING

    def stop(self):
        self.id_tracker.set_user_count(0)
        for client in self.clients.hatching + self.clients.running:
            self.server.send(Message("stop", None, None))
        events.master_stop_hatching.fire()
        events.stopping.fire()

    def quit(self):
        if self.state != STATE_STOPPED:
            events.stopping.fire()
            self.state = STATE_STOPPED
        for client in self.clients.itervalues():
            self.server.send(Message("quit", None, None))
        self.greenlet.kill(block=True)

    def client_listener(self):
        while True:
            msg = self.server.recv()
            if msg.type == "client_ready":
                id = msg.node_id
                self.clients[id] = SlaveNode(id)
                logger.info("Client %r reported as ready. Currently %i clients ready to swarm." % (id, len(self.clients.ready)))
                ## emit a warning if the slave's clock seem to be out of sync with our clock
                #if abs(time() - msg.data["time"]) > 5.0:
                #    warnings.warn("The slave node's clock seem to be out of sync. For the statistics to be correct the different locust servers need to have synchronized clocks.")
            elif msg.type == "client_stopped":
                del self.clients[msg.node_id]
                if len(self.clients.hatching + self.clients.running) == 0:
                    self.state = STATE_STOPPED
                logger.info("Removing %s client from running clients" % (msg.node_id))
            elif msg.type == "stats":
                events.slave_report.fire(client_id=msg.node_id, data=msg.data)
            elif msg.type == "hatching":
                self.clients[msg.node_id].state = STATE_HATCHING
            elif msg.type == "hatch_complete":
                self.clients[msg.node_id].state = STATE_RUNNING
                self.clients[msg.node_id].user_count = msg.data["count"]
                if len(self.clients.hatching) == 0:
                    count = sum(c.user_count for c in self.clients.itervalues())
                    events.hatch_complete.fire(user_count=count)
            elif msg.type == "quit":
                if msg.node_id in self.clients:
                    del self.clients[msg.node_id]
                    logger.info("Client %r quit. Currently %i clients connected." % (msg.node_id, len(self.clients.ready)))
            elif msg.type == "exception":
                self.log_exception(msg.node_id, msg.data["msg"], msg.data["traceback"])
            elif msg.type == "relay":
                # broadcast to all slaves cannot be helped - the slave will filter out its own message
                    self.server.send(Message("relay", msg.data, msg.node_id))


    @property
    def slave_count(self):
        return len(self.clients.ready) + len(self.clients.hatching) + len(self.clients.running)

class SlaveLocustRunner(DistributedLocustRunner):
    def __init__(self, *args, **kwargs):
        super(SlaveLocustRunner, self).__init__(*args, **kwargs)
        self.client_id = socket.gethostname() + "_" + md5(str(time() + random.randint(0,10000))).hexdigest()

        self.client = rpc.Client(self.master_host, self.master_port)
        self.greenlet = Group()

        self.greenlet.spawn(self.worker).link_exception(callback=self.noop)
        self.client.send(Message("client_ready", None, self.client_id))
        self.greenlet.spawn(self.stats_reporter).link_exception(callback=self.noop)

        # register listener for when all locust users have hatched, and report it to the master node
        def on_hatch_complete(user_count):
            self.client.send(Message("hatch_complete", {"count":user_count}, self.client_id))
        events.hatch_complete += on_hatch_complete

        # register listener that adds the current number of spawned locusts to the report that is sent to the master node
        def on_report_to_master(client_id, data):
            data["user_count"] = self.user_count
        events.report_to_master += on_report_to_master

        # register listener that sends quit message to master
        def on_quitting():
            self.client.send(Message("quit", None, self.client_id))
        events.quitting += on_quitting

        # register listener thats sends locust exceptions to master
        def on_locust_error(locust_instance, exception, tb):
            formatted_tb = "".join(traceback.format_tb(tb))
            self.client.send(Message("exception", {"msg" : str(exception), "traceback" : formatted_tb}, self.client_id))
        events.locust_error += on_locust_error

    def worker(self):
        while True:
            msg = self.client.recv()
            if msg.type == "hatch":
                self.client.send(Message("hatching", None, self.client_id))
                job = msg.data
                self.hatch_rate = job["hatch_rate"]
                #self.num_clients = job["num_clients"]
                self.num_requests = job["num_requests"]
                self.host = job["host"]
                self.hatching_greenlet = gevent.spawn(lambda: self.start_hatching(locust_count=job["num_clients"], hatch_rate=job["hatch_rate"], id_changes=job['id_changes']))
            elif msg.type == "stop":
                self.stop()
                self.client.send(Message("client_stopped", None, self.client_id))
                self.client.send(Message("client_ready", None, self.client_id))
            elif msg.type == "quit":
                logger.info("Got quit message from master, shutting down...")
                if self.state != STATE_STOPPED:
                    self.stop()
                self.greenlet.kill(block=True)
            elif msg.type == "relay":
                if msg.node_id != self.client_id:
                    events.relay_message_available.fire(message=msg)

    def stats_reporter(self):
        while True:
            data = {}
            events.report_to_master.fire(client_id=self.client_id, data=data)
            try:
                self.client.send(Message("stats", data, self.client_id))
            except:
                logger.error("Connection lost to master server. Aborting...")
                break

            gevent.sleep(SLAVE_REPORT_INTERVAL)

    def send_relay_msg(self, data):
        """
        Send it via the master to relay to all slave locusts
        """
        self.client.send(Message("relay", data, self.client_id))
