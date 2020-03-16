# -*- coding: utf-8 -*-
import csv
import json
import sys
import traceback
from io import StringIO

import gevent
import requests

from locust import constant
from locust.argument_parser import get_parser
from locust.core import Locust, TaskSet, task
from locust.env import Environment
from locust.runners import LocustRunner
from locust.web import WebUI

from .testcases import LocustTestCase


class TestWebUI(LocustTestCase):
    def setUp(self):
        super(TestWebUI, self).setUp()
        
        parser = get_parser(default_config_files=[])
        self.environment.options = parser.parse_args([])
        self.runner = LocustRunner(self.environment, [])
        self.stats = self.runner.stats
        
        self.web_ui = WebUI(self.environment)
        self.web_ui.app.view_functions["request_stats"].clear_cache()
        
        gevent.spawn(lambda: self.web_ui.start("127.0.0.1", 0))
        gevent.sleep(0.01)
        self.web_port = self.web_ui.server.server_port
    
    def tearDown(self):
        super(TestWebUI, self).tearDown()
        self.web_ui.stop()
        self.runner.quit()
    
    def test_web_ui_reference_on_environment(self):
        self.assertEqual(self.web_ui, self.environment.web_ui)
    
    def test_web_ui_no_runner(self):
        env = Environment()
        web_ui = WebUI(env)
        try:
            gevent.spawn(lambda: web_ui.start("127.0.0.1", 0))
            gevent.sleep(0.01)
            response = requests.get("http://127.0.0.1:%i/" % web_ui.server.server_port)
            self.assertEqual(500, response.status_code)
            self.assertEqual("Error: Locust Environment does not have any runner", response.text)
        finally:
            web_ui.stop()
    
    def test_index(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/" % self.web_port).status_code)
    
    def test_stats_no_data(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).status_code)
    
    def test_stats(self):
        self.stats.log_request("GET", "/<html>", 120, 5612)
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
        self.stats.log_request("GET", "/test", 120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.text)
        self.assertEqual(2, len(data["stats"])) # one entry plus Aggregated
        
        # add another entry
        self.stats.log_request("GET", "/test2", 120, 5612)
        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).text)
        self.assertEqual(2, len(data["stats"])) # old value should be cached now
        
        self.web_ui.app.view_functions["request_stats"].clear_cache()
        
        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).text)
        self.assertEqual(3, len(data["stats"])) # this should no longer be cached
    
    def test_stats_rounding(self):
        self.stats.log_request("GET", "/test", 1.39764125, 2)
        self.stats.log_request("GET", "/test", 999.9764125, 1000)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.text)
        self.assertEqual(1, data["stats"][0]["min_response_time"])
        self.assertEqual(1000, data["stats"][0]["max_response_time"])
    
    def test_request_stats_csv(self):
        self.stats.log_request("GET", "/test2", 120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests/csv" % self.web_port)
        self.assertEqual(200, response.status_code)

    def test_request_stats_history_csv(self):
        self.stats.log_request("GET", "/test2", 120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/stats_history/csv" % self.web_port)
        self.assertEqual(200, response.status_code)

    def test_failure_stats_csv(self):
        self.stats.log_error("GET", "/", Exception("Error1337"))
        response = requests.get("http://127.0.0.1:%i/stats/failures/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
    
    def test_request_stats_with_errors(self):
        self.stats.log_error("GET", "/", Exception("Error1337"))
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("Error1337", response.text)

    def test_reset_stats(self):
        try:
            raise Exception(u"A cool test exception")
        except Exception as e:
            tb = sys.exc_info()[2]
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))

        self.stats.log_request("GET", "/test", 120, 5612)
        self.stats.log_error("GET", "/", Exception("Error1337"))

        response = requests.get("http://127.0.0.1:%i/stats/reset" % self.web_port)

        self.assertEqual(200, response.status_code)

        self.assertEqual({}, self.stats.errors)
        self.assertEqual({}, self.runner.exceptions)
        
        self.assertEqual(0, self.stats.get("/", "GET").num_requests)
        self.assertEqual(0, self.stats.get("/", "GET").num_failures)
        self.assertEqual(0, self.stats.get("/test", "GET").num_requests)
        self.assertEqual(0, self.stats.get("/test", "GET").num_failures)
    
    def test_exceptions(self):
        try:
            raise Exception(u"A cool test exception")
        except Exception as e:
            tb = sys.exc_info()[2]
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
        
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
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
        
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
        class MyLocust(Locust):
            wait_time = constant(1)
            class task_set(TaskSet):
                @task(1)
                def my_task(self):
                    pass
        self.environment.locust_classes = [MyLocust]
        response = requests.post(
            "http://127.0.0.1:%i/swarm" % self.web_port, 
            data={"locust_count": 5, "hatch_rate": 5, "host": "https://localhost"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("https://localhost", response.json()["host"])
        self.assertEqual(self.environment.host, "https://localhost")

    def test_swarm_host_value_not_specified(self):
        class MyLocust(Locust):
            wait_time = constant(1)
            class task_set(TaskSet):
                @task(1)
                def my_task(self):
                    pass
        self.runner.locust_classes = [MyLocust]
        response = requests.post(
            "http://127.0.0.1:%i/swarm" % self.web_port, 
            data={'locust_count': 5, 'hatch_rate': 5},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(None, response.json()["host"])
        self.assertEqual(self.environment.host, None)
    
    def test_host_value_from_locust_class(self):
        class MyLocust(Locust):
            host = "http://example.com"
        self.environment.runner.locust_classes = [MyLocust]
        response = requests.get("http://127.0.0.1:%i/" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("http://example.com", response.content.decode("utf-8"))
        self.assertNotIn("setting this will override the host on all Locust classes", response.content.decode("utf-8"))
    
    def test_host_value_from_multiple_locust_classes(self):
        class MyLocust(Locust):
            host = "http://example.com"
        class MyLocust2(Locust):
            host = "http://example.com"
        self.environment.runner.locust_classes = [MyLocust, MyLocust2]
        response = requests.get("http://127.0.0.1:%i/" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("http://example.com", response.content.decode("utf-8"))
        self.assertNotIn("setting this will override the host on all Locust classes", response.content.decode("utf-8"))
    
    def test_host_value_from_multiple_locust_classes_different_hosts(self):
        class MyLocust(Locust):
            host = None
        class MyLocust2(Locust):
            host = "http://example.com"
        self.environment.runner.locust_classes = [MyLocust, MyLocust2]
        response = requests.get("http://127.0.0.1:%i/" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertNotIn("http://example.com", response.content.decode("utf-8"))
        self.assertIn("setting this will override the host on all Locust classes", response.content.decode("utf-8"))

    def test_swarm_in_step_load_mode(self):
        class MyLocust(Locust):
            wait_time = constant(1)
            class task_set(TaskSet):
                @task(1)
                def my_task(self):
                    pass
        self.environment.locust_classes = [MyLocust]
        self.environment.step_load = True
        response = requests.post(
            "http://127.0.0.1:%i/swarm" % self.web_port,
            data={"locust_count":5, "hatch_rate":2, "step_locust_count":2, "step_duration": "2m"}
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("Step Load Mode", response.text)
