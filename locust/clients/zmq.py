"""ZMQ Locust client"""
import time
import uuid
import atexit
import logging
from pprint import pformat

import zmq
from locust import events as LocustEventHandler

logger = logging.getLogger(__name__)

class ZMQClient(object):
    """ZMQ wrapper for Locust client substitution"""

    def __init__(self, endpoint, name=None):
        self._endpoint = endpoint
        self._name = name
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.connect(endpoint)
        time.sleep(0.5)
        logger.debug("ZMQ Connection set. Endpoint %s", endpoint)
        atexit.register(self.close)

    def close(self):
        """Close connection"""
        self._socket.close()
        self._context.destroy()
        logger.debug("ZMQ Connection closed. Context destroyed")

    def send(self, message):
        """Send message through socket"""
        message = [str(i) for i in message]
        logger.debug("Sending ZMQ message:\n%s", message)
        try:
            tracker = self._socket.send_multipart(message, copy=False, track=True)
            tracker.wait()
            LocustEventHandler.request_success.fire(
                **self._locust_event(response_length=-1)
            )
        except Exception as e:
            LocustEventHandler.request_failure.fire(
                **self._locust_event(exception=e)
            )

    def _locust_event(self, **kwargs):
        msg = {
            'request_type': 'zmq-send',
            'name': self._name or self._endpoint,
            'response_time': 0
        }
        msg.update(kwargs)
        return msg
