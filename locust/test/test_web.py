# -*- coding: utf-8 -*-
import csv
import json
import sys
import traceback

import gevent
import requests
from gevent import wsgi

from locust import runners, stats, web
from locust.main import parse_options
from locust.runners import LocustRunner
from six.moves import StringIO

from .testcases import LocustTestCase


class TestWebUI(LocustTestCase):
    def setUp(self):
        super(TestWebUI, self).setUp()
        
        stats.global_stats.clear_all()
        parser = parse_options()[0]
        options = parser.parse_args([])[0]
        runners.locust_runner = LocustRunner([], options)
        
        web.request_stats.clear_cache()
        
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
        
        data = json.loads(response.text)
        self.assertEqual(2, len(data["stats"])) # one entry plus Total
        self.assertEqual("/test", data["stats"][0]["name"])
        self.assertEqual("GET", data["stats"][0]["method"])
        self.assertEqual(120, data["stats"][0]["avg_response_time"])
        
    def test_stats_cache(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.text)
        self.assertEqual(2, len(data["stats"])) # one entry plus Total
        
        # add another entry
        stats.global_stats.get("/test2", "GET").log(120, 5612)
        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).text)
        self.assertEqual(2, len(data["stats"])) # old value should be cached now
        
        web.request_stats.clear_cache()
        
        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).text)
        self.assertEqual(3, len(data["stats"])) # this should no longer be cached
    
    def test_request_stats_csv(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
    
    def test_distribution_stats_csv(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/distribution/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
    
    def test_request_stats_with_errors(self):
        stats.global_stats.get("/", "GET").log_error(Exception("Error1337"))
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("Error1337", str(response.content))
    
    def test_exceptions(self):
        try:
            raise Exception(u"A cool test exception")
        except Exception as e:
            tb = sys.exc_info()[2]
            runners.locust_runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
            runners.locust_runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
        
        response = requests.get("http://127.0.0.1:%i/exceptions" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("A cool test exception", str(response.content))
        
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
    
    def test_exceptions_csv(self):
        try:
            raise Exception("Test exception")
        except Exception as e:
            tb = sys.exc_info()[2]
            runners.locust_runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
            runners.locust_runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
        
        response = requests.get("http://127.0.0.1:%i/exceptions/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
        
        reader = csv.reader(StringIO(response.text))
        rows = []
        for row in reader:
            rows.append(row)
        
        self.assertEqual(2, len(rows))
        self.assertEqual("Test exception", rows[1][1])
        self.assertEqual(2, int(rows[1][0]), "Exception count should be 2")
