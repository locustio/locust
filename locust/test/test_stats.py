import locust
from locust import HttpUser, TaskSet, User, __version__, constant, task
from locust.env import Environment
from locust.rpc.protocol import Message
from locust.stats import (
    PERCENTILES_TO_REPORT,
    STATS_NAME_WIDTH,
    STATS_TYPE_WIDTH,
    CachedResponseTimes,
    RequestStats,
    StatsCSVFileWriter,
    StatsEntry,
    diff_response_time_dicts,
    stats_history,
)
from locust.test.test_runners import mocked_rpc
from locust.test.testcases import LocustTestCase, WebserverTestCase
from locust.user.inspectuser import _get_task_ratio

import csv
import json
import os
import re
import time
import unittest
from collections import OrderedDict
from io import StringIO
from unittest import mock

import gevent

_TEST_CSV_STATS_INTERVAL_SEC = 0.2
_TEST_CSV_STATS_INTERVAL_WAIT_SEC = _TEST_CSV_STATS_INTERVAL_SEC + 0.1

_TEST_PERCENTILES_TO_CHART_MANY = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
_TEST_PERCENTILES_TOO_HIGH = [1.5, 2.95]
_TEST_PERCENTILES_WRONG_TYPE = ["a", "b"]


def _write_csv_files(environment, stats_base_name, full_history=False):
    """Spawn CVS writer and exit loop after first iteration."""
    stats_writer = StatsCSVFileWriter(environment, PERCENTILES_TO_REPORT, stats_base_name, full_history=full_history)
    greenlet = gevent.spawn(stats_writer)
    gevent.sleep(_TEST_CSV_STATS_INTERVAL_WAIT_SEC)
    gevent.kill(greenlet)
    stats_writer.close_files()


class TestStatsValidation(unittest.TestCase):
    def test_stats_validation_normal_no_return_exit(self):
        assert locust.stats.validate_stats_configuration() is None

    @mock.patch("locust.stats.PERCENTILES_TO_CHART", new=_TEST_PERCENTILES_TO_CHART_MANY)
    def test_stats_validation_fail_on_too_many_percentiles_to_chart(self):
        out = StringIO()
        with mock.patch("sys.stderr", new=out):
            with self.assertRaises(SystemExit) as error:
                locust.stats.validate_stats_configuration()
        out.seek(0)
        stderr = out.read()
        self.assertEqual(error.exception.code, 1)
        self.assertIn("should be a maximum of 6 parameters", stderr)

    @mock.patch("locust.stats.PERCENTILES_TO_CHART", new=_TEST_PERCENTILES_TOO_HIGH)
    def test_stats_validation_fail_on_too_high_chart_value(self):
        out = StringIO()
        with mock.patch("sys.stderr", new=out):
            with self.assertRaises(SystemExit) as error:
                locust.stats.validate_stats_configuration()
        out.seek(0)
        stderr = out.read()
        self.assertEqual(error.exception.code, 1)
        self.assertIn("value between. 0 < percentile < 1 Eg 0.95", stderr)

    @mock.patch("locust.stats.PERCENTILES_TO_STATISTICS", new=_TEST_PERCENTILES_TOO_HIGH)
    def test_stats_validation_fail_on_too_high_statistic_value(self):
        out = StringIO()
        with mock.patch("sys.stderr", new=out):
            with self.assertRaises(SystemExit) as error:
                locust.stats.validate_stats_configuration()
        out.seek(0)
        stderr = out.read()
        self.assertEqual(error.exception.code, 1)
        self.assertIn("value between. 0 < percentile < 1 Eg 0.95", stderr)

    @mock.patch("locust.stats.PERCENTILES_TO_CHART", new=_TEST_PERCENTILES_WRONG_TYPE)
    def test_stats_validation_fail_on_wrong_type_chart_value(self):
        out = StringIO()
        with mock.patch("sys.stderr", new=out):
            with self.assertRaises(SystemExit) as error:
                locust.stats.validate_stats_configuration()
        out.seek(0)
        stderr = out.read()
        self.assertEqual(error.exception.code, 1)
        self.assertIn("need to be float", stderr)

    @mock.patch("locust.stats.PERCENTILES_TO_STATISTICS", new=_TEST_PERCENTILES_WRONG_TYPE)
    def test_stats_validation_fail_on_wrong_type_statistic_value(self):
        out = StringIO()
        with mock.patch("sys.stderr", new=out):
            with self.assertRaises(SystemExit) as error:
                locust.stats.validate_stats_configuration()
        out.seek(0)
        stderr = out.read()
        self.assertEqual(error.exception.code, 1)
        self.assertIn("need to be float", stderr)


class TestRequestStats(unittest.TestCase):
    def setUp(self):
        locust.stats.PERCENTILES_TO_REPORT = PERCENTILES_TO_REPORT
        self.stats = RequestStats()

        def log(response_time, size):
            self.stats.log_request("GET", "test_entry", response_time, size)

        def log_error(exc):
            self.stats.log_error("GET", "test_entry", exc)

        log(45, 1)
        log(135, 1)
        log(44, 1)
        log(None, 1)
        log_error(Exception("dummy fail"))
        log_error(Exception("dummy fail"))
        log(375, 1)
        log(601, 1)
        log(35, 1)
        log(79, 1)
        log(None, 1)
        log_error(Exception("dummy fail"))
        self.s = self.stats.entries[("test_entry", "GET")]

    def test_percentile(self):
        s = StatsEntry(self.stats, "percentile_test", "GET")
        for x in range(100):
            s.log(x, 0)

        self.assertEqual(s.get_response_time_percentile(0.5), 50)
        self.assertEqual(s.get_response_time_percentile(0.6), 60)
        self.assertEqual(s.get_response_time_percentile(0.95), 95)

    def test_median(self):
        self.assertEqual(self.s.median_response_time, 79)

    def test_median_out_of_min_max_bounds(self):
        s = StatsEntry(self.stats, "median_test", "GET")
        s.log(6034, 0)
        self.assertEqual(s.median_response_time, 6034)
        s.reset()
        s.log(6099, 0)
        self.assertEqual(s.median_response_time, 6099)

    def test_total_rps(self):
        self.stats.log_request("GET", "other_endpoint", 1337, 1337)
        s2 = self.stats.entries[("other_endpoint", "GET")]
        s2.start_time = 2.0
        s2.last_request_timestamp = 6.0
        self.s.start_time = 1.0
        self.s.last_request_timestamp = 4.0
        self.stats.total.start_time = 1.0
        self.stats.total.last_request_timestamp = 6.0
        self.assertEqual(self.s.total_rps, 9 / 5.0)
        self.assertAlmostEqual(s2.total_rps, 1 / 5.0)
        self.assertEqual(self.stats.total.total_rps, 10 / 5.0)

    def test_rps_less_than_one_second(self):
        s = StatsEntry(self.stats, "percentile_test", "GET")
        for i in range(10):
            s.log(i, 0)
        self.assertGreater(s.total_rps, 10)

    def test_current_rps(self):
        self.stats.total.last_request_timestamp = int(time.time()) + 4
        self.assertEqual(self.s.current_rps, 4.5)

        self.stats.total.last_request_timestamp = int(time.time()) + 25
        self.assertEqual(self.s.current_rps, 0)

    def test_current_fail_per_sec(self):
        self.stats.total.last_request_timestamp = int(time.time()) + 4
        self.assertEqual(self.s.current_fail_per_sec, 1.5)

        self.stats.total.last_request_timestamp = int(time.time()) + 12
        self.assertEqual(self.s.current_fail_per_sec, 0.3)

        self.stats.total.last_request_timestamp = int(time.time()) + 25
        self.assertEqual(self.s.current_fail_per_sec, 0)

    def test_num_reqs_fails(self):
        self.assertEqual(self.s.num_requests, 9)
        self.assertEqual(self.s.num_failures, 3)

    def test_avg(self):
        self.assertEqual(self.s.avg_response_time, 187.71428571428572)

    def test_total_content_length(self):
        self.assertEqual(self.s.total_content_length, 9)

    def test_reset(self):
        self.s.reset()
        self.s.log(756, 0)
        self.s.log_error(Exception("dummy fail after reset"))
        self.s.log(85, 0)

        self.assertGreater(self.s.total_rps, 2)
        self.assertEqual(self.s.num_requests, 2)
        self.assertEqual(self.s.num_failures, 1)
        self.assertEqual(self.s.avg_response_time, 420.5)
        self.assertEqual(self.s.median_response_time, 85)
        self.assertNotEqual(None, self.s.last_request_timestamp)
        self.s.reset()
        self.assertEqual(None, self.s.last_request_timestamp)

    def test_avg_only_none(self):
        self.s.reset()
        self.s.log(None, 123)
        self.assertEqual(self.s.avg_response_time, 0)
        self.assertEqual(self.s.median_response_time, 0)
        self.assertEqual(self.s.get_response_time_percentile(0.5), 0)

    def test_reset_min_response_time(self):
        self.s.reset()
        self.s.log(756, 0)
        self.assertEqual(756, self.s.min_response_time)

    def test_aggregation(self):
        s1 = StatsEntry(self.stats, "aggregate me!", "GET")
        s1.log(12, 0)
        s1.log(12, 0)
        s1.log(38, 0)
        s1.log_error("Dummy exception")

        s2 = StatsEntry(self.stats, "aggregate me!", "GET")
        s2.log_error("Dummy exception")
        s2.log_error("Dummy exception")
        s2.log(12, 0)
        s2.log(99, 0)
        s2.log(14, 0)
        s2.log(55, 0)
        s2.log(38, 0)
        s2.log(55, 0)
        s2.log(97, 0)

        s = StatsEntry(self.stats, "GET", "")
        s.extend(s1)
        s.extend(s2)

        self.assertEqual(s.num_requests, 10)
        self.assertEqual(s.num_failures, 3)
        self.assertEqual(s.median_response_time, 38)
        self.assertEqual(s.avg_response_time, 43.2)

    def test_aggregation_with_rounding(self):
        s1 = StatsEntry(self.stats, "round me!", "GET")
        s1.log(122, 0)  # (rounded 120) min
        s1.log(992, 0)  # (rounded 990) max
        s1.log(142, 0)  # (rounded 140)
        s1.log(552, 0)  # (rounded 550)
        s1.log(557, 0)  # (rounded 560)
        s1.log(387, 0)  # (rounded 390)
        s1.log(557, 0)  # (rounded 560)
        s1.log(977, 0)  # (rounded 980)

        self.assertEqual(s1.num_requests, 8)
        self.assertEqual(s1.median_response_time, 550)
        self.assertEqual(s1.avg_response_time, 535.75)
        self.assertEqual(s1.min_response_time, 122)
        self.assertEqual(s1.max_response_time, 992)

    def test_aggregation_with_decimal_rounding(self):
        s1 = StatsEntry(self.stats, "round me!", "GET")
        s1.log(1.1, 0)
        s1.log(1.99, 0)
        s1.log(3.1, 0)
        self.assertEqual(s1.num_requests, 3)
        self.assertEqual(s1.median_response_time, 2)
        self.assertEqual(s1.avg_response_time, (1.1 + 1.99 + 3.1) / 3)
        self.assertEqual(s1.min_response_time, 1.1)
        self.assertEqual(s1.max_response_time, 3.1)

    def test_aggregation_min_response_time(self):
        s1 = StatsEntry(self.stats, "min", "GET")
        s1.log(10, 0)
        self.assertEqual(10, s1.min_response_time)
        s2 = StatsEntry(self.stats, "min", "GET")
        s1.extend(s2)
        self.assertEqual(10, s1.min_response_time)

    def test_aggregation_last_request_timestamp(self):
        s1 = StatsEntry(self.stats, "r", "GET")
        s2 = StatsEntry(self.stats, "r", "GET")
        s1.extend(s2)
        self.assertEqual(None, s1.last_request_timestamp)
        s1 = StatsEntry(self.stats, "r", "GET")
        s2 = StatsEntry(self.stats, "r", "GET")
        s1.last_request_timestamp = 666
        s1.extend(s2)
        self.assertEqual(666, s1.last_request_timestamp)
        s1 = StatsEntry(self.stats, "r", "GET")
        s2 = StatsEntry(self.stats, "r", "GET")
        s2.last_request_timestamp = 666
        s1.extend(s2)
        self.assertEqual(666, s1.last_request_timestamp)
        s1 = StatsEntry(self.stats, "r", "GET")
        s2 = StatsEntry(self.stats, "r", "GET")
        s1.last_request_timestamp = 666
        s1.last_request_timestamp = 700
        s1.extend(s2)
        self.assertEqual(700, s1.last_request_timestamp)

    def test_percentile_rounded_down(self):
        s1 = StatsEntry(self.stats, "rounding down!", "GET")
        s1.log(122, 0)  # (rounded 120) min
        actual_percentile = s1.percentile().split()

        self.assertEqual(actual_percentile, ["GET", "rounding", "down!"] + ["120"] * len(PERCENTILES_TO_REPORT) + ["1"])

    def test_percentile_rounded_up(self):
        s2 = StatsEntry(self.stats, "rounding up!", "GET")
        s2.log(127, 0)  # (rounded 130) min
        actual_percentile = s2.percentile().split()
        self.assertEqual(actual_percentile, ["GET", "rounding", "up!"] + ["130"] * len(PERCENTILES_TO_REPORT) + ["1"])

    def test_custom_percentile_list(self):
        s = StatsEntry(self.stats, "custom_percentiles", "GET")
        custom_percentile_list = [0.50, 0.90, 0.95, 0.99]
        locust.stats.PERCENTILES_TO_REPORT = custom_percentile_list
        s.log(150, 0)
        actual_percentile = s.percentile().split()
        self.assertEqual(
            actual_percentile, ["GET", "custom_percentiles"] + ["150"] * len(custom_percentile_list) + ["1"]
        )

    def test_error_grouping(self):
        # reset stats
        self.stats = RequestStats()

        self.stats.log_error("GET", "/some-path", Exception("Exception!"))
        self.stats.log_error("GET", "/some-path", Exception("Exception!"))

        self.assertEqual(1, len(self.stats.errors))
        self.assertEqual(2, list(self.stats.errors.values())[0].occurrences)

        self.stats.log_error("GET", "/some-path", Exception("Another exception!"))
        self.stats.log_error("GET", "/some-path", Exception("Another exception!"))
        self.stats.log_error("GET", "/some-path", Exception("Third exception!"))
        self.assertEqual(3, len(self.stats.errors))

    def test_error_grouping_errors_with_memory_addresses(self):
        # reset stats
        self.stats = RequestStats()

        class Dummy:
            pass

        self.stats.log_error("GET", "/", Exception(f"Error caused by {Dummy()!r}"))
        self.assertEqual(1, len(self.stats.errors))

    def test_serialize_through_message(self):
        """
        Serialize a RequestStats instance, then serialize it through a Message,
        and unserialize the whole thing again. This is done "IRL" when stats are sent
        from workers to master.
        """
        s1 = StatsEntry(self.stats, "test", "GET")
        s1.log(10, 0)
        s1.log(20, 0)
        s1.log(40, 0)
        u1 = StatsEntry.unserialize(s1.serialize())

        data = Message.unserialize(Message("dummy", s1.serialize(), "none").serialize()).data
        u1 = StatsEntry.unserialize(data)

        self.assertEqual(20, u1.median_response_time)


class TestStatsPrinting(LocustTestCase):
    def setUp(self):
        super().setUp()

        self.stats = RequestStats()
        for i in range(100):
            for method, name, freq in [
                (
                    "GET",
                    "test_entry",
                    5,
                ),
                (
                    "DELETE",
                    "test" * int((STATS_NAME_WIDTH - STATS_TYPE_WIDTH + 4) / len("test")),
                    3,
                ),
            ]:
                self.stats.log_request(method, name, i, 2000 + i)
                if i % freq == 0:
                    self.stats.log_error(method, name, RuntimeError(f"{method} error"))

    def test_print_percentile_stats(self):
        locust.stats.print_percentile_stats(self.stats)
        info = self.mocked_log.info
        self.assertEqual(8, len(info))
        self.assertEqual("Response time percentiles (approximated)", info[0])
        # check that headline contains same number of column as the value rows
        headlines = info[1].replace("# reqs", "#reqs").split()
        self.assertEqual(len(headlines), len(info[3].split()))
        self.assertEqual(len(headlines) - 1, len(info[-2].split()))  # Aggregated, no "Type"
        self.assertEqual(info[2], info[-3])  # table ascii separators

    def test_print_stats(self):
        locust.stats.print_stats(self.stats)
        info = self.mocked_log.info
        self.assertEqual(7, len(info))

        headlines = info[0].replace("# ", "#").split()

        # check number of columns in separator
        self.assertEqual(len(headlines), len(info[1].split("|")) + 2)
        # check entry row
        self.assertEqual(len(headlines), len(info[2].split()))
        # check aggregated row, which is missing value in "type"-column
        self.assertEqual(len(headlines) - 1, len(info[-2].split()))
        # table ascii separators
        self.assertEqual(info[1], info[-3])

    def test_print_error_report(self):
        locust.stats.print_error_report(self.stats)
        info = self.mocked_log.info
        self.assertEqual(7, len(info))
        self.assertEqual("Error report", info[0])

        headlines = info[1].replace("# ", "#").split()
        # check number of columns in headlines vs table ascii separator
        self.assertEqual(len(headlines), len(info[2].split("|")))
        # table ascii separators
        self.assertEqual(info[2], info[-2])


class TestCsvStats(LocustTestCase):
    STATS_BASE_NAME = "test"
    STATS_FILENAME = f"{STATS_BASE_NAME}_stats.csv"
    STATS_HISTORY_FILENAME = f"{STATS_BASE_NAME}_stats_history.csv"
    STATS_FAILURES_FILENAME = f"{STATS_BASE_NAME}_failures.csv"
    STATS_EXCEPTIONS_FILENAME = f"{STATS_BASE_NAME}_exceptions.csv"

    def setUp(self):
        super().setUp()
        self.remove_file_if_exists(self.STATS_FILENAME)
        self.remove_file_if_exists(self.STATS_HISTORY_FILENAME)
        self.remove_file_if_exists(self.STATS_FAILURES_FILENAME)
        self.remove_file_if_exists(self.STATS_EXCEPTIONS_FILENAME)

    def tearDown(self):
        self.remove_file_if_exists(self.STATS_FILENAME)
        self.remove_file_if_exists(self.STATS_HISTORY_FILENAME)
        self.remove_file_if_exists(self.STATS_FAILURES_FILENAME)
        self.remove_file_if_exists(self.STATS_EXCEPTIONS_FILENAME)

    def remove_file_if_exists(self, filename):
        if os.path.exists(filename):
            os.remove(filename)

    def test_write_csv_files(self):
        _write_csv_files(self.environment, self.STATS_BASE_NAME)
        self.assertTrue(os.path.exists(self.STATS_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_HISTORY_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_FAILURES_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_EXCEPTIONS_FILENAME))

    def test_write_csv_files_full_history(self):
        _write_csv_files(self.environment, self.STATS_BASE_NAME, full_history=True)
        self.assertTrue(os.path.exists(self.STATS_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_HISTORY_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_FAILURES_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_EXCEPTIONS_FILENAME))

    @mock.patch("locust.stats.CSV_STATS_INTERVAL_SEC", new=_TEST_CSV_STATS_INTERVAL_SEC)
    def test_csv_stats_writer(self):
        _write_csv_files(self.environment, self.STATS_BASE_NAME)

        self.assertTrue(os.path.exists(self.STATS_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_HISTORY_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_FAILURES_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_EXCEPTIONS_FILENAME))

        with open(self.STATS_HISTORY_FILENAME) as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader]

        self.assertEqual(2, len(rows))
        self.assertEqual("Aggregated", rows[0]["Name"])
        self.assertEqual("Aggregated", rows[1]["Name"])

    @mock.patch("locust.stats.CSV_STATS_INTERVAL_SEC", new=_TEST_CSV_STATS_INTERVAL_SEC)
    def test_csv_stats_writer_full_history(self):
        stats_writer = StatsCSVFileWriter(
            self.environment, PERCENTILES_TO_REPORT, self.STATS_BASE_NAME, full_history=True
        )

        for i in range(10):
            self.runner.stats.log_request("GET", "/", 100, content_length=666)

        greenlet = gevent.spawn(stats_writer)
        gevent.sleep(10)

        for i in range(10):
            self.runner.stats.log_request("GET", "/", 10, content_length=666)

        gevent.sleep(5)

        gevent.sleep(_TEST_CSV_STATS_INTERVAL_WAIT_SEC)
        gevent.kill(greenlet)
        stats_writer.close_files()

        self.assertTrue(os.path.exists(self.STATS_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_HISTORY_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_FAILURES_FILENAME))
        self.assertTrue(os.path.exists(self.STATS_EXCEPTIONS_FILENAME))

        with open(self.STATS_HISTORY_FILENAME) as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader]

        self.assertGreaterEqual(len(rows), 130)

        self.assertEqual("/", rows[0]["Name"])
        self.assertEqual("Aggregated", rows[1]["Name"])
        self.assertEqual("/", rows[2]["Name"])
        self.assertEqual("Aggregated", rows[3]["Name"])
        self.assertEqual("20", rows[-1]["Total Request Count"])

        saw100 = False
        saw10 = False

        for row in rows:
            if not saw100 and row["95%"] == "100":
                saw100 = True
            elif saw100 and row["95%"] == "10":
                saw10 = True
                break

        self.assertTrue(saw100, "Never saw 95th percentile increase to 100")
        self.assertTrue(saw10, "Never saw 95th percentile decrease to 10")

    def test_csv_stats_on_master_from_aggregated_stats(self):
        # Failing test for: https://github.com/locustio/locust/issues/1315
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            environment = Environment()
            stats_writer = StatsCSVFileWriter(
                environment, PERCENTILES_TO_REPORT, self.STATS_BASE_NAME, full_history=True
            )
            master = environment.create_master_runner(master_bind_host="*", master_bind_port=0)
            greenlet = gevent.spawn(stats_writer)
            gevent.sleep(_TEST_CSV_STATS_INTERVAL_WAIT_SEC)

            server.mocked_send(Message("client_ready", __version__, "fake_client"))

            master.stats.entries[("/", "GET")].log(100, 23455)
            master.stats.entries[("/", "GET")].log(800, 23455)
            master.stats.entries[("/", "GET")].log(700, 23455)

            data = {"user_count": 1}
            environment.events.report_to_master.fire(client_id="fake_client", data=data)
            master.stats.clear_all()

            server.mocked_send(Message("stats", data, "fake_client"))
            s = master.stats.entries[("/", "GET")]
            self.assertEqual(700, s.median_response_time)

            gevent.kill(greenlet)
            stats_writer.close_files()

            self.assertTrue(os.path.exists(self.STATS_FILENAME))
            self.assertTrue(os.path.exists(self.STATS_HISTORY_FILENAME))
            self.assertTrue(os.path.exists(self.STATS_FAILURES_FILENAME))
            self.assertTrue(os.path.exists(self.STATS_EXCEPTIONS_FILENAME))

    @mock.patch("locust.stats.CSV_STATS_INTERVAL_SEC", new=_TEST_CSV_STATS_INTERVAL_SEC)
    def test_user_count_in_csv_history_stats(self):
        start_time = int(time.time())

        class TestUser(User):
            wait_time = constant(10)

            @task
            def t(self):
                self.environment.runner.stats.log_request("GET", "/", 10, 10)

        environment = Environment(user_classes=[TestUser])
        stats_writer = StatsCSVFileWriter(environment, PERCENTILES_TO_REPORT, self.STATS_BASE_NAME, full_history=True)
        runner = environment.create_local_runner()
        # spawn a user every _TEST_CSV_STATS_INTERVAL_SEC second
        user_count = 15
        spawn_rate = 5
        assert 1 / 5 == _TEST_CSV_STATS_INTERVAL_SEC
        runner_greenlet = gevent.spawn(runner.start, user_count, spawn_rate)
        gevent.sleep(0.1)

        greenlet = gevent.spawn(stats_writer)
        gevent.sleep(user_count / spawn_rate)
        gevent.kill(greenlet)
        stats_writer.close_files()
        runner.stop()
        gevent.kill(runner_greenlet)

        with open(self.STATS_HISTORY_FILENAME) as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader]

        self.assertEqual(2 * user_count, len(rows))
        for i in range(int(user_count / spawn_rate)):
            for _ in range(spawn_rate):
                row = rows.pop(0)
                self.assertEqual("%i" % ((i + 1) * spawn_rate), row["User Count"])
                self.assertEqual("/", row["Name"])
                self.assertEqual("%i" % ((i + 1) * spawn_rate), row["Total Request Count"])
                self.assertGreaterEqual(int(row["Timestamp"]), start_time)
                row = rows.pop(0)
                self.assertEqual("%i" % ((i + 1) * spawn_rate), row["User Count"])
                self.assertEqual("Aggregated", row["Name"])
                self.assertEqual("%i" % ((i + 1) * spawn_rate), row["Total Request Count"])
                self.assertGreaterEqual(int(row["Timestamp"]), start_time)

    def test_requests_csv_quote_escaping(self):
        with mock.patch("locust.rpc.rpc.Server", mocked_rpc()) as server:
            environment = Environment()
            master = environment.create_master_runner(master_bind_host="*", master_bind_port=0)
            server.mocked_send(Message("client_ready", __version__, "fake_client"))

            request_name_dict = {
                "scenario": "get cashes",
                "path": "/cash/[amount]",
                "arguments": [{"size": 1}],
            }
            request_name_str = json.dumps(request_name_dict)

            master.stats.entries[(request_name_str, "GET")].log(100, 23455)
            data = {"user_count": 1}
            environment.events.report_to_master.fire(client_id="fake_client", data=data)
            master.stats.clear_all()
            server.mocked_send(Message("stats", data, "fake_client"))

            _write_csv_files(environment, self.STATS_BASE_NAME, full_history=True)
            with open(self.STATS_FILENAME) as f:
                reader = csv.DictReader(f)
                rows = [r for r in reader]
                csv_request_name = rows[0].get("Name")
                self.assertEqual(request_name_str, csv_request_name)

    def test_stats_history(self):
        env1 = Environment(events=locust.events, catch_exceptions=False)
        runner1 = env1.create_master_runner("127.0.0.1", 5558)
        runner1.state = "running"
        env2 = Environment(events=locust.events, catch_exceptions=False)
        runner2 = env2.create_worker_runner("127.0.0.1", 5558)
        greenlet1 = gevent.spawn(stats_history, runner1)
        greenlet2 = gevent.spawn(stats_history, runner2)
        gevent.sleep(0.1)
        hs1 = runner1.stats.history
        hs2 = runner2.stats.history
        gevent.kill(greenlet1)
        gevent.kill(greenlet2)
        self.assertEqual(1, len(hs1))
        self.assertEqual(0, len(hs2))


class TestStatsEntryResponseTimesCache(unittest.TestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.stats = RequestStats()

    def test_response_times_cached(self):
        s = StatsEntry(self.stats, "/", "GET", use_response_times_cache=True)
        self.assertEqual(1, len(s.response_times_cache))
        s.log(11, 1337)
        self.assertEqual(1, len(s.response_times_cache))
        s.last_request_timestamp -= 1
        s.log(666, 1337)
        self.assertEqual(2, len(s.response_times_cache))
        self.assertEqual(
            CachedResponseTimes(
                response_times={11: 1},
                num_requests=1,
            ),
            s.response_times_cache[int(s.last_request_timestamp) - 1],
        )

    def test_response_times_not_cached_if_not_enabled(self):
        s = StatsEntry(self.stats, "/", "GET")
        s.log(11, 1337)
        self.assertEqual(None, s.response_times_cache)
        s.last_request_timestamp -= 1
        s.log(666, 1337)
        self.assertEqual(None, s.response_times_cache)

    def test_latest_total_response_times_pruned(self):
        """
        Check that RequestStats.latest_total_response_times are pruned when exceeding 20 entries
        """
        s = StatsEntry(self.stats, "/", "GET", use_response_times_cache=True)
        t = int(time.time())
        for i in reversed(range(2, 30)):
            s.response_times_cache[t - i] = CachedResponseTimes(response_times={}, num_requests=0)
        self.assertEqual(29, len(s.response_times_cache))
        s.log(17, 1337)
        s.last_request_timestamp -= 1
        s.log(1, 1)
        self.assertEqual(20, len(s.response_times_cache))
        self.assertEqual(
            CachedResponseTimes(response_times={17: 1}, num_requests=1),
            s.response_times_cache.popitem(last=True)[1],
        )

    def test_get_current_response_time_percentile(self):
        s = StatsEntry(self.stats, "/", "GET", use_response_times_cache=True)
        t = int(time.time())
        s.response_times_cache[t - 10] = CachedResponseTimes(
            response_times={i: 1 for i in range(100)}, num_requests=200
        )
        s.response_times_cache[t - 10].response_times[1] = 201

        s.response_times = {i: 2 for i in range(100)}
        s.response_times[1] = 202
        s.num_requests = 300

        self.assertEqual(95, s.get_current_response_time_percentile(0.95))

    def test_get_current_response_time_percentile_outside_cache_window(self):
        s = StatsEntry(self.stats, "/", "GET", use_response_times_cache=True)
        # an empty response times cache, current time will not be in this cache
        s.response_times_cache = {}
        self.assertEqual(None, s.get_current_response_time_percentile(0.95))

    def test_diff_response_times_dicts(self):
        self.assertEqual(
            {1: 5, 6: 8},
            diff_response_time_dicts(
                {1: 6, 6: 16, 2: 2},
                {1: 1, 6: 8, 2: 2},
            ),
        )
        self.assertEqual(
            {},
            diff_response_time_dicts(
                {},
                {},
            ),
        )
        self.assertEqual(
            {10: 15},
            diff_response_time_dicts(
                {10: 15},
                {},
            ),
        )
        self.assertEqual(
            {10: 10},
            diff_response_time_dicts(
                {10: 10},
                {},
            ),
        )
        self.assertEqual(
            {},
            diff_response_time_dicts(
                {1: 1},
                {1: 1},
            ),
        )

    def test_unserialize_with_response_times_cache_parameter(self):
        """Test the use_response_times_cache parameter in StatsEntry.unserialize()"""
        # Create an entry with caching enabled and log the data.
        s1 = StatsEntry(self.stats, "/test", "GET", use_response_times_cache=True)
        s1.log(100, 1000)
        s1.log(200, 2000)
        s1.log(300, 3000)

        # Serialized data
        serialized = s1.serialize()

        # test1: use_response_times_cache=False
        s2_no_cache = StatsEntry.unserialize(serialized, use_response_times_cache=False)

        # test2: use_response_times_cache=True
        s2_with_cache = StatsEntry.unserialize(serialized, use_response_times_cache=True)

        # Verify basic data consistency
        self.assertEqual(s2_no_cache.num_requests, 3)
        self.assertEqual(s2_no_cache.total_response_time, 600)
        self.assertEqual(s2_no_cache.avg_response_time, 200)

        self.assertEqual(s2_with_cache.num_requests, 3)
        self.assertEqual(s2_with_cache.total_response_time, 600)
        self.assertEqual(s2_with_cache.avg_response_time, 200)

        # verify use_response_times_cach
        self.assertFalse(s2_no_cache.use_response_times_cache)
        self.assertTrue(s2_with_cache.use_response_times_cache)

        # verify response_times_cache
        self.assertIsNone(s2_no_cache.response_times_cache)
        self.assertIsNotNone(s2_with_cache.response_times_cache)
        self.assertIsInstance(s2_with_cache.response_times_cache, OrderedDict)

    def test_distributed_worker_report_with_cache(self):
        """Test cache usage in distributed worker reports"""
        # Create worker stats (simulating worker nodes)
        worker_stats = RequestStats(use_response_times_cache=True)
        worker_entry = StatsEntry(worker_stats, "/api/data", "POST", use_response_times_cache=True)

        # Log test data on worker
        for i in range(10):
            response_time = 100 + i * 10
            worker_entry.log(response_time, 1000 + i * 100)

        worker_data = worker_entry.serialize()

        # Simulate master unserialize with cache enabled
        master_entry = StatsEntry.unserialize(
            worker_data,
            use_response_times_cache=True,  # 关键：确保传递了True
        )

        # Verify data consistency
        self.assertEqual(worker_entry.num_requests, master_entry.num_requests)
        self.assertEqual(worker_entry.total_response_time, master_entry.total_response_time)
        self.assertEqual(worker_entry.avg_response_time, master_entry.avg_response_time)

        # Verify cache initialization
        self.assertTrue(master_entry.use_response_times_cache)
        self.assertIsNotNone(master_entry.response_times_cache)

        # Verify master can log new data
        master_entry.log(500, 5000)
        self.assertEqual(master_entry.num_requests, 11)
        self.assertEqual(master_entry.max_response_time, 500)

    def test_on_worker_report_uses_cache_parameter(self):
        """Test on_worker_report uses cache param in setup_distributed_stats_event_listeners"""
        from locust.event import Events
        from locust.stats import setup_distributed_stats_event_listeners

        # Create events and master stats
        events = Events()
        master_stats = RequestStats(use_response_times_cache=True)
        setup_distributed_stats_event_listeners(events, master_stats)

        # Simulate worker stats data
        worker_stats_data = {
            "stats": [
                {
                    "name": "/test/endpoint",
                    "method": "GET",
                    "num_requests": 5,
                    "num_failures": 0,
                    "total_response_time": 1500,
                    "min_response_time": 100,
                    "max_response_time": 500,
                    "total_content_length": 5000,
                    "response_times": {100: 2, 200: 1, 300: 1, 500: 1},
                    "num_reqs_per_sec": {123456: 5},
                    "num_fail_per_sec": {},
                    "last_request_timestamp": 123456.789,
                    "start_time": 123450.0,
                }
            ],
            "stats_total": {
                "name": "Aggregated",
                "method": "",
                "num_requests": 5,
                "num_failures": 0,
                "total_response_time": 1500,
                "min_response_time": 100,
                "max_response_time": 500,
                "total_content_length": 5000,
                "response_times": {100: 2, 200: 1, 300: 1, 500: 1},
                "num_reqs_per_sec": {123456: 5},
                "num_fail_per_sec": {},
                "last_request_timestamp": 123456.789,
                "start_time": 123450.0,
            },
            "errors": {},
        }

        # Trigger worker_report event
        events.worker_report.fire(client_id="worker1", data=worker_stats_data)

        # Verify entry creation and cache status
        entry = master_stats.get("/test/endpoint", "GET")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.num_requests, 5)

        # Verify entry uses cache
        self.assertTrue(entry.use_response_times_cache)

    def test_cross_server_response_time_consistency(self):
        """Test cross-server response time data consistency"""
        # Simulate two different environments (different servers)
        stats_server_a = RequestStats(use_response_times_cache=True)

        # Log data on server A (worker)
        entry_a = StatsEntry(stats_server_a, "/api/resource", "PUT", use_response_times_cache=True)

        response_times = [150, 225, 300, 375, 450, 525, 600]
        for rt in response_times:
            entry_a.log(rt, 2000)
            gevent.sleep(0.001)

        # Verify percentile consistency
        median_a = entry_a.median_response_time
        percentile_95_a = entry_a.get_response_time_percentile(0.95)
        serialized = entry_a.serialize()

        # Deserialize on server B (master) with cache enabled
        entry_b = StatsEntry.unserialize(serialized, use_response_times_cache=True)

        # Calculate percentiles
        median_b = entry_b.median_response_time
        percentile_95_b = entry_b.get_response_time_percentile(0.95)

        # Verify consistency
        self.assertEqual(median_a, median_b)
        self.assertEqual(percentile_95_a, percentile_95_b)

        # Verify master can log new data
        entry_b.log(750, 3000)
        self.assertEqual(entry_b.num_requests, 8)
        self.assertEqual(entry_b.max_response_time, 750)

    def test_response_times_cache_after_unserialize(self):
        """Test response time cache behavior after unserialization"""
        # Create entry with cache and log data
        entry = StatsEntry(self.stats, "/test", "GET", use_response_times_cache=True)
        current_time = int(time.time())
        entry.log(100, 1000)
        entry.last_request_timestamp = current_time + 0.5
        entry.log(200, 2000)

        # Cache response times and serialize
        entry._cache_response_times(current_time)
        serialized = entry.serialize()

        # Deserialize (using cache)
        new_entry = StatsEntry.unserialize(serialized, use_response_times_cache=True)

        # Verify cache-related attributes
        self.assertTrue(new_entry.use_response_times_cache)
        self.assertIsInstance(new_entry.response_times_cache, OrderedDict)

    def test_stats_entry_method_none_handling(self):
        """Test StatsEntry handling when method parameter is None"""
        # Create entry with None method
        entry = StatsEntry(self.stats, "/test", None, use_response_times_cache=True)
        entry.log(150, 1500)

        # Serialize and unserialize
        serialized = entry.serialize()
        new_entry = StatsEntry.unserialize(serialized, use_response_times_cache=True)

        # Verify data and cache
        self.assertIsNone(new_entry.method)
        self.assertEqual(new_entry.name, "/test")
        self.assertEqual(new_entry.num_requests, 1)
        self.assertEqual(new_entry.avg_response_time, 150.0)
        self.assertEqual(new_entry.total_response_time, 150)


class TestStatsEntry(unittest.TestCase):
    def parse_string_output(self, text):
        tokenlist = re.split(r"[\s\(\)%|]+", text.strip())
        tokens = {
            "method": tokenlist[0],
            "name": tokenlist[1],
            "request_count": int(tokenlist[2]),
            "failure_count": int(tokenlist[3]),
            "failure_percentage": float(tokenlist[4]),
        }
        return tokens

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.stats = RequestStats()

    def test_fail_ratio_with_no_failures(self):
        REQUEST_COUNT = 10
        FAILURE_COUNT = 0
        EXPECTED_FAIL_RATIO = 0.0

        s = StatsEntry(self.stats, "/", "GET")
        s.num_requests = REQUEST_COUNT
        s.num_failures = FAILURE_COUNT

        self.assertAlmostEqual(s.fail_ratio, EXPECTED_FAIL_RATIO)
        output_fields = self.parse_string_output(str(s))
        self.assertEqual(output_fields["request_count"], REQUEST_COUNT)
        self.assertEqual(output_fields["failure_count"], FAILURE_COUNT)
        self.assertAlmostEqual(output_fields["failure_percentage"], EXPECTED_FAIL_RATIO * 100)

    def test_fail_ratio_with_all_failures(self):
        REQUEST_COUNT = 10
        FAILURE_COUNT = 10
        EXPECTED_FAIL_RATIO = 1.0

        s = StatsEntry(self.stats, "/", "GET")
        s.num_requests = REQUEST_COUNT
        s.num_failures = FAILURE_COUNT

        self.assertAlmostEqual(s.fail_ratio, EXPECTED_FAIL_RATIO)
        output_fields = self.parse_string_output(str(s))
        self.assertEqual(output_fields["request_count"], REQUEST_COUNT)
        self.assertEqual(output_fields["failure_count"], FAILURE_COUNT)
        self.assertAlmostEqual(output_fields["failure_percentage"], EXPECTED_FAIL_RATIO * 100)

    def test_fail_ratio_with_half_failures(self):
        REQUEST_COUNT = 10
        FAILURE_COUNT = 5
        EXPECTED_FAIL_RATIO = 0.5

        s = StatsEntry(self.stats, "/", "GET")
        s.num_requests = REQUEST_COUNT
        s.num_failures = FAILURE_COUNT

        self.assertAlmostEqual(s.fail_ratio, EXPECTED_FAIL_RATIO)
        output_fields = self.parse_string_output(str(s))
        self.assertEqual(output_fields["request_count"], REQUEST_COUNT)
        self.assertEqual(output_fields["failure_count"], FAILURE_COUNT)
        self.assertAlmostEqual(output_fields["failure_percentage"], EXPECTED_FAIL_RATIO * 100)


class TestRequestStatsWithWebserver(WebserverTestCase):
    def setUp(self):
        super().setUp()

        class MyUser(HttpUser):
            host = "http://127.0.0.1:%i" % self.port

        self.locust = MyUser(self.environment)

    def test_request_stats_content_length(self):
        self.locust.client.get("/ultra_fast")
        self.assertEqual(
            self.runner.stats.entries[("/ultra_fast", "GET")].avg_content_length, len("This is an ultra fast response")
        )
        self.locust.client.get("/ultra_fast")
        # test legacy stats.get() function sometimes too
        self.assertEqual(
            self.runner.stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response")
        )

    def test_request_stats_no_content_length(self):
        path = "/no_content_length"
        self.locust.client.get(path)
        self.assertEqual(
            self.runner.stats.entries[(path, "GET")].avg_content_length,
            len("This response does not have content-length in the header"),
        )

    def test_request_stats_no_content_length_streaming(self):
        path = "/no_content_length"
        self.locust.client.get(path, stream=True)
        self.assertEqual(0, self.runner.stats.entries[(path, "GET")].avg_content_length)

    def test_request_stats_named_endpoint(self):
        self.locust.client.get("/ultra_fast", name="my_custom_name")
        self.assertEqual(1, self.runner.stats.entries[("my_custom_name", "GET")].num_requests)

    def test_request_stats_named_endpoint_request_name(self):
        self.locust.client.request_name = "my_custom_name_1"
        self.locust.client.get("/ultra_fast")
        self.assertEqual(1, self.runner.stats.entries[("my_custom_name_1", "GET")].num_requests)
        self.locust.client.request_name = None

    def test_request_stats_named_endpoint_rename_request(self):
        with self.locust.client.rename_request("my_custom_name_3"):
            self.locust.client.get("/ultra_fast")
        self.assertEqual(1, self.runner.stats.entries[("my_custom_name_3", "GET")].num_requests)

    def test_request_stats_query_variables(self):
        self.locust.client.get("/ultra_fast?query=1")
        self.assertEqual(1, self.runner.stats.entries[("/ultra_fast?query=1", "GET")].num_requests)

    def test_request_stats_put(self):
        self.locust.client.put("/put")
        self.assertEqual(1, self.runner.stats.entries[("/put", "PUT")].num_requests)

    def test_request_connection_error(self):
        class MyUser(HttpUser):
            host = "http://localhost:1"

        locust = MyUser(self.environment)
        response = locust.client.get("/", timeout=0.1)
        self.assertEqual(response.status_code, 0)
        self.assertEqual(1, self.runner.stats.entries[("/", "GET")].num_failures)
        self.assertEqual(1, self.runner.stats.entries[("/", "GET")].num_requests)


class MyTaskSet(TaskSet):
    @task(75)
    def root_task(self):
        pass

    @task(25)
    class MySubTaskSet(TaskSet):
        @task
        def task1(self):
            pass

        @task
        def task2(self):
            pass


class TestInspectUser(unittest.TestCase):
    def test_get_task_ratio_relative(self):
        ratio = _get_task_ratio([MyTaskSet], False, 1.0)
        self.assertEqual(1.0, ratio["MyTaskSet"]["ratio"])
        self.assertEqual(0.75, ratio["MyTaskSet"]["tasks"]["root_task"]["ratio"])
        self.assertEqual(0.25, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["ratio"])
        self.assertEqual(0.5, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task1"]["ratio"])
        self.assertEqual(0.5, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task2"]["ratio"])

    def test_get_task_ratio_total(self):
        ratio = _get_task_ratio([MyTaskSet], True, 1.0)
        self.assertEqual(1.0, ratio["MyTaskSet"]["ratio"])
        self.assertEqual(0.75, ratio["MyTaskSet"]["tasks"]["root_task"]["ratio"])
        self.assertEqual(0.25, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["ratio"])
        self.assertEqual(0.125, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task1"]["ratio"])
        self.assertEqual(0.125, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task2"]["ratio"])


class TestDistributedResponseTimeFix(unittest.TestCase):
    """Test suite for distributed response time fix"""

    def setUp(self):
        self.stats = RequestStats(use_response_times_cache=True)

    def test_master_worker_response_time_sync(self):
        """Test response time sync between master and worker nodes"""
        from locust.event import Events
        from locust.stats import setup_distributed_stats_event_listeners

        # Simulate worker stats and log data
        worker_stats = RequestStats(use_response_times_cache=True)
        worker_entry = worker_stats.get("/test", "GET")

        for i in range(20):
            worker_entry.log(50 + i * 25, 1000)

        # Serialize worker data
        worker_data = {
            "stats": worker_stats.serialize_stats(),
            "stats_total": worker_stats.total.serialize(),
            "errors": {},
        }

        # Simulate master receiving data
        master_stats = RequestStats(use_response_times_cache=True)
        events = Events()
        setup_distributed_stats_event_listeners(events, master_stats)

        # Trigger event
        events.worker_report.fire(client_id="test-worker", data=worker_data)

        # Verify master's stats
        master_entry = master_stats.get("/test", "GET")
        self.assertIsNotNone(master_entry)
        self.assertEqual(master_entry.num_requests, 20)

        # Verify cache is enabled
        self.assertTrue(master_entry.use_response_times_cache)

    def test_response_time_cache_in_distributed_mode(self):
        """Test response time cache consistency in distributed mode"""
        stats1 = RequestStats(use_response_times_cache=True)
        stats2 = RequestStats(use_response_times_cache=True)
        entry1 = StatsEntry(stats1, "/api", "GET", use_response_times_cache=True)
        entry2 = StatsEntry(stats2, "/api", "GET", use_response_times_cache=True)

        # Log different response times
        for i in range(10):
            entry1.log(100 + i * 20, 1000)

        for i in range(10, 20):
            entry2.log(100 + i * 20, 1000)

        # Simulate merge (master merge worker data)
        serialized2 = entry2.serialize()
        entry2_deserialized = StatsEntry.unserialize(serialized2, use_response_times_cache=True)
        entry1.extend(entry2_deserialized)

        # Verify merged stats and cache
        self.assertEqual(entry1.num_requests, 20)

        # Verify cache state
        self.assertTrue(entry1.use_response_times_cache)

    def test_serialization_with_cache_param_true(self):
        """Test serialization/unserialization with use_response_times_cache=True"""
        stats = RequestStats(use_response_times_cache=True)
        entry = StatsEntry(stats, "/api/test", "GET", use_response_times_cache=True)
        for i in range(5):
            entry.log(100 + i * 50, 1000 + i * 200)

        # 序列Serialize and unserialize化
        serialized = entry.serialize()

        # Verify data and cache
        deserialized = StatsEntry.unserialize(serialized, use_response_times_cache=True)

        self.assertEqual(entry.method, deserialized.method)
        self.assertEqual(entry.name, deserialized.name)
        self.assertEqual(entry.num_requests, deserialized.num_requests)
        self.assertEqual(entry.total_response_time, deserialized.total_response_time)

        self.assertTrue(deserialized.use_response_times_cache)
        self.assertIsNotNone(deserialized.response_times_cache)
        self.assertIsInstance(deserialized.response_times_cache, OrderedDict)

    def test_serialization_with_cache_param_false(self):
        """Test serialization/unserialization with use_response_times_cache=False"""
        stats = RequestStats(use_response_times_cache=True)
        entry = StatsEntry(stats, "/api/test", "GET", use_response_times_cache=True)
        for i in range(5):
            entry.log(100 + i * 50, 1000 + i * 200)

        # Serialize and unserialize without cache
        serialized = entry.serialize()

        # Verify data and cache
        deserialized = StatsEntry.unserialize(serialized, use_response_times_cache=False)

        self.assertEqual(entry.method, deserialized.method)
        self.assertEqual(entry.name, deserialized.name)
        self.assertEqual(entry.num_requests, deserialized.num_requests)
        self.assertEqual(entry.total_response_time, deserialized.total_response_time)

        self.assertFalse(deserialized.use_response_times_cache)
        self.assertIsNone(deserialized.response_times_cache)

    def test_distributed_response_time_percentile_issue_and_fix(self):
        """Demonstrate and fix percentile calculation issue in distributed mode"""
        response_times = [100, 150, 200, 250, 300, 350, 400, 450, 500, 550]

        # Demonstrate issue: no cache leads to percentile calculation failure
        worker_stats_no_cache = RequestStats(use_response_times_cache=False)
        worker_entry_no_cache = StatsEntry(
            worker_stats_no_cache, "/api/endpoint", "GET", use_response_times_cache=False
        )

        for rt in response_times:
            worker_entry_no_cache.log(rt, 1000)
        serialized_data = worker_entry_no_cache.serialize()

        master_entry_broken = StatsEntry.unserialize(serialized_data, use_response_times_cache=False)
        with self.assertRaises(ValueError) as context:
            master_entry_broken.get_current_response_time_percentile(0.95)
        self.assertIn(
            "use_response_times_cache must be set to True",
            str(context.exception),
            "Problem demonstration: Calling get_current_response_time_percentile when there is no cache should throw an exception.",
        )

        # Demonstrate fix: cache enabled for correct percentile calculation
        worker_stats_with_cache = RequestStats(use_response_times_cache=True)
        worker_entry_with_cache = StatsEntry(
            worker_stats_with_cache, "/api/endpoint", "GET", use_response_times_cache=True
        )

        for rt in response_times:
            worker_entry_with_cache.log(rt, 1000)

        serialized_data_fixed = worker_entry_with_cache.serialize()
        master_entry_fixed = StatsEntry.unserialize(serialized_data_fixed, use_response_times_cache=True)

        # Verify cache initialization and data consistency
        self.assertIsNotNone(
            master_entry_fixed.response_times_cache,
            "Repair verification: The response time cache was correctly initialized during Master deserialization.",
        )
        self.assertIsInstance(
            master_entry_fixed.response_times_cache,
            OrderedDict,
            "Repair verification: The response time cache should be an OrderedDict type",
        )
        self.assertTrue(
            master_entry_fixed.use_response_times_cache,
            "Repair verification: Master's entry should have response times cache enabled",
        )
        self.assertEqual(
            worker_entry_with_cache.num_requests,
            master_entry_fixed.num_requests,
            "Cross-server verification: The number of requests to Worker and Master should be the same.",
        )
        self.assertEqual(
            worker_entry_with_cache.total_response_time,
            master_entry_fixed.total_response_time,
            "Cross-server verification: The total response time to Worker and Master should be the same.",
        )
        self.assertEqual(
            worker_entry_with_cache.avg_response_time,
            master_entry_fixed.avg_response_time,
            "Cross-server verification: Worker and Master should have the same average response time",
        )

        # Verify master can log new data
        master_entry_fixed.log(600, 1000)
        self.assertEqual(
            master_entry_fixed.num_requests,
            11,
            "Master should be able to continue recording new response times.",
        )
        self.assertEqual(
            master_entry_fixed.max_response_time,
            600,
            "Master should correctly update the maximum response time",
        )
