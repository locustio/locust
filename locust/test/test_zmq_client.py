import gevent
import zmq.green as zmq

from locust.stats import global_stats
from locust.clients import ZMQClient
from .testcases import WebserverTestCase

endpoint = 'tcp://127.0.0.1:6565'

class ZMQServer(object):
    def __init__(self, endpoint):
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.SUB)
        self.receiver.bind(endpoint)
        self.receiver.setsockopt(zmq.SUBSCRIBE, '')

    def read(self):
        return self.receiver.recv()

    def close(self):
        self.receiver.close()
        self.context.term()

class Locust(object):
    current_task = "task"

class TestZMQClient(WebserverTestCase):

    def setUp(self):
        super(TestZMQClient, self).setUp()
        self.server = ZMQServer(endpoint)
        gevent.sleep(0.1)

    def tearDown(self):
        super(TestZMQClient, self).tearDown()
        self.server.close()
        self.client.close()
        gevent.sleep(0.1)

    def test_message_send(self):
        self.client = ZMQClient(Locust, endpoint)
        self.result = None
        def listen():
            self.result = self.server.read()
        greenlet = gevent.spawn(listen)
        self.client.send(['test_message'])
        greenlet.join()
        self.assertEqual('test_message', self.result)

    def test_stats_tracking(self):
        self.client = ZMQClient(Locust, endpoint)
        self.client.send(['test_message'])
        self.assertEqual(global_stats.num_requests, 1)
        self.assertIn(('task', endpoint, 'zmq-fire'), global_stats.entries.keys())
        self.assertIn(('Action Total', endpoint, 'zmq-fire'), global_stats.entries.keys())

    def test_custom_client_name(self):
        self.client = ZMQClient(Locust, endpoint, 'zmq-client')
        self.client.send(['test_message'])
        self.assertEqual(global_stats.num_requests, 1)
        self.assertIn(('task', 'zmq-client', 'zmq-fire'), global_stats.entries.keys())
        self.assertIn(('Action Total', 'zmq-client', 'zmq-fire'), global_stats.entries.keys())
