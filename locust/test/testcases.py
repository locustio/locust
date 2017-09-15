import base64
import random
import sys
import unittest
import warnings
from copy import copy
from io import BytesIO

import gevent
import gevent.pywsgi
import six
from flask import (Flask, Response, make_response, redirect, request,
                   send_file, stream_with_context)

from locust import events
from locust.stats import global_stats


def safe_repr(obj, short=False):
    """
    Function from python 2.7's unittest.util. Used in methods that is copied 
    from 2.7's unittest.TestCase to work in python 2.6.
    """
    _MAX_LENGTH = 80
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'



app = Flask(__name__)

@app.route("/ultra_fast")
def ultra_fast():
    return "This is an ultra fast response"

@app.route("/fast")
def fast():
    gevent.sleep(random.choice([0.1, 0.2, 0.3]))
    return "This is a fast response"

@app.route("/slow")
def slow():
    delay = request.args.get("delay")
    if delay:
        gevent.sleep(float(delay))
    else:
        gevent.sleep(random.choice([0.5, 1, 1.5]))
    return "This is a slow response"

@app.route("/consistent")
def consistent():
    gevent.sleep(0.2)
    return "This is a consistent response"

@app.route("/request_method", methods=["POST", "GET", "HEAD", "PUT", "DELETE"])
def request_method():
    return request.method

@app.route("/request_header_test")
def request_header_test():
    return request.headers["X-Header-Test"]

@app.route("/post", methods=["POST"])
@app.route("/put", methods=["PUT"])
def manipulate():
    return str(request.form.get("arg", ""))

@app.route("/fail")
def failed_request():
    return "This response failed", 500

@app.route("/redirect", methods=["GET", "POST"])
def do_redirect():
    delay = request.args.get("delay")
    if delay:
        gevent.sleep(float(delay))
    url = request.args.get("url", "/ultra_fast")
    return redirect(url)

@app.route("/basic_auth")
def basic_auth():
    auth = base64.b64decode(request.headers.get("Authorization", "").replace("Basic ", "")).decode('utf-8')
    if auth == "locust:menace":
        return "Authorized"
    resp = make_response("401 Authorization Required", 401)
    resp.headers["WWW-Authenticate"] = 'Basic realm="Locust"'
    return resp

@app.route("/no_content_length")
def no_content_length():
    r = send_file(BytesIO("This response does not have content-length in the header".encode('utf-8')),
                  add_etags=False,
                  mimetype='text/plain')
    return r

@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404

@app.route("/streaming/<int:iterations>")
def streaming_response(iterations):
    import time
    def generate():
        yield "<html><body><h1>streaming response</h1>"
        for i in range(iterations):
            yield "<span>%s</span>\n" % i
            time.sleep(0.01)
        yield "</body></html>"
    return Response(stream_with_context(generate()), mimetype="text/html")


class LocustTestCase(unittest.TestCase):
    """
    Test case class that restores locust.events.EventHook listeners on tearDown, so that it is
    safe to register any custom event handlers within the test.
    """
    def setUp(self):
        # Prevent args passed to test runner from being passed to Locust
        del sys.argv[1:]

        self._event_handlers = {}
        for name in dir(events):
            event = getattr(events, name)
            if isinstance(event, events.EventHook):
                self._event_handlers[event] = copy(event._handlers)
        
        # When running the tests in Python 3 we get warnings about unclosed sockets. 
        # This causes tests that depends on calls to sys.stderr to fail, so we'll 
        # suppress those warnings. For more info see: 
        # https://github.com/requests/requests/issues/1882
        try:
            warnings.filterwarnings(action="ignore", message="unclosed <socket object", category=ResourceWarning)
        except NameError:
            # ResourceWarning doesn't exist in Python 2, but since the warning only appears
            # on Python 3 we don't need to mock it. Instead we can happily ignore the exception
            pass
                      
    def tearDown(self):
        for event, handlers in six.iteritems(self._event_handlers):
            event._handlers = handlers
    
    def assertIn(self, member, container, msg=None):
        """
        Just like self.assertTrue(a in b), but with a nicer default message.
        Implemented here to work with Python 2.6
        """
        if member not in container:
            standardMsg = '%s not found in %s' % (safe_repr(member),
                                                  safe_repr(container))
            self.fail(self._formatMessage(msg, standardMsg))
    
    def assertLess(self, a, b, msg=None):
        """Just like self.assertTrue(a < b), but with a nicer default message."""
        if not a < b:
            standardMsg = '%s not less than %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertLessEqual(self, a, b, msg=None):
        """Just like self.assertTrue(a <= b), but with a nicer default message."""
        if not a <= b:
            standardMsg = '%s not less than or equal to %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertGreater(self, a, b, msg=None):
        """Just like self.assertTrue(a > b), but with a nicer default message."""
        if not a > b:
            standardMsg = '%s not greater than %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertGreaterEqual(self, a, b, msg=None):
        """Just like self.assertTrue(a >= b), but with a nicer default message."""
        if not a >= b:
            standardMsg = '%s not greater than or equal to %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

            
class WebserverTestCase(LocustTestCase):
    """
    Test case class that sets up an HTTP server which can be used within the tests
    """
    def setUp(self):
        super(WebserverTestCase, self).setUp()
        self._web_server = gevent.pywsgi.WSGIServer(("127.0.0.1", 0), app, log=None)
        gevent.spawn(lambda: self._web_server.serve_forever())
        gevent.sleep(0.01)
        self.port = self._web_server.server_port
        global_stats.clear_all()

    def tearDown(self):
        super(WebserverTestCase, self).tearDown()
        self._web_server.stop_accepting()
        self._web_server.stop()
