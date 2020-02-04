# -*- coding: utf-8 -*-
import csv
import json
import sys
import traceback

import gevent
import requests
from gevent import pywsgi

from locust import events, runners, stats, web
from locust.core import Locust
from locust.main import parse_options
from locust.runners import LocustRunner
from io import StringIO

from .testcases import LocustTestCase

ALTERNATIVE_HOST = 'http://localhost'
SWARM_DATA_WITH_HOST = {'locust_count': 5, 'hatch_rate': 5, 'host': ALTERNATIVE_HOST}
SWARM_DATA_WITH_NO_HOST = {'locust_count': 5, 'hatch_rate': 5}
SWARM_DATA_WITH_STEP_LOAD = {"locust_count":5, "hatch_rate":2, "step_locust_count":2, "step_duration": "2m"}

class TestWebUI(LocustTestCase):
    def setUp(self):
        super(TestWebUI, self).setUp()
        
        stats.global_stats.clear_all()
        parser = parse_options(default_config_files=[])[0]
        self.options = parser.parse_args([])
        runners.locust_runner = LocustRunner([], self.options)
        
        web.request_stats.clear_cache()
        
        self._web_ui_server = pywsgi.WSGIServer(('127.0.0.1', 0), web.app, log=None)
        gevent.spawn(lambda: self._web_ui_server.serve_forever())
        gevent.sleep(0.01)
        self.web_port = self._web_ui_server.server_port
    
    def tearDown(self):
        super(TestWebUI, self).tearDown()
        runners.locust_runner = None
        self._web_ui_server.stop()
    
    def test_index(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/" % self.web_port).status_code)
    
    def test_stats_no_data(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).status_code)
    
    def test_stats(self):
        stats.global_stats.log_request("GET", "/<html>", 120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.text)
        self.assertEqual(2, len(data["stats"])) # one entry plus Aggregated
        self.assertEqual("/<html>", data["stats"][0]["name"])
        self.assertEqual("/&lt;html&gt;", data["stats"][0]["safe_name"])
        self.assertEqual("GET", data["stats"][0]["method"])
        self.assertEqual(120, data["stats"][0]["avg_response_time"])
        
        self.assertEqual("Aggregated", data["stats"][1]["name"])
        self.assertEqual(1, data["stats"][1]["num_requests"])
        self.assertEqual(120, data["stats"][1]["avg_response_time"])
        
    def test_stats_cache(self):
        stats.global_stats.log_request("GET", "/test", 120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.text)
        self.assertEqual(2, len(data["stats"])) # one entry plus Aggregated
        
        # add another entry
        stats.global_stats.log_request("GET", "/test2", 120, 5612)
        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).text)
        self.assertEqual(2, len(data["stats"])) # old value should be cached now
        
        web.request_stats.clear_cache()
        
        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).text)
        self.assertEqual(3, len(data["stats"])) # this should no longer be cached
    
    def test_stats_rounding(self):
        stats.global_stats.log_request("GET", "/test", 1.39764125, 2)
        stats.global_stats.log_request("GET", "/test", 999.9764125, 1000)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.text)
        self.assertEqual(1, data["stats"][0]["min_response_time"])
        self.assertEqual(1000, data["stats"][0]["max_response_time"])
    
    def test_request_stats_csv(self):
        stats.global_stats.log_request("GET", "/test2", 120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests/csv" % self.web_port)
        self.assertEqual(200, response.status_code)

    def test_request_stats_history_csv(self):
        stats.global_stats.log_request("GET", "/test2", 120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/stats_history/csv" % self.web_port)
        self.assertEqual(200, response.status_code)

    def test_failure_stats_csv(self):
        stats.global_stats.log_error("GET", "/", Exception("Error1337"))
        response = requests.get("http://127.0.0.1:%i/stats/failures/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
    
    def test_request_stats_with_errors(self):
        stats.global_stats.log_error("GET", "/", Exception("Error1337"))
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("Error1337", response.text)

    def test_reset_stats(self):
        try:
            raise Exception(u"A cool test exception")
        except Exception as e:
            tb = sys.exc_info()[2]
            runners.locust_runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
            runners.locust_runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))

        stats.global_stats.log_request("GET", "/test", 120, 5612)
        stats.global_stats.log_error("GET", "/", Exception("Error1337"))

        response = requests.get("http://127.0.0.1:%i/stats/reset" % self.web_port)

        self.assertEqual(200, response.status_code)

        self.assertEqual({}, stats.global_stats.errors)
        self.assertEqual({}, runners.locust_runner.exceptions)
        
        self.assertEqual(0, stats.global_stats.get("/", "GET").num_requests)
        self.assertEqual(0, stats.global_stats.get("/", "GET").num_failures)
        self.assertEqual(0, stats.global_stats.get("/test", "GET").num_requests)
        self.assertEqual(0, stats.global_stats.get("/test", "GET").num_failures)
    
    def test_exceptions(self):
        try:
            raise Exception(u"A cool test exception")
        except Exception as e:
            tb = sys.exc_info()[2]
            runners.locust_runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
            runners.locust_runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
        
        response = requests.get("http://127.0.0.1:%i/exceptions" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("A cool test exception", response.text)
        
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

    def test_swarm_host_value_specified(self):
        response = requests.post("http://127.0.0.1:%i/swarm" % self.web_port, data=SWARM_DATA_WITH_HOST)
        self.assertEqual(200, response.status_code)
        self.assertEqual(runners.locust_runner.host, SWARM_DATA_WITH_HOST['host'])

    def test_swarm_host_value_not_specified(self):
        response = requests.post("http://127.0.0.1:%i/swarm" % self.web_port, data=SWARM_DATA_WITH_NO_HOST)
        self.assertEqual(200, response.status_code)
        self.assertEqual(runners.locust_runner.host, None)
    
    def test_host_value_from_locust_class(self):
        class MyLocust(Locust):
            host = "http://example.com"
        runners.locust_runner = LocustRunner([MyLocust], options=self.options)
        response = requests.get("http://127.0.0.1:%i/" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("http://example.com", response.content.decode("utf-8"))
        self.assertNotIn("setting this will override the host on all Locust classes", response.content.decode("utf-8"))
    
    def test_host_value_from_multiple_locust_classes(self):
        class MyLocust(Locust):
            host = "http://example.com"
        class MyLocust2(Locust):
            host = "http://example.com"        
        runners.locust_runner = LocustRunner([MyLocust, MyLocust2], options=self.options)
        response = requests.get("http://127.0.0.1:%i/" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("http://example.com", response.content.decode("utf-8"))
        self.assertNotIn("setting this will override the host on all Locust classes", response.content.decode("utf-8"))
    
    def test_host_value_from_multiple_locust_classes_different_hosts(self):
        class MyLocust(Locust):
            host = None
        class MyLocust2(Locust):
            host = "http://example.com"
        runners.locust_runner = LocustRunner([MyLocust, MyLocust2], options=self.options)
        response = requests.get("http://127.0.0.1:%i/" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertNotIn("http://example.com", response.content.decode("utf-8"))
        self.assertIn("setting this will override the host on all Locust classes", response.content.decode("utf-8"))

    def test_swarm_in_step_load_mode(self):
        runners.locust_runner.step_load = True
        response = requests.post("http://127.0.0.1:%i/swarm" % self.web_port, SWARM_DATA_WITH_STEP_LOAD)
        self.assertEqual(200, response.status_code)
        self.assertIn("Step Load Mode", response.text)
