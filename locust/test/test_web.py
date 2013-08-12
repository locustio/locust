import json
import requests
import gevent
from gevent import wsgi

from locust import web
from locust import runners
from locust.runners import LocustRunner
from locust import stats
from .testcases import LocustTestCase


class TestWebUI(LocustTestCase):
    def setUp(self):
        super(TestWebUI, self).setUp()
        
        stats.global_stats.clear_all()
        runners.locust_runner = LocustRunner([], None, None, None, None)
        
        self._web_ui_server = wsgi.WSGIServer(('127.0.0.1', 0), web.app, log=None)
        gevent.spawn(lambda: self._web_ui_server.serve_forever())
        gevent.sleep(0.01)
        self.web_port = self._web_ui_server.server_port
    
    def tearDown(self):
        super(TestWebUI, self).tearDown()
        self._web_ui_server.stop()
    
    def test_index(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/" % self.web_port).status_code)
    
    def test_stats_no_data(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).status_code)
    
    def test_stats(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.content)
        self.assertEqual(2, len(data["stats"])) # one entry plus Total
        self.assertEqual("/test", data["stats"][0]["name"])
        self.assertEqual("GET", data["stats"][0]["method"])
        self.assertEqual(120, data["stats"][0]["avg_response_time"])
    
    def test_request_stats_csv(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
    
    def test_distribution_stats_csv(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/distribution/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
