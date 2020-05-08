# -*- coding: utf-8 -*-
import csv
import json
import os
import sys
import traceback
from datetime import datetime, timedelta
from io import StringIO
from tempfile import NamedTemporaryFile

import gevent
import requests
from pyquery import PyQuery as pq

from locust import constant
from locust.argument_parser import get_parser, parse_options
from locust.user import User, task
from locust.env import Environment
from locust.runners import Runner
from locust.web import WebUI

from .testcases import LocustTestCase
from .util import create_tls_cert


class TestWebUI(LocustTestCase):
    def setUp(self):
        super(TestWebUI, self).setUp()

        parser = get_parser(default_config_files=[])
        self.environment.options = parser.parse_args([])
        self.stats = self.environment.stats

        self.web_ui = self.environment.create_web_ui("127.0.0.1", 0)
        self.web_ui.app.view_functions["request_stats"].clear_cache()
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
        web_ui = WebUI(env, "127.0.0.1", 0)
        gevent.sleep(0.01)
        try:
            response = requests.get("http://127.0.0.1:%i/" % web_ui.server.server_port)
            self.assertEqual(500, response.status_code)
            self.assertEqual("Error: Locust Environment does not have any runner", response.text)
        finally:
            web_ui.stop()
    
    def test_index(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/" % self.web_port).status_code)

    def test_index_with_hatch_options(self):
        html_to_option = {
                'user_count':['-u','100'],
                'hatch_rate':['-r','10.0'],
                'step_user_count':['--step-users','20'],
                'step_duration':['--step-time','15'],
                }
        self.environment.step_load = True
        for html_name_to_test in html_to_option.keys():
            # Test that setting each hatch option individually populates the corresponding field in the html, and none of the others
            self.environment.parsed_options = parse_options(html_to_option[html_name_to_test])

            response = requests.get("http://127.0.0.1:%i/" % self.web_port)
            self.assertEqual(200, response.status_code)

            d = pq(response.content.decode('utf-8'))

            for html_name in html_to_option.keys():
                start_value = d(f'.start [name={html_name}]').attr('value')
                edit_value = d(f'.edit [name={html_name}]').attr('value')
                if html_name_to_test == html_name:
                    self.assertEqual(html_to_option[html_name][1], start_value)
                    self.assertEqual(html_to_option[html_name][1], edit_value)
                else:
                    self.assertEqual('', start_value)
                    self.assertEqual('', edit_value)

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
        class MyUser(User):
            wait_time = constant(1)
            @task(1)
            def my_task(self):
                pass
        self.environment.user_classes = [MyUser]
        response = requests.post(
            "http://127.0.0.1:%i/swarm" % self.web_port, 
            data={"user_count": 5, "hatch_rate": 5, "host": "https://localhost"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("https://localhost", response.json()["host"])
        self.assertEqual(self.environment.host, "https://localhost")

    def test_swarm_host_value_not_specified(self):
        class MyUser(User):
            wait_time = constant(1)
            @task(1)
            def my_task(self):
                pass
        self.environment.user_classes = [MyUser]
        response = requests.post(
            "http://127.0.0.1:%i/swarm" % self.web_port, 
            data={'user_count': 5, 'hatch_rate': 5},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(None, response.json()["host"])
        self.assertEqual(self.environment.host, None)
    
    def test_host_value_from_user_class(self):
        class MyUser(User):
            host = "http://example.com"
        self.environment.user_classes = [MyUser]
        response = requests.get("http://127.0.0.1:%i/" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("http://example.com", response.content.decode("utf-8"))
        self.assertNotIn("setting this will override the host on all User classes", response.content.decode("utf-8"))
    
    def test_host_value_from_multiple_user_classes(self):
        class MyUser(User):
            host = "http://example.com"
        class MyUser2(User):
            host = "http://example.com"
        self.environment.user_classes = [MyUser, MyUser2]
        response = requests.get("http://127.0.0.1:%i/" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("http://example.com", response.content.decode("utf-8"))
        self.assertNotIn("setting this will override the host on all User classes", response.content.decode("utf-8"))
    
    def test_host_value_from_multiple_user_classes_different_hosts(self):
        class MyUser(User):
            host = None
        class MyUser2(User):
            host = "http://example.com"
        self.environment.user_classes = [MyUser, MyUser2]
        response = requests.get("http://127.0.0.1:%i/" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertNotIn("http://example.com", response.content.decode("utf-8"))
        self.assertIn("setting this will override the host on all User classes", response.content.decode("utf-8"))

    def test_swarm_in_step_load_mode(self):
        class MyUser(User):
            wait_time = constant(1)
            @task(1)
            def my_task(self):
                pass
        self.environment.user_classes = [MyUser]
        self.environment.step_load = True
        response = requests.post(
            "http://127.0.0.1:%i/swarm" % self.web_port,
            data={"user_count":5, "hatch_rate":2, "step_user_count":2, "step_duration": "2m"}
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("Step Load Mode", response.text)


class TestWebUIAuth(LocustTestCase):
    def setUp(self):
        super(TestWebUIAuth, self).setUp()

        parser = get_parser(default_config_files=[])
        options = parser.parse_args(["--web-auth", "john:doe"])
        self.runner = Runner(self.environment)
        self.stats = self.runner.stats
        self.web_ui = self.environment.create_web_ui("127.0.0.1", 0, auth_credentials=options.web_auth)
        self.web_ui.app.view_functions["request_stats"].clear_cache()
        gevent.sleep(0.01)
        self.web_port = self.web_ui.server.server_port

    def tearDown(self):
        super(TestWebUIAuth, self).tearDown()
        self.web_ui.stop()
        self.runner.quit()

    def test_index_with_basic_auth_enabled_correct_credentials(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/?ele=phino" % self.web_port, auth=('john', 'doe')).status_code)

    def test_index_with_basic_auth_enabled_incorrect_credentials(self):
        self.assertEqual(401, requests.get("http://127.0.0.1:%i/?ele=phino" % self.web_port,
                                           auth=('john', 'invalid')).status_code)

    def test_index_with_basic_auth_enabled_blank_credentials(self):
        self.assertEqual(401, requests.get("http://127.0.0.1:%i/?ele=phino" % self.web_port).status_code)


class TestWebUIWithTLS(LocustTestCase):
    def setUp(self):
        super(TestWebUIWithTLS, self).setUp()
        tls_cert, tls_key = create_tls_cert("127.0.0.1")
        self.tls_cert_file = NamedTemporaryFile(delete=False)
        self.tls_key_file = NamedTemporaryFile(delete=False)
        with open(self.tls_cert_file.name, 'w') as f:
            f.write(tls_cert.decode())
        with open(self.tls_key_file.name, 'w') as f:
            f.write(tls_key.decode())

        parser = get_parser(default_config_files=[])
        options = parser.parse_args([
            "--tls-cert", self.tls_cert_file.name,
            "--tls-key", self.tls_key_file.name,
        ])
        self.runner = Runner(self.environment)
        self.stats = self.runner.stats
        self.web_ui = self.environment.create_web_ui("127.0.0.1", 0, tls_cert=options.tls_cert, tls_key=options.tls_key)
        gevent.sleep(0.01)
        self.web_port = self.web_ui.server.server_port

    def tearDown(self):
        super(TestWebUIWithTLS, self).tearDown()
        self.web_ui.stop()
        self.runner.quit()
        os.unlink(self.tls_cert_file.name)
        os.unlink(self.tls_key_file.name)

    def test_index_with_https(self):
        # Suppress only the single warning from urllib3 needed.
        from urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        self.assertEqual(200, requests.get("https://127.0.0.1:%i/" % self.web_port, verify=False).status_code)
