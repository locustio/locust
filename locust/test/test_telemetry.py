import textwrap
import unittest

from .mock_locustfile import mock_locustfile
from .subprocess_utils import TestProcess


class TelemetryTests(unittest.TestCase):
    def test_otel_flag(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path}",
                expect_return_code=None,
            ) as tp:
                tp.expect("Starting Locust")
                tp.not_expect_any("OpenTelemetry enabled")

            with TestProcess(
                f"locust -f {mocked.file_path} --otel",
                expect_return_code=None,
            ) as tp:
                tp.expect("Starting Locust")
                tp.expect_any("OpenTelemetry enabled")

    def test_httpuser(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless -u 1 --otel --run-time 1s",
                expect_return_code=None,
                env={
                    "OTEL_METRICS_EXPORTER": "console",
                    "OTEL_TRACES_EXPORTER": "console",
                },
            ) as tp:
                tp.expect("OpenTelemetry enabled")
                tp.expect("trace_id", stream="stdout")
                tp.expect("resource_metrics", stream="stdout")

    def test_request_name(self):
        locustfile = textwrap.dedent(
            """
            from locust import HttpUser, task, constant

            class TestUser(HttpUser):
                host = "http://www.locust.cloud"
                wait_time = constant(1)

                @task
                def t(self):
                    self.client.get("/hello")
                    self.client.get("/world", name="/custom-name")
            """
        )
        with mock_locustfile(content=locustfile) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless -u 1 --otel --run-time 1s",
                expect_return_code=None,
                env={
                    "OTEL_METRICS_EXPORTER": "none",
                    "OTEL_TRACES_EXPORTER": "console",
                },
            ) as tp:
                tp.expect("GET /hello", stream="stdout")
                tp.expect("GET /custom-name", stream="stdout")
                tp.not_expect_any("GET /world", stream="stdout")
