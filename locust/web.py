import locust
import bottle
import gevent
import json
from bottle import route, run, send_file
from gevent import wsgi
from stats import RequestStats

_locust = None
_hatch_rate = 1
_max = 1

@route('/public/:filename')
def static_file(filename):
    send_file(filename, root='public')

@route('/')
def index():
    send_file('index.html', root='public')

@route('/swarm')
def start():
    locust.swarm(_locust, _hatch_rate, _max)
    return {'message': 'Swarming started'}

@route('/stats/requests')
def request_stats():
    stats = []

    for s in RequestStats.requests.itervalues():
        stats.append([
            s.name,
            s.num_requests(),
            s.avg_response_time(),
            s.min_response_time(),
            s.max_response_time(),
            s.reqs_per_sec()
        ])

    return json.dumps(stats)

def start(locust, hatch_rate, max):
    global _locust, _hatch_rate, _max
    _locust = locust
    _hatch_rate = hatch_rate
    _max = max
    app = bottle.default_app()
    wsgi.WSGIServer(('', 8089), app).start()

bottle.debug(True)

if __name__ == '__main__':
    start(locust, 5, 20)
    gevent.sleep(1000000)
