import locust.core
import gevent
from clients import HTTPClient, HttpBrowser

from simple_test_server import test_server
gevent.spawn(lambda: gevent.wsgi.WSGIServer(('', 8088), test_server).serve_forever())

def ultra_fast(l):
    l.client.get('/ultra_fast', name='Ultra fast page')

def fast(l):
    l.client.get('/fast', name='Fast page')

def slow(l):
    l.client.get('/slow', name='Slow page')

def consistent(l):
    l.client.get('/consistent', name='Consistent page')

class WebsiteUser(locust.core.Locust):
    host = "http://127.0.0.1:8088"
    tasks = [ultra_fast, fast, slow, consistent]
    min_wait=3000
    max_wait=10000

#locust.core.swarm(WebsiteUser, hatch_rate=500, max=30000)
#gevent.sleep(100000)
