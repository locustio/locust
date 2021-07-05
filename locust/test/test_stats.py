import csv
import time
import unittest
import re
import os
import json

import gevent
import mock
import locust
from locust import HttpUser, TaskSet, task, User, constant
from locust.env import Environment
from locust.rpc.protocol import Message
from locust.stats import CachedResponseTimes, RequestStats, StatsEntry, diff_response_time_dicts, PERCENTILES_TO_REPORT
from locust.stats import StatsCSVFileWriter
from locust.stats import stats_history
from locust.test.testcases import LocustTestCase
from locust.user.inspectuser import get_task_ratio_dict

from .testcases import WebserverTestCase
from .test_runners import mocked_rpc


_TEST_CSV_STATS_INTERVAL_SEC = 0.2
_TEST_CSV_STATS_INTERVAL_WAIT_SEC = _TEST_CSV_STATS_INTERVAL_SEC + 0.1


def _write_csv_files(environment, stats_base_name, full_history=False):
    """Spawn CVS writer and exit loop after first iteration."""
    stats_writer = StatsCSVFileWriter(environment, PERCENTILES_TO_REPORT, stats_base_name, full_history=full_history)
    greenlet = gevent.spawn(stats_writer)
    gevent.sleep(_TEST_CSV_STATS_INTERVAL_WAIT_SEC)
    gevent.kill(greenlet)
    stats_writer.close_files()


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
        self.s = self.stats.get("test_entry", "GET")

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
        s2 = self.stats.get("other_endpoint", "GET")
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

        self.stats.log_error("GET", "/", Exception("Error caused by %r" % Dummy()))
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
    def test_print_percentile_stats(self):
        stats = RequestStats()
        for i in range(100):
            stats.log_request("GET", "test_entry", i, 2000 + i)
        locust.stats.print_percentile_stats(stats)
        info = self.mocked_log.info
        self.assertEqual(7, len(info))
        # check that headline contains same number of column as the value rows
        headlines = info[1].replace("# reqs", "#reqs").split()
        self.assertEqual(len(headlines), len(info[3].split()))
        self.assertEqual(len(headlines), len(info[5].split()))


class TestCsvStats(LocustTestCase):
    STATS_BASE_NAME = "test"
    STATS_FILENAME = "{}_stats.csv".format(STATS_BASE_NAME)
    STATS_HISTORY_FILENAME = "{}_stats_history.csv".format(STATS_BASE_NAME)
    STATS_FAILURES_FILENAME = "{}_failures.csv".format(STATS_BASE_NAME)
    STATS_EXCEPTIONS_FILENAME = "{}_exceptions.csv".format(STATS_BASE_NAME)

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
        self.runner.stats.log_request("GET", "/", 10, content_length=666)
        greenlet = gevent.spawn(stats_writer)
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

        self.assertEqual(4, len(rows))
        self.assertEqual("/", rows[0]["Name"])
        self.assertEqual("Aggregated", rows[1]["Name"])
        self.assertEqual("/", rows[2]["Name"])
        self.assertEqual("Aggregated", rows[3]["Name"])

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

            server.mocked_send(Message("client_ready", None, "fake_client"))

            master.stats.get("/", "GET").log(100, 23455)
            master.stats.get("/", "GET").log(800, 23455)
            master.stats.get("/", "GET").log(700, 23455)

            data = {"user_count": 1}
            environment.events.report_to_master.fire(client_id="fake_client", data=data)
            master.stats.clear_all()

            server.mocked_send(Message("stats", data, "fake_client"))
            s = master.stats.get("/", "GET")
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
            server.mocked_send(Message("client_ready", None, "fake_client"))

            request_name_dict = {
                "scenario": "get cashes",
                "path": "/cash/[amount]",
                "arguments": [{"size": 1}],
            }
            request_name_str = json.dumps(request_name_dict)

            master.stats.get(request_name_str, "GET").log(100, 23455)
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
        env2 = Environment(events=locust.events, catch_exceptions=False)
        runner2 = env2.create_worker_runner("127.0.0.1", 5558)
        greenlet1 = gevent.spawn(stats_history, runner1)
        greenlet2 = gevent.spawn(stats_history, runner2)
        gevent.sleep(1)
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
            self.runner.stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response")
        )
        self.locust.client.get("/ultra_fast")
        self.assertEqual(
            self.runner.stats.get("/ultra_fast", "GET").avg_content_length, len("This is an ultra fast response")
        )

    def test_request_stats_no_content_length(self):
        path = "/no_content_length"
        self.locust.client.get(path)
        self.assertEqual(
            self.runner.stats.get(path, "GET").avg_content_length,
            len("This response does not have content-length in the header"),
        )

    def test_request_stats_no_content_length_streaming(self):
        path = "/no_content_length"
        self.locust.client.get(path, stream=True)
        self.assertEqual(0, self.runner.stats.get(path, "GET").avg_content_length)

    def test_request_stats_named_endpoint(self):
        self.locust.client.get("/ultra_fast", name="my_custom_name")
        self.assertEqual(1, self.runner.stats.get("my_custom_name", "GET").num_requests)

    def test_request_stats_query_variables(self):
        self.locust.client.get("/ultra_fast?query=1")
        self.assertEqual(1, self.runner.stats.get("/ultra_fast?query=1", "GET").num_requests)

    def test_request_stats_put(self):
        self.locust.client.put("/put")
        self.assertEqual(1, self.runner.stats.get("/put", "PUT").num_requests)

    def test_request_connection_error(self):
        class MyUser(HttpUser):
            host = "http://localhost:1"

        locust = MyUser(self.environment)
        response = locust.client.get("/", timeout=0.1)
        self.assertEqual(response.status_code, 0)
        self.assertEqual(1, self.runner.stats.get("/", "GET").num_failures)
        self.assertEqual(1, self.runner.stats.get("/", "GET").num_requests)


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
    def test_get_task_ratio_dict_relative(self):
        ratio = get_task_ratio_dict([MyTaskSet])
        self.assertEqual(1.0, ratio["MyTaskSet"]["ratio"])
        self.assertEqual(0.75, ratio["MyTaskSet"]["tasks"]["root_task"]["ratio"])
        self.assertEqual(0.25, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["ratio"])
        self.assertEqual(0.5, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task1"]["ratio"])
        self.assertEqual(0.5, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task2"]["ratio"])

    def test_get_task_ratio_dict_total(self):
        ratio = get_task_ratio_dict([MyTaskSet], total=True)
        self.assertEqual(1.0, ratio["MyTaskSet"]["ratio"])
        self.assertEqual(0.75, ratio["MyTaskSet"]["tasks"]["root_task"]["ratio"])
        self.assertEqual(0.25, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["ratio"])
        self.assertEqual(0.125, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task1"]["ratio"])
        self.assertEqual(0.125, ratio["MyTaskSet"]["tasks"]["MySubTaskSet"]["tasks"]["task2"]["ratio"])
