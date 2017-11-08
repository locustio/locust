"""SocketIO Locust client"""
import time
import uuid
import atexit
import logging
from collections import deque
from contextlib import contextmanager
from pprint import pformat
from socket import error as SocketError

import six
import gevent
from socketIO_client import SocketIO, BaseNamespace
from socketIO_client.transports import WebsocketTransport, XHR_PollingTransport
from socketIO_client.exceptions import TimeoutError, PacketError
from socketIO_client.symmetries import SSLError
from socketIO_client.parsers import parse_packet_text
try:
    from websocket import (
        WebSocketConnectionClosedException, WebSocketTimeoutException,
        create_connection)
except ImportError:
    exit("""\
An incompatible websocket library is conflicting with the one we need.
You can remove the incompatible library and install the correct one
by running the following commands:

yes | pip uninstall websocket websocket-client
pip install -U websocket-client""")

from locust import events as LocustEventHandler
from locust.exception import RescheduleTask
from locust.log import LazyLog

logger = logging.getLogger(__name__)


class SocketIOTimeoutError(Exception):
    """Timeout waiting for response from MMQueue."""
    pass


class SocketIODisconnectedError(Exception):
    """SocketIO connection lost"""
    pass


class SocketIOConnectionError(Exception):
    """Unable to set SocketIO connection"""
    def __init__(self, message, errno=-1):
        self.message = message
        self.errno = errno


class SocketIOMSG(object):
    """Struct for SocketIO message description"""

    def __init__(self, msg_type, payload):
        self.type = msg_type
        self.payload = payload
        self.timestamp = time.time()

    def __str__(self):
        return "  SocketIO message\n" +\
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


class ExtendedWebsocketTransport(WebsocketTransport):
    """
    Extension for WebsocketTransport with redefined exception
    Exception will translate TCP socket errno if such exist
    """
    def recv_packet(self):
        try:
            packet_text = self._connection.recv()
        except WebSocketTimeoutException as e:
            raise TimeoutError('recv timed out (%s)' % e)
        except SSLError as e:
            raise SocketIOConnectionError('recv disconnected by SSL (%s)' % e)
        except WebSocketConnectionClosedException as e:
            raise SocketIOConnectionError('WebSocket :: recv disconnected (%s)' % e)
        except SocketError as e:
            raise SocketIOConnectionError('Socket :: recv disconnected (%s)' % e, e.errno)
        if not isinstance(packet_text, six.binary_type):
            packet_text = packet_text.encode('utf-8')
        engineIO_packet_type, engineIO_packet_data = parse_packet_text(
            packet_text)
        yield engineIO_packet_type, engineIO_packet_data


class ExtendedSocketIO(SocketIO):
    """
    Extension for SocketIO with redefined rection for SocketExceptions
    """

    def _get_transport(self, transport_name):
        SelectedTransport = {
            'xhr-polling': XHR_PollingTransport,
            'websocket': ExtendedWebsocketTransport,
        }[transport_name]
        return SelectedTransport(
            self._http_session, self._is_secure, self._url,
            self._engineIO_session)

    def wait(self, seconds=None, **kw):
        'Wait in a loop and react to events as defined in the namespaces'
        # Use ping/pong to unblock recv for polling transport
        self._heartbeat_thread.hurry()
        # Use timeout to unblock recv for websocket transport
        self._transport.set_timeout(seconds=1)
        # Listen
        warning_screen = self._yield_warning_screen(seconds)
        for elapsed_time in warning_screen:
            if self._should_stop_waiting(**kw):
                break
            try:
                try:
                    self._process_packets()
                except TimeoutError:
                    pass
                except KeyboardInterrupt:
                    self._close()
                    raise
            except SocketIOConnectionError as e:
                if e.errno == 35:
                    # EAGAIN error, no data for tcp connection for now
                    continue

                self._opened = False
                try:
                    warning = Exception('[connection error] %s' % e)
                    warning_screen.throw(warning)
                except StopIteration:
                    self._warn(warning)
                try:
                    namespace = self.get_namespace()
                    namespace._find_packet_callback('disconnect')(e.message)
                except PacketError:
                    pass
        self._heartbeat_thread.relax()
        self._transport.set_timeout()


class SocketIOClient(object):
    """SocketIO client wrapper"""
    MSG_CACHE = 100 # Amount of recived messages cached
    TIMEOUT = 1200
    SYNC_TIME = 0.5 # Not influence on request-response sequence time tracking

    def __init__(self, locust, host, resource, namespace):
        self.binded_locust = locust
        self.client_id = str(uuid.uuid4())
        self._messages = deque([], self.MSG_CACHE)
        self._listener = None
        self._namespace = namespace
        self._is_active = True
        self.__socket = None
        self._connect(host, resource, namespace)

    def _connect(self, host, resource, namespace):
        client_wrapper = self

        class Namespace(BaseNamespace):
            """SocketIO event namespace declaration"""
            def on_connect(self):
                pass

            def on_reconnect(self):
                pass

            def on_disconnect(self, reason):
                raise SocketIODisconnectedError(reason)

            def on_event(self, event, *args):
                msg = SocketIOMSG(event, args[0] if args else None)
                client_wrapper._receive(msg)

        self.__socket = ExtendedSocketIO(
            host,
            verify=True,
            wait_for_connection=True,
            resource=resource
        )
        gevent.sleep(0.5)
        self._socket.define(Namespace)
        self._socket.define(Namespace, path=namespace)
        logger.debug("Created socketIO client. ID: %s", self.client_id)
        logger.debug("Established socketIO connection to %s", host)

        atexit.register(self.close)

    @property
    def _socket(self):
        if not self.__socket.connected:
            attempt = 0
            while not self.__socket.connected and attempt < 4:
                for path in self.__socket._namespace_by_path.keys():
                    self.__socket.connect(path)
                gevent.sleep(0.5)
            if not self.__socket.connected:
                self._is_active = False
                self.close()
                raise SocketIOConnectionError('Unable to restore socket connection')
        return self.__socket

    def __bool__(self):
        return self._is_active

    def __nonzero__(self):
        return self.__bool__()

    def close(self):
        """Close socketIO connection"""
        self._socket.disconnect()
        self._socket.disconnect(self._namespace)
        logger.debug("Closed socketIO connection. Client id: %s", self.client_id)

    def _receive(self, msg):
        self._messages.append(msg)
        logger.debug("Message received:\n%s", msg)
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
            logger.debug("Message sent:\n%s", msg)
            self._socket.emit(msg.type, msg.payload, path=self._namespace)
        except Exception as e:
            logger.debug("Message sent failure: %s", msg.type)
            LocustEventHandler.request_failure.fire(
                **self._locust_event('request', action_name, 0, exception=e)
            )
            raise RescheduleTask(e, action_name)
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
            'response_time': time,
            'task': self.binded_locust.current_task
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
            exception = SocketIOTimeoutError('SocketIO listener timeout')
            LocustEventHandler.request_failure.fire(
                **self._locust_event(event, name, exec_time, exception=exception)
            )
            raise RescheduleTask(exception, name)
