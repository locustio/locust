"""Websocket Locust client"""
import time
import uuid
import atexit
import logging
from collections import deque
from contextlib import contextmanager
from pprint import pformat

from socketIO_client import SocketIO, BaseNamespace
from locust import events as LocustEventHandler

logger = logging.getLogger(__name__)

class SocketIOMSG(object):
    """Struct for SocketIO message description"""

    def __init__(self, msg_type, payload):
        self.type = msg_type
        self.payload = payload
        self.timestamp = time.time()

    def __str__(self):
        return "  Websocket message\n" +\
                "  Message type: {}\n".format(self.type) +\
                "  Timestamp: {}\n".format(self.timestamp) +\
                "  Payload:\n{}\n".format(pformat(self.payload))

class SocketIOAbstractListener(object):
    """Abstract class for socketIO sync listeners"""

    def __init__(self):
        self.msg = None
        self._start_time = time.time()
        self._exec_time = None

    @property
    def exec_time(self):
        """Read listener execution time"""
        if not self._exec_time:
            self._track_time()
        return self._exec_time

    def __call__(self, msg):
        self.msg = msg
        if self.fulfilled:
            self._track_time()

    def fulfilled(self):
        """Was listener resolve conditions fulfilled. Boolean"""
        return self.msg

    def _track_time(self):
        self._exec_time = int((time.time() - self._start_time) * 1000)


class WebSocketTimeoutError(Exception):
    """Timeout waiting for response from MMQueue."""
    pass


class WebSocketClient(object):
    """SocketIO client wrapper"""
    MSG_CACHE = 100 # Amount of recived messages cached
    TIMEOUT = 1200
    SYNC_TIME = 0.5 # Not influence on request-response sequence time tracking

    def __init__(self, host, resource, service):
        self.client_id = str(uuid.uuid4())
        self._messages = deque([], self.MSG_CACHE)
        self._listener = None
        self._graceful_close = False
        self._connect(host, resource, service)

    def _connect(self, host, resource, service):
        client_wrapper = self

        class Namespace(BaseNamespace):
            """SocketIO event namespace declaration"""
            def on_connect(self):
                pass

            def on_reconnect(self):
                pass

            def on_disconnect(self):
                client_wrapper._handle_disconnect(self)

            def on_event(self, event, *args):
                msg = SocketIOMSG(event, args[0] if args else None)
                client_wrapper._receive(msg)

            def reconnect(self):
                for path in self._io._namespace_by_path.keys():
                    self._io.connect(path)

        self._socket = SocketIO(host,
                                verify=True,
                                wait_for_connection=True,
                                resource=resource)
        self._socket.define(Namespace)
        self._socket.define(Namespace, path=service)
        logger.debug("Created websocket client. ID: %s", self.client_id)
        logger.debug("Established websocket connection to %s", host)

        atexit.register(self.close)

    def close(self):
        """Close websocket connection"""
        self._graceful_close = True
        self._socket.disconnect()
        logger.debug("Closed websocket connection. Client id: %s", self.client_id)

    def _handle_disconnect(self, namespace):
        attempt = 0
        if not self._graceful_close:
            while not self._socket.connected and attempt < 4:
                logger.debug('Connection lost. Trying to reconnect...')
                namespace.reconnect()
                self._socket.wait(0.5)
                attempt += 1

    def _receive(self, msg):
        self._messages.append(msg)
        logger.debug("Message received:\n%s", str(msg))
        if callable(self._listener):
            self._listener(msg)

    def send_sync(self, message, payload, response, description=''):
        """Synchoronious msg send with waiting for exact response time"""
        action_name = message + ' ({})'.format(description)
        self._emit(SocketIOMSG(message, payload), action_name)
        return self.wait_for_message(response, description=description)

    def send_async(self, message, payload, description=''):
        """Async message send (fire-n-forget), void"""
        action_name = message + ' ({})'.format(description)
        result = self._emit(SocketIOMSG(message, payload), action_name)
        if result:
            LocustEventHandler.request_success.fire(
                **self._locust_event('sequence', action_name, 0, response_length=-1)
            )

    def _emit(self, msg, action_name):
        success = False
        try:
            logger.debug("Message sent:\n%s", str(msg))
            self._socket.emit(msg.type, msg.payload, path=self.SOCKETIO_SERVICE_PATH)
        except Exception as e:
            logger.debug("Message sent failure: %s", msg.type)
            LocustEventHandler.request_failure.fire(
                **self._locust_event('request', action_name, 0, exception=e)
            )
        else:
            success = True
        return success

    def wait_for_message(self, message, condition=None, description=''):
        """
        Sync wait for exact msg type received. Blocks execution thread
        Condtion should be callable with argument where Socket message would be passed
        in check callback
        """
        class MSGTypeListener(SocketIOAbstractListener):

            def __init__(self, msg_type, condition):
                super(MSGTypeListener, self).__init__()
                self.expected_type = msg_type
                self.condition = condition
                logger.debug("Started message type listener. Message type: %s", msg_type)

            def __call__(self, msg):
                if self.condition and callable(self.condition):
                    if msg.type == self.expected_type and self.condition(msg):
                        self.msg = msg
                        self._track_time()
                else:
                    if msg.type == self.expected_type:
                        self.msg = msg
                        self._track_time()

        with self._wait_for(MSGTypeListener(message, condition)) as listener:
            result = listener.fulfilled()
            exec_time = listener.exec_time

        action_name = message + ' ({})'.format(description)
        self._fire_post_listener_event(result, 'listener', action_name, exec_time)

        return result

    def wait_for_message_amount(self, amount):
        """Sync wait for specific msg amount received. Blocks execution thread"""
        class MSGCountListener(SocketIOAbstractListener):
            def __init__(self, amount):
                super(MSGCountListener, self).__init__()
                self.expected_amount = amount
                self.msges = []
                logger.debug("Started message count listener. Message count: %s", amount)

            def __call__(self, msg):
                self.msges.append(msg)
                if self.fulfilled():
                    self._track_time()

            def fulfilled(self):
                return len(self.msges) >= self.expected_amount

        with self._wait_for(MSGCountListener(amount)) as listener:
            result = listener.fulfilled()
            exec_time = listener.exec_time
            messages = listener.msges

        name = "Count: {}".format(amount)
        self._fire_post_listener_event(result, 'counter', name, exec_time)

        return messages

    @contextmanager
    def _wait_for(self, listener):
        """listener should be SocketIOAbstractListener descendant"""
        self._listener = listener
        timer = 0
        while timer < self.TIMEOUT:
            if self._listener.fulfilled():
                break
            before = time.time()
            self._socket.wait(self.SYNC_TIME)
            timer += time.time() - before

        yield listener
        self._listener = None

    def _locust_event(self, request, name, time, **kwarg):
        msg = {
            'request_type': 'socketio-' + request,
            'name': name,
            'response_time': time
        }
        msg.update(kwarg)
        return msg

    def _fire_post_listener_event(self, result, event, name, exec_time):
        if result:
            logger.debug("Listener resolved succesfully")
            LocustEventHandler.request_success.fire(
                **self._locust_event(event, name, exec_time, response_length=-1)
            )
        else:
            logger.debug("Listener resolved by timeout")
            exception = WebSocketTimeoutError('WebSocket listener timeout')
            LocustEventHandler.request_failure.fire(
                **self._locust_event(event, name, exec_time, exception=exception)
            )
