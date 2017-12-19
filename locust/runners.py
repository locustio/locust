# -*- coding: utf-8 -*-
import collections
import itertools
import logging
import numbers
import random
import socket
import traceback
import warnings
from hashlib import md5
from time import time

import gevent
import six
from gevent import GreenletExit
from gevent.pool import Group

from six.moves import filter, map, xrange, zip

from . import events
from .rpc import Message, rpc
from .stats import global_stats

logger = logging.getLogger(__name__)

# global locust runner singleton
locust_runner = None

STATE_INIT, STATE_HATCHING, STATE_RUNNING, STATE_STOPPED = ["ready", "hatching", "running", "stopped"]
SLAVE_REPORT_INTERVAL = 3.0


class LocustRunner(object):
    def __init__(self, locust_classes, options):
        # handle case of single locust class
        try:
            iter(locust_classes)
        except TypeError:
            locust_classes = [locust_classes]

        self.options = options
        self.locust_classes_by_name = {
            locust.__name__: locust for locust in locust_classes
        }

        self.hatch_rate = options.hatch_rate
        self.num_clients_by_class = collections.defaultdict(int)
        self.host = options.host
        self.locusts = Group()
        self.greenlet = self.locusts
        self.state = STATE_INIT
        self.locust_hatchers = Group()
        self.hatching_greenlet = None
        self.exceptions = {}
        self.stats = global_stats
        
        # register listener that resets stats when hatching is complete
        def on_hatch_complete(user_count):
            self.state = STATE_RUNNING
            if self.options.reset_stats:
                logger.info("Resetting stats\n")
                self.stats.reset_all()
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

    @property
    def num_clients(self):
        return sum(six.itervalues(self.num_clients_by_class))

    @num_clients.setter
    def num_clients(self, new_num_clients):
        orig = self.num_clients

        if new_num_clients == orig:
            return

        self.num_clients_by_class.update(
            self.weight_locusts_value(
                new_num_clients,
                self.num_clients_by_class if orig else None
            )
        )

    @property
    def hatch_rate(self):
        return sum(self.hatch_rates.values())

    @hatch_rate.setter
    def hatch_rate(self, value):
        self.hatch_rates = self.weight_locusts_value(float(value))

    @property
    def locust_classes(self):
        return list(self.locust_classes_by_name.values())

    def translate_locust_dict(self, d):
        """
        Translates keys in dict from locust class names to locust classes
        """
        return {
            self.locust_classes_by_name[clsname]: value
            for clsname, value in six.iteritems(d)
        }

    def weight_locusts(self, amount, stop_timeout=None):
        """
        Distributes the amount of locusts for each WebLocust-class according to it's weight
        returns a list "bucket" with the weighted locusts
        """

        if not isinstance(amount, dict):
            locust_counts = self.weight_locusts_value(int(amount))

        def gen():
            for locust, count in six.iteritems(locust_counts):
                if not locust.task_set:
                    warnings.warn("Notice: Found Locust class (%s) got no task_set. Skipping..." % locust.__name__)
                    continue

                if self.host is not None:
                    locust.host = self.host
                if stop_timeout is not None:
                    locust.stop_timeout = stop_timeout

                for _ in xrange(count):
                    yield locust

        return list(gen())

    def weight_locusts_value(self, value, weights=None):
        """
        Distribute value by locust weights

        :param value: Value to distribute by weight (int or float). If value is
                      int, the result will be rounded
        :type value: int, float
        :param weights: Dictionary of weights to use instead of locust.weight
        :type weights: dict or None
        :return: dict of locust_class -> int or locust_class -> float
                 depending on the type of `value`
        """
        fractional = isinstance(value, float)
        locust_classes = self.locust_classes

        if weights is None:
            def get_weight(locust):
                return locust.weight

        else:
            def get_weight(locust):
                return weights.get(locust, 0)

        weight_sum = float(sum(map(get_weight, locust_classes)))
        ret = {
            locust: get_weight(locust) / weight_sum * value
            for locust in locust_classes
        }

        if fractional:
            return ret

        # round all the things
        for k in ret:
            ret[k] = int(round(ret[k]))

        # compensate for rounding error by distributing it over locusts
        remainder = value - sum(six.itervalues(ret))
        inc = 1 if remainder > 0 else -1
        while remainder != 0:
            for _, (locust, __) in zip(
                    xrange(remainder), filter(lambda _, v: v, six.iteritems(ret))):
                ret[locust] += inc
                remainder -= inc

        return ret

    def _preprocess_locust_count(self, locust_count):
        if locust_count is None:
            return None

        if isinstance(locust_count, numbers.Number):
            weights = self.num_clients_by_class if self.num_clients else None
            return self.weight_locusts_value(int(locust_count), weights)

        if isinstance(locust_count, dict):
            return locust_count

        raise TypeError("Invalid type for locust count")

    def _preprocess_hatch_rate(self, hatch_rate):
        if hatch_rate is None:
            return None

        if isinstance(hatch_rate, numbers.Number):
            return self.weight_locusts_value(float(hatch_rate))

        if isinstance(hatch_rate, dict):
            return hatch_rate

        raise TypeError("Invalid type for hatch rate")

    def spawn_locusts(self, spawn_count=None, stop_timeout=None, wait=False):
        spawn_count = (
            self._preprocess_locust_count(spawn_count) or
            self.num_clients_by_class
        )

        # at this point, spawn_count is a dict of locust -> count
        # begin hatching
        if self.state == STATE_INIT or self.state == STATE_STOPPED:
            self.state = STATE_HATCHING
            self.num_clients_by_class.clear()

        for locust in spawn_count:
            self.num_clients_by_class[locust] += spawn_count[locust]

        def start_locust(locust):
            try:
                locust().run()
            except GreenletExit:
                pass

        def hatch(locust_class, hatch_rate, amount):
            sleep_time = 1.0 / hatch_rate

            logger.info(
                "Hatching and swarming %i %s clients at the rate of %g clients/s",
                amount, locust_class.__name__, hatch_rate)

            while amount > 0:
                self.locusts.spawn(start_locust, locust_class)
                amount -= 1
                gevent.sleep(sleep_time)

        for locust, count in six.iteritems(spawn_count):
            self.locust_hatchers.spawn(
                hatch, locust, self.hatch_rates[locust], count)

        self.locust_hatchers.join()
        events.hatch_complete.fire(user_count=self.num_clients)
        logger.info(
            "All locusts hatched: %s",
            ', '.join(
                '{}: {}'.format(locust_class.__name__, count)
                for locust_class, count
                in six.iteritems(self.num_clients_by_class)))

        if wait:
            self.locusts.join()
            logger.info("All locusts dead\n")

    def kill_locusts(self, kill_count):
        """
        Kill some locusts

        :param kill_count: Dict of locust class -> int or int of locusts to
                           kill
        """
        kill_count = self._preprocess_locust_count(kill_count)

        grouped_running_locusts = itertools.groupby(
            sorted(self.locusts, key=lambda locust: locust.args[0].__name__),
            lambda locust: locust.args[0]
        )

        running_locusts = {
            locust_class: list(locusts_iterable)
            for locust_class, locusts_iterable in grouped_running_locusts
        }

        for locust_class, locusts_to_kill in six.iteritems(kill_count):
            locust_instances = running_locusts.get(locust_class, [])
            locusts_to_kill = max(0, locusts_to_kill)
            locusts_to_kill = min(len(locust_instances), locusts_to_kill)

            if not locust_instances:
                continue

            for locust in random.sample(locust_instances, locusts_to_kill):
                cls = locust.args[0]
                self.locusts.killone(locust)
                self.num_clients_by_class[cls] -= 1

        events.hatch_complete.fire(user_count=self.num_clients)

    def start_hatching(self, locust_count=None, hatch_rate=None, wait=False):
        if self.state not in (STATE_RUNNING, STATE_HATCHING):
            self.stats.clear_all()
            self.stats.start_time = time()
            self.exceptions = {}
            events.locust_start_hatching.fire()

        locust_count = self._preprocess_locust_count(locust_count)
        hatch_rate = self._preprocess_hatch_rate(hatch_rate)

        if self.state in (STATE_INIT, STATE_STOPPED):
            self.hatch_rates = hatch_rate
            self.spawn_locusts(locust_count, wait=wait)

        else:
            # dynamically changing locust count
            self.state = STATE_HATCHING

            if hatch_rate:
                self.hatch_rates = hatch_rate

            if locust_count is None:
                return

            locust_count = self._preprocess_locust_count(locust_count)

            # compute kill/spawn counts
            all_locusts = set(self.num_clients_by_class) | set(locust_count)
            kill_count = {}
            spawn_count = {}
            for locust in all_locusts:
                delta = (
                    locust_count.get(locust, 0) -
                    self.num_clients_by_class.get(locust, 0)
                )

                if delta > 0:
                    spawn_count[locust] = delta
                elif delta < 0:
                    kill_count[locust] = -delta

            # target achieved, nothing to do
            if not (kill_count or spawn_count):
                events.hatch_complete.fire(user_count=self.num_clients)
                return

            # kill some
            if kill_count:
                self.kill_locusts(kill_count)

            # spawn some
            if spawn_count:
                self.hatch_rates = hatch_rate
                self.spawn_locusts(spawn_count)

    def stop(self):
        # if we are currently hatching locusts we need to kill the hatching greenlet first
        if self.hatching_greenlet and not self.hatching_greenlet.ready():
            self.hatching_greenlet.kill(block=True)

        if self.locust_hatchers:
            self.locust_hatchers.kill(block=True)

        self.locusts.kill(block=True)
        self.state = STATE_STOPPED
        events.locust_stop_hatching.fire()
    
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
    def __init__(self, locust_classes, options):
        super(LocalLocustRunner, self).__init__(locust_classes, options)

        # register listener thats logs the exception for the local runner
        def on_locust_error(locust_instance, exception, tb):
            formatted_tb = "".join(traceback.format_tb(tb))
            self.log_exception("local", str(exception), formatted_tb)
        events.locust_error += on_locust_error

    def start_hatching(self, locust_count=None, hatch_rate=None, wait=False):
        self.hatching_greenlet = gevent.spawn(lambda: super(LocalLocustRunner, self).start_hatching(locust_count, hatch_rate, wait=wait))
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
    def __init__(self, *args, **kwargs):
        super(MasterLocustRunner, self).__init__(*args, **kwargs)
        
        class SlaveNodesDict(dict):
            def get_by_state(self, state):
                return [c for c in six.itervalues(self) if c.state == state]
            
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
        return sum([c.user_count for c in six.itervalues(self.clients)])
    
    def start_hatching(self, locust_count, hatch_rate):
        num_slaves = len(self.clients.ready) + len(self.clients.running)
        if not num_slaves:
            logger.warning("You are running in distributed mode but have no slave servers connected. "
                           "Please connect slaves prior to swarming.")
            return

        locust_count = self._preprocess_locust_count(locust_count)
        hatch_rate = self._preprocess_hatch_rate(hatch_rate)

        if set(six.iterkeys(locust_count)) != set(six.iterkeys(hatch_rate)):
            raise ValueError("locust_count and hatch_rate do not have matching"
                             " locust classes")

        self.num_clients_by_class.clear()
        self.num_clients_by_class.update(locust_count)

        slave_num_clients = {}
        slave_hatch_rate = {}
        remaining = {}
        for cls, count in six.iteritems(locust_count):
            slave_num_clients[cls.__name__] = count // num_slaves
            remaining[cls.__name__] = count % num_slaves

        for cls, rate in six.iteritems(hatch_rate):
            slave_hatch_rate[cls.__name__] = rate / num_slaves

        logger.info("Sending hatch jobs to %d ready clients", num_slaves)

        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            self.stats.clear_all()
            self.exceptions = {}
            events.master_start_hatching.fire()

        for client in six.itervalues(self.clients):
            data = {
                "hatch_rate": slave_hatch_rate.copy(),
                "num_clients": slave_num_clients.copy(),
                "host": self.host,
                "stop_timeout": None
            }

            for clsname, rem in six.iteritems(remaining):
                if not rem:
                    continue

                data['num_clients'][clsname] += 1
                remaining[clsname] -= 1

            self.server.send(Message("hatch", data, None))

        self.stats.start_time = time()
        self.state = STATE_HATCHING

    def stop(self):
        for client in self.clients.hatching + self.clients.running:
            self.server.send(Message("stop", None, None))
        events.master_stop_hatching.fire()
    
    def quit(self):
        for client in six.itervalues(self.clients):
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
                    count = sum(c.user_count for c in six.itervalues(self.clients))
                    events.hatch_complete.fire(user_count=count)
            elif msg.type == "quit":
                if msg.node_id in self.clients:
                    del self.clients[msg.node_id]
                    logger.info("Client %r quit. Currently %i clients connected." % (msg.node_id, len(self.clients.ready)))
            elif msg.type == "exception":
                self.log_exception(msg.node_id, msg.data["msg"], msg.data["traceback"])

    @property
    def slave_count(self):
        return len(self.clients.ready) + len(self.clients.hatching) + len(self.clients.running)

class SlaveLocustRunner(DistributedLocustRunner):
    def __init__(self, *args, **kwargs):
        super(SlaveLocustRunner, self).__init__(*args, **kwargs)
        self.client_id = socket.gethostname() + "_" + md5(str(time() + random.randint(0,10000)).encode('utf-8')).hexdigest()
        
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

                hatch_rate = job["hatch_rate"]
                locust_count = job["num_clients"]

                if isinstance(hatch_rate, dict):
                    hatch_rate = self.translate_locust_dict(hatch_rate)

                if isinstance(locust_count, dict):
                    locust_count = self.translate_locust_dict(locust_count)

                #self.num_clients = job["num_clients"]
                self.host = job["host"]
                self.hatching_greenlet = gevent.spawn(
                    lambda: self.start_hatching(
                        locust_count=locust_count, hatch_rate=hatch_rate))
            elif msg.type == "stop":
                self.stop()
                self.client.send(Message("client_stopped", None, self.client_id))
                self.client.send(Message("client_ready", None, self.client_id))
            elif msg.type == "quit":
                logger.info("Got quit message from master, shutting down...")
                self.stop()
                self.greenlet.kill(block=True)

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
