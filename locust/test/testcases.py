import gevent
import gevent.wsgi
import unittest
import random
from werkzeug.wrappers import Request

# Simple WSGI server simulating fast and slow responses.
import base64

from locust.stats import RequestStats

def simple_webserver(env, start_response):
    if env['PATH_INFO'] == '/ultra_fast':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ["This is an ultra fast response"]
    elif env['PATH_INFO'] == '/fast':
        start_response('200 OK', [('Content-Type', 'text/html')])
        gevent.sleep(random.choice([0.1, 0.2, 0.3]))
        return ["This is a fast response"]
    elif env['PATH_INFO'] == '/slow':
        start_response('200 OK', [('Content-Type', 'text/html')])
        gevent.sleep(random.choice([0.5, 1, 1.5]))
        return ["This is a slow response"]
    elif env['PATH_INFO'] == '/consistent':
        start_response('200 OK', [('Content-Type', 'text/html')])
        gevent.sleep(0.2)
        return ["This is a consistent response"]
    elif env['PATH_INFO'] == '/request_header_test':
        start_response('200 OK', [('Content-Type', 'text/html')])
        request = Request(env)
        return [request.headers.get("X-Header-Test")]
    elif env['PATH_INFO'] == '/request_method':
        start_response('200 OK', [('Content-Type', 'text/html')])
        request = Request(env)
        return [request.method]
    elif env['PATH_INFO'] == '/post':
        start_response('200 OK', [('Content-Type', 'text/html')])
        request = Request(env)
        return [str(request.form.get("arg", ""))]
    elif env['PATH_INFO'] == '/fail':
        start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
        return ["This response failed"]
    elif env['PATH_INFO'] == '/redirect':
        start_response('302 Found', [('Content-Type', 'text/html'), ('Location', '/ultra_fast')])
        return ["Redirected, bro"]
    elif env['PATH_INFO'] == '/basic_auth':
        request = Request(env)
        if "Authorization" in request.headers:
            auth = base64.b64decode(request.headers.get("Authorization").replace("Basic ", ""))
            if auth == "locust:menace":
                start_response('200 OK', [('Content-Type', 'text/html')])
                return ["Authorized"]

        start_response('401 Authorization Required', [('Content-Type', 'text/html'), ('WWW-Authenticate', 'Basic realm="Locust"')])
        return ['401 Authorization Required']
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['Not Found']

class WebserverTestCase(unittest.TestCase):
    def setUp(self):
        self._web_server = gevent.wsgi.WSGIServer(("127.0.0.1", 0), simple_webserver, log=None)
        gevent.spawn(lambda: self._web_server.serve_forever())
        gevent.sleep(0)
        self.port = self._web_server.server_port
        RequestStats.requests = {}

    def tearDown(self):
        self._web_server.kill()

