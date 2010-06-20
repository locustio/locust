import locust
import gevent
import random
from clients import HTTPClient
from gevent import wsgi

# Defines the behaviour of a locust (aka a website user :)
# This is the interesting part!
def website_user(name):
    c = HTTPClient('http://localhost:8088')
    for i in range(0, 10):
        c.get('/fast', name='Fast page')
        c.get('/slow', name='Slow page')
        c.get('/consistent', name='Consistent page')


# Simple WSGI server simulating fast and slow responses
def test_server(env, start_response):
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


# Start the test server that will be our website under test
wsgi.WSGIServer(('', 8088), test_server).start()

# Start a web server where you can control the swarming
# from a web-based UI (recommended).
# website_user is a greenlet/function defining behavior of a locust (aka a user)
# Hatch rate is how many locusts are created per second. A value of 4 means: hatch 4 every second
# Max defines how many locusts that may get hatched
locust.prepare_swarm_from_web(website_user, hatch_rate=4, max=10)

# Immediately start swarming and print statistics to stdout every 1s
#locust.swarm(website_user, hatch_rate=4, max=10)

