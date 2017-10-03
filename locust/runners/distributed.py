"""Abstract runners implementation"""
from locust.stats import global_stats

class STATE(object):
    INIT = 'ready'
    HATCHING = 'hatching'
    RUNNING = 'running'
    STOPPED = 'stopped'


class Node(object):
    def __init__(self, id, state=STATE.INIT):
        self.id = id
        self.state = state
        self.user_count = 0
        self.ping_answ = True
        self.worker_count = 0
        self.task = None


class NodesDict(dict):
    def get_by_state(self, state):
        return [c for c in self.itervalues() if c.state == state]

    @property
    def ready(self):
        return self.get_by_state(STATE.INIT)

    @property
    def hatching(self):
        return self.get_by_state(STATE.HATCHING)

    @property
    def running(self):
        return self.get_by_state(STATE.RUNNING)


class DistributedLocustRunner(object):
    def __init__(self, locust_classes, options):
        self.state = STATE.INIT
        self.locust_classes = locust_classes
        self.options = options
        self.stats = global_stats
        self.master_host = options.master_host
        self.master_port = options.master_port
        self.master_bind_host = options.master_bind_host
        self.master_bind_port = options.master_bind_port

    def noop(self, *args, **kwargs):
        """ Used to link() greenlets to in order to be compatible with gevent 1.0 """
        pass
