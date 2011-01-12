import gevent
import random

# Simple WSGI server simulating fast and slow responses.
def test_server(env, start_response):
    if env['PATH_INFO'] == '/ultra_fast':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ["This is a ultra fast response"]
    if env['PATH_INFO'] == '/fast':
        start_response('200 OK', [('Content-Type', 'text/html')])
        gevent.sleep(random.choice([0.1, 0.2, 0.3]))
        return ["This is a fast response"]
    if env['PATH_INFO'] == '/slow':
        start_response('200 OK', [('Content-Type', 'text/html')])
        gevent.sleep(random.choice([0.5, 1, 1.5]))
        return ["This is a slow response"]
    if env['PATH_INFO'] == '/consistent':
        start_response('200 OK', [('Content-Type', 'text/html')])
        gevent.sleep(0.2)
        return ["This is a consistent response"]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['Not Found']

