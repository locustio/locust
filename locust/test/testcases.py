import random
import gevent
import gevent.pywsgi
import unittest
import base64
from copy import copy
from StringIO import StringIO

from locust import events
from locust.stats import RequestStats
from flask import Flask, request, redirect, make_response, send_file

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

@app.route("/redirect")
def redirect():
    return redirect("/ultra_fast")

@app.route("/basic_auth")
def basic_auth():
    auth = base64.b64decode(request.headers.get("Authorization").replace("Basic ", ""))
    if auth == "locust:menace":
        return "Authorized"
    resp = make_response("401 Authorization Required", 401)
    resp.headers["WWW-Authenticate"] = 'Basic realm="Locust"'
    return resp

@app.route("/no_content_length")
def no_content_length():
    r = send_file(StringIO("This response does not have content-length in the header"), add_etags=False)
    return r

@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404


class LocustTestCase(unittest.TestCase):
    """
    Test case class that restores locust.events.EventHook listeners on tearDown, so that it is
    safe to register any custom event handlers within the test.
    """
    def setUp(self):
        self._event_handlers = {}
        for name in dir(events):
            event = getattr(events, name)
            if isinstance(event, events.EventHook):
                self._event_handlers[event] = copy(event._handlers)
                      
    def tearDown(self):
        for event, handlers in self._event_handlers.iteritems():
            event._handlers = handlers

            
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
        RequestStats.requests = {}

    def tearDown(self):
        super(WebserverTestCase, self).tearDown()
        self._web_server.stop()
