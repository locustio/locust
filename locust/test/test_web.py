import csv
import json
import os
import traceback
from io import StringIO
from tempfile import NamedTemporaryFile

import gevent
import requests
from pyquery import PyQuery as pq

import locust
from locust import constant
from locust.argument_parser import get_parser, parse_options
from locust.user import User, task
from locust.env import Environment
from locust.runners import Runner
from locust import stats
from locust.stats import StatsCSVFileWriter
from locust.web import WebUI

from .testcases import LocustTestCase
from .util import create_tls_cert


class _HeaderCheckMixin:
    def _check_csv_headers(self, headers, exp_fn_prefix):
        # Check common headers for csv file download request
        self.assertIn("Content-Type", headers)
        content_type = headers["Content-Type"]
        self.assertIn("text/csv", content_type)

        self.assertIn("Content-disposition", headers)
        disposition = headers[
            "Content-disposition"
        ]  # e.g.: 'attachment; filename=requests_full_history_1597586811.5084946.csv'
        self.assertIn(exp_fn_prefix, disposition)


class TestWebUI(LocustTestCase, _HeaderCheckMixin):
    def setUp(self):
        super().setUp()

        parser = get_parser(default_config_files=[])
        self.environment.parsed_options = parser.parse_args([])
        self.stats = self.environment.stats

        self.web_ui = self.environment.create_web_ui("127.0.0.1", 0)
        self.web_ui.app.view_functions["request_stats"].clear_cache()
        gevent.sleep(0.01)
        self.web_port = self.web_ui.server.server_port

    def tearDown(self):
        super().tearDown()
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

    def test_index_with_spawn_options(self):
        html_to_option = {
            "user_count": ["-u", "100"],
            "spawn_rate": ["-r", "10.0"],
        }
        for html_name_to_test in html_to_option.keys():
            # Test that setting each spawn option individually populates the corresponding field in the html, and none of the others
            self.environment.parsed_options = parse_options(html_to_option[html_name_to_test])

            response = requests.get("http://127.0.0.1:%i/" % self.web_port)
            self.assertEqual(200, response.status_code)

            d = pq(response.content.decode("utf-8"))

            for html_name in html_to_option.keys():
                start_value = d(f".start [name={html_name}]").attr("value")
                edit_value = d(f".edit [name={html_name}]").attr("value")
                if html_name_to_test == html_name:
                    self.assertEqual(html_to_option[html_name][1], start_value)
                    self.assertEqual(html_to_option[html_name][1], edit_value)
                else:
                    self.assertEqual("1", start_value, msg=f"start value was {start_value} for {html_name}")
                    self.assertEqual("1", edit_value, msg=f"edit value was {edit_value} for {html_name}")

    def test_stats_no_data(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).status_code)

    def test_stats(self):
        self.stats.log_request("GET", "/<html>", 120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.text)
        self.assertEqual(2, len(data["stats"]))  # one entry plus Aggregated
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
        self.assertEqual(2, len(data["stats"]))  # one entry plus Aggregated

        # add another entry
        self.stats.log_request("GET", "/test2", 120, 5612)
        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).text)
        self.assertEqual(2, len(data["stats"]))  # old value should be cached now

        self.web_ui.app.view_functions["request_stats"].clear_cache()

        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).text)
        self.assertEqual(3, len(data["stats"]))  # this should no longer be cached

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
        self._check_csv_headers(response.headers, "requests")

    def test_request_stats_full_history_csv_not_present(self):
        self.stats.log_request("GET", "/test2", 120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests_full_history/csv" % self.web_port)
        self.assertEqual(404, response.status_code)

    def test_failure_stats_csv(self):
        self.stats.log_error("GET", "/", Exception("Error1337"))
        response = requests.get("http://127.0.0.1:%i/stats/failures/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
        self._check_csv_headers(response.headers, "failures")

    def test_request_stats_with_errors(self):
        self.stats.log_error("GET", "/", Exception("Error1337"))
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertIn("Error1337", response.text)

    def test_reset_stats(self):
        try:
            raise Exception("A cool test exception")
        except Exception as e:
            tb = e.__traceback__
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
            raise Exception("A cool test exception")
        except Exception as e:
            tb = e.__traceback__
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
            tb = e.__traceback__
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))

        response = requests.get("http://127.0.0.1:%i/exceptions/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
        self._check_csv_headers(response.headers, "exceptions")

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
            data={"user_count": 5, "spawn_rate": 5, "host": "https://localhost"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("https://localhost", response.json()["host"])
        self.assertEqual(self.environment.host, "https://localhost")
        # stop
        gevent.sleep(1)
        response = requests.get("http://127.0.0.1:%i/stop" % self.web_port)
        self.assertEqual(response.json()["message"], "Test stopped")
        # and swarm again, with new host
        gevent.sleep(1)
        response = requests.post(
            "http://127.0.0.1:%i/swarm" % self.web_port,
            data={"user_count": 5, "spawn_rate": 5, "host": "https://localhost/other"},
        )
        gevent.sleep(1)
        self.assertEqual(200, response.status_code)
        self.assertEqual("https://localhost/other", response.json()["host"])
        self.assertEqual(self.environment.host, "https://localhost/other")

    def test_swarm_custom_argument(self):
        my_dict = {}

        class MyUser(User):
            host = "http://example.com"
            wait_time = constant(1)

            @task(1)
            def my_task(self):
                my_dict["val"] = self.environment.parsed_options.my_argument

        @locust.events.init_command_line_parser.add_listener
        def _(parser, **kw):
            parser.add_argument("--my-argument", type=int, help="Give me a number")

        self.environment.user_classes = [MyUser]
        self.environment.parsed_options = parse_options(args=["--my-argument", "42"])
        response = requests.post(
            "http://127.0.0.1:%i/swarm" % self.web_port,
            data={"user_count": 1, "spawn_rate": 1, "host": "", "my_argument": "42"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(my_dict["val"], 42)

    def test_swarm_host_value_not_specified(self):
        class MyUser(User):
            wait_time = constant(1)

            @task(1)
            def my_task(self):
                pass

        self.environment.user_classes = [MyUser]
        response = requests.post(
            "http://127.0.0.1:%i/swarm" % self.web_port,
            data={"user_count": 5, "spawn_rate": 5},
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

    def test_report_page(self):
        self.stats.log_request("GET", "/test", 120, 5612)
        r = requests.get("http://127.0.0.1:%i/stats/report" % self.web_port)
        self.assertEqual(200, r.status_code)
        self.assertIn("<title>Test Report for None</title>", r.text)
        self.assertIn("<p>Script: <span>None</span></p>", r.text)
        self.assertIn("charts-container", r.text)
        self.assertIn(
            '<a href="?download=1">Download the Report</a>',
            r.text,
            "Download report link not found in HTML content",
        )

    def test_report_page_empty_stats(self):
        r = requests.get("http://127.0.0.1:%i/stats/report" % self.web_port)
        self.assertEqual(200, r.status_code)
        self.assertIn("<title>Test Report for None</title>", r.text)
        self.assertIn("charts-container", r.text)

    def test_report_download(self):
        self.stats.log_request("GET", "/test", 120, 5612)
        r = requests.get("http://127.0.0.1:%i/stats/report?download=1" % self.web_port)
        self.assertEqual(200, r.status_code)
        self.assertIn("attachment", r.headers.get("Content-Disposition", ""))
        self.assertNotIn("Download the Report", r.text, "Download report link found in HTML content")

    def test_report_host(self):
        self.environment.host = "http://test.com"
        self.stats.log_request("GET", "/test", 120, 5612)
        r = requests.get("http://127.0.0.1:%i/stats/report" % self.web_port)
        self.assertEqual(200, r.status_code)
        self.assertIn("http://test.com", r.text)

    def test_report_host2(self):
        class MyUser(User):
            host = "http://test2.com"

            @task
            def my_task(self):
                pass

        self.environment.host = None
        self.environment.user_classes = [MyUser]
        self.stats.log_request("GET", "/test", 120, 5612)
        r = requests.get("http://127.0.0.1:%i/stats/report" % self.web_port)
        self.assertEqual(200, r.status_code)
        self.assertIn("http://test2.com", r.text)

    def test_report_exceptions(self):
        try:
            raise Exception("Test exception")
        except Exception as e:
            tb = e.__traceback__
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
            self.runner.log_exception("local", str(e), "".join(traceback.format_tb(tb)))
        self.stats.log_request("GET", "/test", 120, 5612)
        r = requests.get("http://127.0.0.1:%i/stats/report" % self.web_port)
        # self.assertEqual(200, r.status_code)
        self.assertIn("<h2>Exceptions Statistics</h2>", r.text)

        # Prior to 088a98bf8ff4035a0de3becc8cd4e887d618af53, the "nodes" field for each exception in
        # "self.runner.exceptions" was accidentally mutated in "get_html_report" to a string.
        # This assertion reproduces the issue and it is left there to make sure there's no
        # regression in the future.
        self.assertTrue(
            isinstance(next(iter(self.runner.exceptions.values()))["nodes"], set), "exception object has been mutated"
        )


class TestWebUIAuth(LocustTestCase):
    def setUp(self):
        super().setUp()

        parser = get_parser(default_config_files=[])
        options = parser.parse_args(["--web-auth", "john:doe"])
        self.runner = Runner(self.environment)
        self.stats = self.runner.stats
        self.web_ui = self.environment.create_web_ui("127.0.0.1", 0, auth_credentials=options.web_auth)
        self.web_ui.app.view_functions["request_stats"].clear_cache()
        gevent.sleep(0.01)
        self.web_port = self.web_ui.server.server_port

    def tearDown(self):
        super().tearDown()
        self.web_ui.stop()
        self.runner.quit()

    def test_index_with_basic_auth_enabled_correct_credentials(self):
        self.assertEqual(
            200, requests.get("http://127.0.0.1:%i/?ele=phino" % self.web_port, auth=("john", "doe")).status_code
        )

    def test_index_with_basic_auth_enabled_incorrect_credentials(self):
        self.assertEqual(
            401, requests.get("http://127.0.0.1:%i/?ele=phino" % self.web_port, auth=("john", "invalid")).status_code
        )

    def test_index_with_basic_auth_enabled_blank_credentials(self):
        self.assertEqual(401, requests.get("http://127.0.0.1:%i/?ele=phino" % self.web_port).status_code)


class TestWebUIWithTLS(LocustTestCase):
    def setUp(self):
        super().setUp()
        tls_cert, tls_key = create_tls_cert("127.0.0.1")
        self.tls_cert_file = NamedTemporaryFile(delete=False)
        self.tls_key_file = NamedTemporaryFile(delete=False)
        with open(self.tls_cert_file.name, "w") as f:
            f.write(tls_cert.decode())
        with open(self.tls_key_file.name, "w") as f:
            f.write(tls_key.decode())

        parser = get_parser(default_config_files=[])
        options = parser.parse_args(
            [
                "--tls-cert",
                self.tls_cert_file.name,
                "--tls-key",
                self.tls_key_file.name,
            ]
        )
        self.runner = Runner(self.environment)
        self.stats = self.runner.stats
        self.web_ui = self.environment.create_web_ui("127.0.0.1", 0, tls_cert=options.tls_cert, tls_key=options.tls_key)
        gevent.sleep(0.01)
        self.web_port = self.web_ui.server.server_port

    def tearDown(self):
        super().tearDown()
        self.web_ui.stop()
        self.runner.quit()
        os.unlink(self.tls_cert_file.name)
        os.unlink(self.tls_key_file.name)

    def test_index_with_https(self):
        # Suppress only the single warning from urllib3 needed.
        from urllib3.exceptions import InsecureRequestWarning

        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        self.assertEqual(200, requests.get("https://127.0.0.1:%i/" % self.web_port, verify=False).status_code)


class TestWebUIFullHistory(LocustTestCase, _HeaderCheckMixin):
    STATS_BASE_NAME = "web_test"
    STATS_FILENAME = f"{STATS_BASE_NAME}_stats.csv"
    STATS_HISTORY_FILENAME = f"{STATS_BASE_NAME}_stats_history.csv"
    STATS_FAILURES_FILENAME = f"{STATS_BASE_NAME}_failures.csv"

    def setUp(self):
        super().setUp()
        self.remove_files_if_exists()

        parser = get_parser(default_config_files=[])
        self.environment.parsed_options = parser.parse_args(["--csv", self.STATS_BASE_NAME, "--csv-full-history"])
        self.stats = self.environment.stats
        self.stats.CSV_STATS_INTERVAL_SEC = 0.02

        locust.stats.CSV_STATS_INTERVAL_SEC = 0.1
        self.stats_csv_writer = StatsCSVFileWriter(
            self.environment, stats.PERCENTILES_TO_REPORT, self.STATS_BASE_NAME, full_history=True
        )
        self.web_ui = self.environment.create_web_ui("127.0.0.1", 0, stats_csv_writer=self.stats_csv_writer)
        self.web_ui.app.view_functions["request_stats"].clear_cache()
        gevent.sleep(0.01)
        self.web_port = self.web_ui.server.server_port

    def tearDown(self):
        super().tearDown()
        self.web_ui.stop()
        self.runner.quit()
        self.remove_files_if_exists()

    def remove_file_if_exists(self, filename):
        if os.path.exists(filename):
            os.remove(filename)

    def remove_files_if_exists(self):
        self.remove_file_if_exists(self.STATS_FILENAME)
        self.remove_file_if_exists(self.STATS_HISTORY_FILENAME)
        self.remove_file_if_exists(self.STATS_FAILURES_FILENAME)

    def test_request_stats_full_history_csv(self):
        self.stats.log_request("GET", "/test", 1.39764125, 2)
        self.stats.log_request("GET", "/test", 999.9764125, 1000)
        self.stats.log_request("GET", "/test2", 120, 5612)

        greenlet = gevent.spawn(self.stats_csv_writer.stats_writer)
        gevent.sleep(0.01)
        self.stats_csv_writer.stats_history_flush()
        gevent.kill(greenlet)

        response = requests.get("http://127.0.0.1:%i/stats/requests_full_history/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
        self._check_csv_headers(response.headers, "requests_full_history")
        self.assertIn("Content-Length", response.headers)

        reader = csv.reader(StringIO(response.text))
        rows = [r for r in reader]

        self.assertEqual(4, len(rows))
        self.assertEqual("Timestamp", rows[0][0])
        self.assertEqual("GET", rows[1][2])
        self.assertEqual("/test", rows[1][3])
        self.assertEqual("/test2", rows[2][3])
        self.assertEqual("", rows[3][2])
        self.assertEqual("Aggregated", rows[3][3])
