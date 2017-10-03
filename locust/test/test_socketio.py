import socketio
import gevent
from gevent import pywsgi
from locust.clients import SocketIOClient
from locust.stats import global_stats
from locust import config
from .testcases import LocustTestCase

class SimpleSocketIOServer(object):

    def __init__(self, service=''):
        self.greenlet = None
        self.clients = []
        self.messages = []

        self.server = None
        self.sio = socketio.Server(async_mode='gevent', logger=False)

        @self.sio.on('connect', namespace=service)
        def connect(sid, environ):
            self.clients.append(sid)

        @self.sio.on('async_message', namespace=service)
        def async_message(sid, data):
            self.messages.append({'async_message': data})

        @self.sio.on('sync_message', namespace=service)
        def sync_message(sid, data):
            self.messages.append({'sync_message': data})
            self.sio.emit('reply-sync-message', room=sid, data={'key1': 'value1'})

        @self.sio.on('wait_for_message', namespace=service)
        def wait_for_message(sid, data):
            response = data[0]
            for _ in range(5):
                self.sio.emit('stub', room=sid, data={})
                self.sio.sleep(0.2)
            self.sio.emit(response, room=sid, data={'key1': 'value1'})

        @self.sio.on('wait_for_message_amount', namespace=service)
        def wait_for_message_amount(sid, amount):
            self.sio.sleep(0.2)
            for _ in range(amount):
                self.sio.emit('stub', room=sid, data={})
                self.sio.sleep(0.2)

        @self.sio.on('self_disconnect', namespace=service)
        def disconnect_message(sid, data):
            self.sio.disconnect(sid)
            self.clients.remove(sid)

        @self.sio.on('disconnect', namespace=service)
        def disconnect(sid):
            self.clients.remove(sid)

    def run(self):
        app = socketio.Middleware(self.sio)
        self.server = pywsgi.WSGIServer(('127.0.0.1', 8081), app)
        self.server.init_socket()
        self.server.start()

    def stop(self):
        self.server.stop()
        self.server.close()


class Locust(object):
    current_task = "task"


class TestSocketIO(LocustTestCase):

    def setUp(self):
        super(TestSocketIO, self).setUp()
        self.client = None
        self.server = SimpleSocketIOServer()
        self.server.run()
        gevent.sleep(0.5)
        global_stats.clear_all()

    def tearDown(self):
        super(TestSocketIO, self).tearDown()
        gevent.sleep(0.5)
        self.client.close()
        self.server.stop()

    def test_connect_disconnect(self):
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '')
        self.assertEqual(len(self.server.clients), 1)
        gevent.sleep(0.5)
        self.client.close()
        self.assertEqual(len(self.server.clients), 0)

    def test_send_async(self):
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '')
        self.client.send_async('async_message', {'key': 'value'})
        self.assertIn({'async_message': {'key': 'value'}}, self.server.messages)

    def test_send_sync(self):
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '')
        payload = {'key': 'value'}
        result = self.client.send_sync('sync_message', payload, response='reply-sync-message')
        self.assertIn({'sync_message': {'key': 'value'}}, self.server.messages)
        self.assertEqual(result.payload, {'key1': 'value1'})

    def test_reconnect(self):
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '')
        self.client.send_async('self_disconnect', {})
        self.assertEqual(len(self.server.clients), 0)
        self.client._socket.wait(1)
        self.assertEqual(len(self.server.clients), 1)

    def test_wait_for_message(self):
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '')
        self.client.send_async('wait_for_message', ['long_wait'])
        result = self.client.wait_for_message('long_wait')
        self.assertEqual(result.payload, {'key1': 'value1'})

    def test_wait_for_message_with_condition(self):
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '')
        self.client.send_async('wait_for_message', ['stub'])
        condition = lambda msg: 'key1' in msg.payload.keys()
        result = self.client.wait_for_message('stub', condition=condition)
        self.assertEqual(result.payload, {'key1': 'value1'})

    def test_wait_for_message_with_amount(self):
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '')
        self.client.send_async('wait_for_message_amount', 5)
        messages = self.client.wait_for_message_amount(5)
        self.assertEqual(len(messages), 5)

    def test_work_with_service(self):
        gevent.sleep(0.5)
        self.server.stop()
        self.server = SimpleSocketIOServer('/test')
        self.server.run()
        gevent.sleep(0.5)
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '/test')
        self.assertEqual(len(self.server.clients), 1)
        payload = {'key': 'value'}
        result = self.client.send_sync('sync_message', payload, response='reply-sync-message')
        self.assertIn({'sync_message': {'key': 'value'}}, self.server.messages)
        self.assertEqual(result.payload, {'key1': 'value1'})
        self.client.send_async('self_disconnect', {})
        self.assertEqual(len(self.server.clients), 0)
        self.client._socket.wait(1)
        self.assertEqual(len(self.server.clients), 2)

    def test_stats_tracking(self):
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '')
        self.client.send_async('async_message', {'key': 'value'})
        self.assertEqual(global_stats.num_requests, 1)
        self.assertIn(
            ('task', 'async_message ()', 'socketio-sequence'),
            global_stats.entries.keys()
        )
        self.assertIn(
            ('Action Total', 'async_message ()', 'socketio-sequence'),
            global_stats.entries.keys()
        )

    def test_custom_action_name(self):
        self.client = SocketIOClient(Locust, 'http://127.0.0.1:8081', 'socket.io', '')
        self.client.send_async('async_message', {'key': 'value'}, description='test_namespace')
        self.assertEqual(global_stats.num_requests, 1)
        self.assertIn(
            ('task', 'async_message (test_namespace)', 'socketio-sequence'),
            global_stats.entries.keys()
        )
        self.assertIn(
            ('Action Total', 'async_message (test_namespace)', 'socketio-sequence'),
            global_stats.entries.keys()
        )
