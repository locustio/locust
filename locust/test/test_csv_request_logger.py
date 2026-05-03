"""Tests for locust.contrib.csv_request_logger."""

from locust.contrib.csv_request_logger import CSV_COLUMNS, CsvRequestLogger, _status_code
from locust.env import Environment

import csv
import os
import tempfile
import unittest
from unittest.mock import MagicMock


def _make_environment() -> Environment:
    return Environment(events=None, catch_exceptions=False)


def _fire(env: Environment, **overrides):
    """Fire a synthetic request event with sensible defaults."""
    defaults = dict(
        request_type="GET",
        name="/test",
        response_time=123.45,
        response_length=512,
        exception=None,
        response=None,
        start_time=1_700_000_000.0,
        context={},
    )
    defaults.update(overrides)
    env.events.request.fire(**defaults)


class TestStatusCodeHelper(unittest.TestCase):
    def test_http_response_returns_status_code(self):
        resp = MagicMock()
        resp.status_code = 200
        assert _status_code(resp, None) == 200

    def test_exception_without_response_returns_zero(self):
        assert _status_code(None, Exception("conn error")) == 0

    def test_missing_status_code_attribute_returns_zero(self):
        resp = object()  # no status_code attr
        assert _status_code(resp, None) == 0

    def test_non_numeric_status_code_returns_zero(self):
        resp = MagicMock()
        resp.status_code = "bad"
        assert _status_code(resp, None) == 0


class TestCsvRequestLogger(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self._tmpdir.name, "requests.csv")
        self.env = _make_environment()

    def tearDown(self):
        self._tmpdir.cleanup()

    def _read_csv(self):
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    # ------------------------------------------------------------------

    def test_header_row_written_on_register(self):
        log = CsvRequestLogger(self.csv_path)
        log.register(self.env)
        log.close()

        with open(self.csv_path, newline="", encoding="utf-8") as f:
            header = f.readline().strip()

        assert header == ",".join(CSV_COLUMNS)

    def test_successful_request_writes_one_row(self):
        resp = MagicMock()
        resp.status_code = 200

        log = CsvRequestLogger(self.csv_path)
        log.register(self.env)
        _fire(self.env, response=resp)
        log.close()

        rows = self._read_csv()
        assert len(rows) == 1
        row = rows[0]
        assert row["request_type"] == "GET"
        assert row["name"] == "/test"
        assert float(row["response_time_ms"]) == 123.45
        assert int(row["response_length"]) == 512
        assert int(row["status_code"]) == 200
        assert row["exception"] == ""

    def test_failed_request_records_exception_string(self):
        log = CsvRequestLogger(self.csv_path)
        log.register(self.env)
        _fire(self.env, exception=ConnectionError("timeout"), response=None)
        log.close()

        rows = self._read_csv()
        assert len(rows) == 1
        assert int(rows[0]["status_code"]) == 0
        assert "timeout" in rows[0]["exception"]

    def test_multiple_requests_produce_multiple_rows(self):
        log = CsvRequestLogger(self.csv_path)
        log.register(self.env)

        resp = MagicMock()
        resp.status_code = 201
        _fire(self.env, name="/a", response=resp)
        resp2 = MagicMock()
        resp2.status_code = 404
        _fire(self.env, name="/b", response=resp2)
        log.close()

        rows = self._read_csv()
        assert len(rows) == 2
        assert rows[0]["name"] == "/a"
        assert int(rows[0]["status_code"]) == 201
        assert rows[1]["name"] == "/b"
        assert int(rows[1]["status_code"]) == 404

    def test_timestamp_uses_start_time_when_provided(self):
        log = CsvRequestLogger(self.csv_path)
        log.register(self.env)
        _fire(self.env, start_time=9_999_999.123456)
        log.close()

        rows = self._read_csv()
        assert float(rows[0]["timestamp"]) == 9_999_999.123456

    def test_quitting_event_closes_file(self):
        log = CsvRequestLogger(self.csv_path)
        log.register(self.env)
        _fire(self.env)

        # simulate Locust shutdown
        self.env.events.quitting.fire(environment=self.env, exitcode=0)

        # file must be flushed and closed — re-opening should succeed
        rows = self._read_csv()
        assert len(rows) == 1

    def test_close_is_idempotent(self):
        log = CsvRequestLogger(self.csv_path)
        log.register(self.env)
        log.close()
        log.close()  # must not raise

    def test_flush_interval_respected(self):
        """Logger with flush_interval=3 should buffer rows without crashing."""
        log = CsvRequestLogger(self.csv_path, flush_interval=3)
        log.register(self.env)

        for i in range(5):
            _fire(self.env, name=f"/route/{i}")
        log.close()

        rows = self._read_csv()
        assert len(rows) == 5

    def test_custom_protocol_request_type(self):
        """Non-HTTP request types (WebSocket, gRPC, etc.) are recorded as-is."""
        log = CsvRequestLogger(self.csv_path)
        log.register(self.env)
        _fire(self.env, request_type="WS", name="message/send")
        log.close()

        rows = self._read_csv()
        assert rows[0]["request_type"] == "WS"

    def test_no_rows_written_after_close(self):
        """Events fired after close() are silently ignored."""
        log = CsvRequestLogger(self.csv_path)
        log.register(self.env)
        log.close()

        # fire AFTER close — must not raise, must not append rows
        _fire(self.env)

        rows = self._read_csv()
        assert len(rows) == 0


if __name__ == "__main__":
    unittest.main()
