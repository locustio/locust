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
