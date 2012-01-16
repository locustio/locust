import gevent
import unittest
import random
from werkzeug.wrappers import Request

# Simple WSGI server simulating fast and slow responses.
import base64

from locust.stats import RequestStats

from flask import Flask, request, redirect, make_response

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
    print "METHOD", request.method
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

@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404

class WebserverTestCase(unittest.TestCase):
    def setUp(self):
        gevent.spawn(lambda: app.run(port=8080))
        gevent.sleep(0)
        self.port = 8080
        RequestStats.requests = {}

    def tearDown(self):
        pass

