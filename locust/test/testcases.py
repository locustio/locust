import base64
import logging
import random
import sys
import unittest
import warnings
from copy import copy
from io import BytesIO

import gevent
import gevent.pywsgi
from flask import Flask, Response, make_response, redirect, request, send_file, stream_with_context

import locust
from locust import log
from locust.event import Events
from locust.env import Environment
from locust.test.mock_logging import MockedLoggingHandler


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


@app.route("/request_method", methods=["POST", "GET", "HEAD", "PUT", "DELETE", "PATCH"])
def request_method():
    return request.method


@app.route("/request_header_test")
def request_header_test():
    return request.headers["X-Header-Test"]


@app.route("/post", methods=["POST"])
@app.route("/put", methods=["PUT"])
def manipulate():
    return str(request.form.get("arg", ""))


@app.route("/get_arg", methods=["GET"])
def get_arg():
    return request.args.get("arg")


@app.route("/fail")
def failed_request():
    return "This response failed", 500


@app.route("/status/204")
def status_204():
    return "", 204


@app.route("/redirect", methods=["GET", "POST"])
def do_redirect():
    delay = request.args.get("delay")
    if delay:
        gevent.sleep(float(delay))
    url = request.args.get("url", "/ultra_fast")
    return redirect(url)


@app.route("/basic_auth")
def basic_auth():
    auth = base64.b64decode(request.headers.get("Authorization", "").replace("Basic ", "")).decode("utf-8")
    if auth == "locust:menace":
        return "Authorized"
    resp = make_response("401 Authorization Required", 401)
    resp.headers["WWW-Authenticate"] = 'Basic realm="Locust"'
    return resp


@app.route("/no_content_length")
def no_content_length():
    r = send_file(
        BytesIO("This response does not have content-length in the header".encode("utf-8")),
        add_etags=False,
        mimetype="text/plain",
    )
    r.headers.remove("Content-Length")
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


@app.route("/set_cookie", methods=["POST"])
def set_cookie():
    response = make_response("ok")
    response.set_cookie(request.args.get("name"), request.args.get("value"))
    return response


@app.route("/get_cookie")
def get_cookie():
    return make_response(request.cookies.get(request.args.get("name"), ""))


class LocustTestCase(unittest.TestCase):
    """
    Test case class that restores locust.events.EventHook listeners on tearDown, so that it is
    safe to register any custom event handlers within the test.
    """

    def setUp(self):
        # Prevent args passed to test runner from being passed to Locust
        del sys.argv[1:]

        locust.events = Events()
        self.environment = Environment(events=locust.events, catch_exceptions=False)
        self.runner = self.environment.create_local_runner()

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

        # set up mocked logging handler
        self._logger_class = MockedLoggingHandler()
        self._logger_class.setLevel(logging.INFO)
        self._root_log_handlers = [h for h in logging.root.handlers]
        [logging.root.removeHandler(h) for h in logging.root.handlers]
        logging.root.addHandler(self._logger_class)
        logging.root.setLevel(logging.INFO)
        self.mocked_log = MockedLoggingHandler

        # set unhandled exception flag to False
        log.unhandled_greenlet_exception = False

    def tearDown(self):
        # restore logging class
        logging.root.removeHandler(self._logger_class)
        [logging.root.addHandler(h) for h in self._root_log_handlers]
        self.mocked_log.reset()


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

    def tearDown(self):
        super(WebserverTestCase, self).tearDown()
        self._web_server.stop_accepting()
        self._web_server.stop()
