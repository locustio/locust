from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
import sys
import tempfile
import textwrap
import unittest
from tempfile import TemporaryDirectory
from unittest import TestCase

import gevent
import psutil
import requests
from pyquery import PyQuery as pq

from .mock_locustfile import MOCK_LOCUSTFILE_CONTENT, mock_locustfile
from .subprocess_utils import TestProcess
from .util import IS_WINDOWS, get_free_tcp_port, patch_env, temporary_file, wait_for_server

SHORT_SLEEP = 2 if sys.platform == "darwin" else 1  # macOS is slow on GH, give it some extra time


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


MOCK_LOCUSTFILE_CONTENT_A = textwrap.dedent(
    """
    from locust import User, task, constant, events
    class TestUser1(User):
        wait_time = constant(1)
        @task
        def my_task(self):
            print("running my_task()")
"""
)
MOCK_LOCUSTFILE_CONTENT_B = textwrap.dedent(
    """
    from locust import User, task, constant, events
    class TestUser2(User):
        wait_time = constant(1)
        @task
        def my_task(self):
            print("running my_task()")
"""
)


class ProcessIntegrationTest(TestCase):
    def setUp(self):
        super().setUp()
        self.timeout = gevent.Timeout(10)
        self.timeout.start()

    def tearDown(self):
        self.timeout.cancel()
        super().tearDown()


class StandaloneIntegrationTests(ProcessIntegrationTest):
    def test_help_arg(self):
        output = subprocess.check_output(
            ["locust", "--help"],
            stderr=subprocess.STDOUT,
            timeout=5,
            text=True,
        ).strip()
        self.assertTrue(output.startswith("Usage: locust [options] [UserClass"))
        self.assertIn("Common options:", output)
        self.assertIn("--locustfile <filename>", output)
        self.assertIn("Logging options:", output)
        self.assertIn("--skip-log-setup      Disable Locust's logging setup.", output)

    @unittest.skipIf(IS_WINDOWS, reason="Signal handling on windows is hard")
    def test_custom_arguments(self):
        port = get_free_tcp_port()
        with temporary_file(
            content=textwrap.dedent(
                """
            from locust import User, task, constant, events
            @events.init_command_line_parser.add_listener
            def _(parser, **kw):
                parser.add_argument("--custom-string-arg")

            class TestUser(User):
                wait_time = constant(10)
                @task
                def my_task(self):
                    print(self.environment.parsed_options.custom_string_arg)
        """
            )
        ) as file_path:
            # print(subprocess.check_output(["cat", file_path]))
            with TestProcess(
                f"locust -f {file_path} --custom-string-arg command_line_value --web-port {port}",
            ) as tp:
                tp.expect("Starting Locust")
                wait_for_server(f"http://127.0.0.1:{port}/swarm")
                requests.post(
                    f"http://127.0.0.1:{port}/swarm",
                    data={
                        "user_count": 1,
                        "spawn_rate": 1,
                        "host": "https://localhost",
                        "custom_string_arg": "web_form_value",
                    },
                )
                tp.expect('All users spawned: {"TestUser": 1} (1 total users)')
                tp.expect("web_form_value", stream="stdout")
                tp.terminate()
                tp.expect("Shutting down")
                tp.expect("Aggregated")
                tp.not_expect_any("command_line_value")

    @unittest.skipIf(IS_WINDOWS, reason="Signal handling on windows is hard")
    def test_custom_arguments_in_file(self):
        with temporary_file(
            content=textwrap.dedent(
                """
            from locust import User, task, constant, events
            @events.init_command_line_parser.add_listener
            def _(parser, **kw):
                parser.add_argument("--custom-string-arg")

            class TestUser(User):
                wait_time = constant(10)
                @task
                def my_task(self):
                    print(self.environment.parsed_options.custom_string_arg)
        """
            )
        ) as file_path:
            try:
                with open("locust.conf", "w") as conf_file:
                    conf_file.write("custom-string-arg config_file_value")

                with TestProcess(f"locust -f {file_path} --autostart") as tp:
                    tp.expect("Starting Locust")
                    tp.expect("config_file_value", stream="stdout")
                    tp.terminate()
                    tp.expect("Shutting down")
                    tp.not_expect_any("Traceback")
            finally:
                os.remove("locust.conf")

    @unittest.skipIf(IS_WINDOWS, reason="Signal handling on windows is hard")
    def test_custom_exit_code(self):
        with temporary_file(
            content=textwrap.dedent(
                """
            from locust import User, task, constant, events
            @events.quitting.add_listener
            def _(environment, **kw):
                environment.process_exit_code = 42
            @events.quit.add_listener
            def _(exit_code, **kw):
                print(f"Exit code in quit event {exit_code}")
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """
            )
        ) as file_path:
            with TestProcess(f"locust -f {file_path} --headless", expect_return_code=42) as tp:
                tp.expect("Starting Locust")
                # if terminate happens too soon it might happen to be ignored, so wait for the first report:
                tp.expect("Ramping to 1 users at a rate of 1.00 per second")
                tp.expect("Aggregated")
                tp.terminate()
                tp.expect("Shutting down (exit code 42)")
                tp.expect("Exit code in quit event 42", stream="stdout")

    def test_webserver(self):
        with temporary_file(
            content=textwrap.dedent(
                """
            from locust import User, task, constant, events
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """
            )
        ) as file_path:
            with TestProcess(f"locust -f {file_path}") as tp:
                tp.expect("Starting Locust")
                tp.expect("Starting web interface at")
                # Ensure we do not trigger SIGINT when instantiating webui as it can result
                # in `create_web_ui` traceback
                gevent.sleep(0.1)

    def test_percentile_parameter(self):
        port = get_free_tcp_port()
        with temporary_file(
            content=textwrap.dedent(
                """
            from locust import User, task, constant, events
            from locust import stats
            stats.PERCENTILES_TO_CHART = [0.9, 0.4]
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """
            )
        ) as file_path:
            with TestProcess(f"locust -f {file_path} --web-port {port} --autostart") as tp:
                tp.expect("Starting web interface at")

                wait_for_server(f"http://localhost:{port}/")
                response = requests.get(f"http://localhost:{port}/")
                self.assertEqual(200, response.status_code)

    def test_percentiles_to_statistics(self):
        port = get_free_tcp_port()
        with temporary_file(
            content=textwrap.dedent(
                """
                from locust import User, task, constant, events
                from locust.stats import PERCENTILES_TO_STATISTICS
                PERCENTILES_TO_STATISTICS = [0.9, 0.99]
                class TestUser(User):
                    wait_time = constant(3)
                    @task
                    def my_task(self):
                        print("running my_task()")
            """
            )
        ) as file_path:
            with TestProcess(f"locust -f {file_path} --web-port {port} --autostart") as tp:
                tp.expect("Starting web interface at")

                wait_for_server(f"http://localhost:{port}/")
                response = requests.get(f"http://localhost:{port}/")
                self.assertEqual(200, response.status_code)

    def test_invalid_percentile_parameter(self):
        with temporary_file(
            content=textwrap.dedent(
                """
            from locust import User, task, constant, events
            from locust import stats
            stats.PERCENTILES_TO_CHART  = [1.2]
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """
            )
        ) as file_path:
            with TestProcess(f"locust -f {file_path} --headless", sigint_on_exit=False, expect_return_code=1) as tp:
                tp.expect("parameter need to be float and value between. 0 < percentile < 1 Eg 0.95")

    def test_csv_full_history_requires_csv(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --csv-full-history", sigint_on_exit=False, expect_return_code=2
            ) as tp:
                tp.expect("locust: error: '--csv-full-history' requires '--csv'.")

    def test_webserver_multiple_locustfiles(self):
        with mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_A) as mocked1:
            with mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_B) as mocked2:
                with TestProcess(f"locust -f {mocked1.file_path},{mocked2.file_path}") as tp:
                    tp.expect("Starting Locust")
                    tp.expect("Starting web interface at")
                    gevent.sleep(0.1)

    def test_webserver_multiple_locustfiles_in_directory(self):
        with TemporaryDirectory() as temp_dir:
            with mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_A, dir=temp_dir):
                with mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_B, dir=temp_dir):
                    with TestProcess(f"locust -f {temp_dir}") as tp:
                        tp.expect("Starting Locust")
                        tp.expect("Starting web interface at")
                        gevent.sleep(0.1)

    def test_webserver_multiple_locustfiles_with_shape(self):
        content = textwrap.dedent(
            """
            from locust import User, task, between
            class TestUser2(User):
                wait_time = between(2, 4)
                @task
                def my_task(self):
                    print("running my_task() again")
            """
        )
        with mock_locustfile(content=content) as mocked1:
            with temporary_file(
                content=textwrap.dedent(
                    """
                from locust import User, task, between, LoadTestShape
                class LoadTestShape(LoadTestShape):
                    def tick(self):
                        run_time = self.get_run_time()
                        if run_time < 2:
                            return (10, 1)

                        return None

                class TestUser(User):
                    wait_time = between(2, 4)
                    @task
                    def my_task(self):
                        print("running my_task()")
            """
                )
            ) as mocked2:
                with TestProcess(f"locust -f {mocked1.file_path},{mocked2} -L DEBUG") as tp:
                    tp.expect("Starting Locust")
                    tp.expect("Starting web interface at")
                    gevent.sleep(0.1)
                    tp.terminate()
                    if not IS_WINDOWS:
                        tp.expect("Shutting down")
                    # This test is the reason we need the -L DEBUG option
                    tp.not_expect_any("Locust is running with the UserClass Picker Enabled")

    def test_default_headless_spawn_options(self):
        with mock_locustfile() as mocked:
            # just to test --stop-timeout argument parsing, doesnt actually validate its function:
            with TestProcess(
                f"locust -f {mocked.file_path} --host https://test.com --run-time 1s --headless --loglevel DEBUG --exit-code-on-error 0 --stop-timeout 0s",
            ) as tp:
                tp.expect('Spawning additional {"UserSubclass": 1} ({"UserSubclass": 0} already running)...')
                tp.not_expect_any("Traceback")

    def test_invalid_stop_timeout_string(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --host https://test.com --stop-timeout asdf1",
                expect_return_code=2,
                sigint_on_exit=False,
            ) as tp:
                tp.expect(
                    "locust: error: argument -s/--stop-timeout: Invalid time span format. Valid formats: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc."
                )

    @unittest.skipIf(IS_WINDOWS, reason="Signal handling on windows is hard")
    def test_headless_spawn_options_wo_run_time(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --host https://test.com --headless --exit-code-on-error 0"
            ) as tp:
                tp.expect("Starting Locust")
                tp.expect("No run time limit set, use CTRL+C to interrupt")
                tp.expect("All users spawned")
                tp.terminate()
                tp.expect("Shutting down (exit code 0)")

    @unittest.skipIf(IS_WINDOWS, reason="Signal handling on windows is hard")
    def test_run_headless_with_multiple_locustfiles(self):
        with TemporaryDirectory() as temp_dir:
            with mock_locustfile(dir=temp_dir):
                with temporary_file(
                    content=textwrap.dedent(
                        """
                    from locust import User, task, constant, events
                    class TestUser(User):
                        wait_time = constant(1)
                        @task
                        def my_task(self):
                            print("running my_task()")
                """
                    ),
                    dir=temp_dir,
                ):
                    with TestProcess(f"locust -f {temp_dir} --headless -u 2 --exit-code-on-error 0") as tp:
                        tp.expect("Starting Locust")
                        tp.expect('All users spawned: {"TestUser": 1, "UserSubclass": 1} (2 total users)')
                        # if terminate happens too soon it might happen to be ignored, so wait for the first report:
                        tp.expect("failures/s")
                        tp.terminate()
                        tp.expect("Shutting down (exit code 0)")

    def test_default_headless_spawn_options_with_shape(self):
        content = MOCK_LOCUSTFILE_CONTENT + textwrap.dedent(
            """
            class LoadTestShape(LoadTestShape):
                def tick(self):
                    run_time = self.get_run_time()
                    if run_time < 0.1:
                        return (10, 1)

                    return None
            """
        )
        with mock_locustfile(content=content) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --host https://test.com/ --headless --exit-code-on-error 0",
                sigint_on_exit=False,
            ) as tp:
                tp.expect("Shape test updating to 10 users at 1.00 spawn rate")
                # ensure stats printer printed at least one report before shutting down and that there was a final report printed as well
                tp.expect_any("Aggregated")
                tp.expect("Shutting down (exit code 0)")
                tp.expect("Aggregated")

    def test_run_headless_with_multiple_locustfiles_with_shape(self):
        content = textwrap.dedent(
            """
            from locust import User, task, between
            class TestUser2(User):
                wait_time = between(2, 4)
                @task
                def my_task(self):
                    print("running my_task() again")
            """
        )
        with mock_locustfile(content=content) as mocked1:
            with temporary_file(
                content=textwrap.dedent(
                    """
                from locust import User, task, between, LoadTestShape
                class LoadTestShape(LoadTestShape):
                    def tick(self):
                        run_time = self.get_run_time()
                        if run_time < 0.1:
                            return (10, 1)

                        return None

                class TestUser(User):
                    wait_time = between(2, 4)
                    @task
                    def my_task(self):
                        print("running my_task()")
            """
                )
            ) as mocked2:
                with TestProcess(
                    f"locust -f {mocked1.file_path},{mocked2} --host https://test.com --headless --exit-code-on-error 0",
                    sigint_on_exit=False,
                ) as tp:
                    tp.expect("Shape test updating to 10 users at 1.00 spawn rate")
                    # ensure stats printer printed at least one report before shutting down and that there was a final report printed as well
                    tp.expect_any("Aggregated")
                    tp.expect("Shutting down (exit code 0)")
                    tp.expect("Aggregated")

    @unittest.skipIf(IS_WINDOWS, reason="Signal handling on windows is hard")
    @unittest.skipIf(sys.platform == "darwin", reason="Disable on macOS for now because it has issues on GH")
    def test_autostart_wo_run_time(self):
        port = get_free_tcp_port()
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --web-port {port} --autostart", expect_return_code=None
            ) as tp:
                tp.expect("Starting Locust")

                wait_for_server(f"http://localhost:{port}/")
                response = requests.get(f"http://localhost:{port}/")

                tp.expect("No run time limit set, use CTRL+C to interrupt")
                tp.terminate()
                tp.expect("Shutting down")

                tp.not_expect_any("Traceback")

                # check response afterwards, because it really isn't as informative as stderr
                self.assertEqual(200, response.status_code)
                d = pq(response.content.decode("utf-8"))
                self.assertIn('"state": "running"', str(d))

    @unittest.skipIf(sys.platform == "darwin", reason="This is too messy on macOS")
    def test_autostart_w_run_time(self):
        port = get_free_tcp_port()
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --web-port {port} -t 1 --autostart --autoquit 0", expect_return_code=None
            ) as tp:
                tp.expect("Starting Locust")
                tp.expect("Run time limit set to 1 seconds")

                wait_for_server(f"http://localhost:{port}/")
                response = requests.get(f"http://localhost:{port}/")

                if not IS_WINDOWS:
                    tp.terminate()
                    tp.expect("Shutting down")

                tp.not_expect_any("Traceback")

                # check response afterwards, because it really isn't as informative as stderr
                d = pq(response.content.decode("utf-8"))

                self.assertEqual(200, response.status_code)
                self.assertIn('"state": "running"', str(d))

    @unittest.skipIf(IS_WINDOWS, reason="Signal handling on windows is hard")
    def test_run_autostart_with_multiple_locustfiles(self):
        with TemporaryDirectory() as temp_dir:
            with mock_locustfile(dir=temp_dir):
                with temporary_file(
                    content=textwrap.dedent(
                        """
                    from locust import User, task, constant, events
                    class TestUser(User):
                        wait_time = constant(1)
                        @task
                        def my_task(self):
                            print("running my_task()")
                """
                    ),
                    dir=temp_dir,
                ):
                    with TestProcess(f"locust -f {temp_dir} --autostart -u 2 --exit-code-on-error 0") as tp:
                        tp.expect("Starting Locust")
                        tp.expect('All users spawned: {"TestUser": 1, "UserSubclass": 1} (2 total users)')
                        tp.terminate()
                        tp.expect("Shutting down (exit code 0)")

    @unittest.skipIf(sys.platform == "darwin", reason="Disable on macOS for now because it has issues on GH")
    def test_autostart_w_load_shape(self):
        port = get_free_tcp_port()
        with mock_locustfile(
            content=MOCK_LOCUSTFILE_CONTENT
            + textwrap.dedent(
                """
            from locust import LoadTestShape
            class LoadTestShape(LoadTestShape):
                def tick(self):
                    run_time = self.get_run_time()
                    if run_time < 1:
                        return (10, 1)

                    return None
            """
            )
        ) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --web-port {port} --autostart", expect_return_code=None
            ) as tp:
                tp.expect("Starting Locust")
                tp.expect("Starting web interface")

                wait_for_server(f"http://localhost:{port}/")
                response = requests.get(f"http://localhost:{port}/")
                self.assertEqual(200, response.status_code)

                tp.expect("Shape test starting")
                tp.expect("--run-time limit reached")

    @unittest.skipIf(sys.platform == "darwin", reason="Disable on macOS for now because it has issues on GH")
    def test_autostart_multiple_locustfiles_with_shape(self):
        port = get_free_tcp_port()
        content = textwrap.dedent(
            """
            from locust import User, task, between
            class TestUser2(User):
                wait_time = between(0.5, 1.5)
                @task
                def my_task(self):
                    print("running my_task() again")
            """
        )
        with mock_locustfile(content=content) as mocked1:
            with temporary_file(
                content=textwrap.dedent(
                    """
                from locust import User, task, between, LoadTestShape
                class LoadTestShape(LoadTestShape):
                    def tick(self):
                        run_time = self.get_run_time()
                        if run_time < 2:
                            return (10, 1)

                        return None

                class TestUser(User):
                    wait_time = between(0.5, 1.5)
                    @task
                    def my_task(self):
                        print("running my_task()")
            """
                )
            ) as mocked2:
                # macOS on GH is slow so we need some extra time
                # for the webui to start and then finish gracefully
                autoquit = 5 if sys.platform == "darwin" else 0
                with TestProcess(
                    f"locust -f {mocked1.file_path},{mocked2} -u 5 -r 5 --web-port {port} --autostart --autoquit {autoquit}",
                    expect_timeout=6,
                    sigint_on_exit=False,
                ) as tp:
                    tp.expect("Starting Locust")
                    tp.expect("Starting web interface")

                    wait_for_server(f"http://localhost:{port}/")
                    response = requests.get(f"http://localhost:{port}/")
                    self.assertEqual(200, response.status_code)

                    tp.expect("Shape test starting")
                    tp.expect("Shape test stopping")

                    tp.expect("--run-time limit reached")
                    tp.expect("--autoquit time reached")
                    tp.expect("Shutting down")

                    tp.expect_any("running my_task()", stream="stdout")
                    tp.expect_any("running my_task() again", stream="stdout")

    @unittest.skipIf(platform.system() == "Darwin", reason="Messy on macOS on GH")
    @unittest.skipIf(IS_WINDOWS, reason="Signal handling on windows is hard")
    def test_web_options(self):
        port = get_free_tcp_port()
        if platform.system() != "Darwin":
            # MacOS only sets up the loopback interface for 127.0.0.1 and not for 127.*.*.*, so we can't test this
            with mock_locustfile() as mocked:
                with TestProcess(f"locust -f {mocked.file_path} --web-host 127.0.0.2 --web-port {port}"):
                    wait_for_server(f"http://127.0.0.2:{port}/")
                    response = requests.get(f"http://127.0.0.2:{port}/")
                    self.assertEqual(200, response.status_code)

        port = get_free_tcp_port()
        with mock_locustfile() as mocked:
            with TestProcess(f"locust -f {mocked.file_path} --web-host * --web-port {port}"):
                wait_for_server(f"http://127.0.0.1:{port}/")
                response = requests.get(f"http://127.0.0.1:{port}/")
                self.assertEqual(200, response.status_code)

    @unittest.skipIf(IS_WINDOWS, reason="termios doesnt exist on windows, and thus we cannot import pty")
    def test_input(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
        from locust import User, TaskSet, task, between

        class UserSubclass(User):
            wait_time = between(0.2, 0.8)
            @task
            def t(self):
                print("Test task is running")
        """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(f"locust -f {mocked.file_path} --headless -u 0", use_pty=True) as tp:
                tp.expect('All users spawned: {"UserSubclass": 0} (0 total users)')

                tp.send_input("w")
                tp.expect("Ramping to 1 users at a rate of 100.00 per second")
                tp.expect('All users spawned: {"UserSubclass": 1} (1 total users)')
                tp.expect("Test task is running", stream="stdout")

                tp.send_input("W")
                tp.expect("Ramping to 11 users at a rate of 100.00 per second")
                tp.expect('All users spawned: {"UserSubclass": 11} (11 total users)')
                tp.expect("Test task is running", stream="stdout")

                tp.send_input("s")
                tp.expect("Ramping to 10 users at a rate of 100.00 per second")
                tp.expect('All users spawned: {"UserSubclass": 10} (10 total users)')
                tp.expect("Test task is running", stream="stdout")

                tp.send_input("S")
                tp.expect("Ramping to 0 users at a rate of 100.00 per second")
                tp.expect('All users spawned: {"UserSubclass": 0} (0 total users)')

                # This should not do anything since we are already at zero users
                tp.send_input("S")

                # ensure stats printer printed at least one report before shutting down and that there was a final report printed as well
                tp.expect_any("Aggregated")
                # Stop locust process
                tp.terminate()
                tp.expect("Shutting down (exit code 0)")
                tp.expect("Aggregated")
                tp.expect("Response time percentiles (approximated)")

    @unittest.skipIf(IS_WINDOWS, reason="termios doesnt exist on windows, and thus we cannot import pty")
    def test_autospawn_browser(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """

        from pytest import MonkeyPatch
        import sys
        import webbrowser

        monkeypatch = MonkeyPatch()

        def open_new_tab(url):
            print("browser opened with url", url)
            sys.exit(0)

        monkeypatch.setattr(webbrowser, "open_new_tab", open_new_tab)
        print("patched")
        from locust import User, TaskSet, task, between
        class UserSubclass(User):
            @task
            def t(self):
                print("Test task is running")

        """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(f"locust -f {mocked.file_path}", use_pty=True, sigint_on_exit=False) as tp:
                tp.expect("Starting web interface at")
                tp.send_input("\n")
                tp.expect("browser opened", stream="stdout")

    def test_spawning_with_fixed(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
        from locust import User, task, constant

        class User1(User):
            fixed_count = 2
            wait_time = constant(1)

            @task
            def t(self):
                print("Test task is running")

        class User2(User):
            wait_time = constant(1)
            @task
            def t(self):
                print("Test task is running")

        class User3(User):
            wait_time = constant(1)
            @task
            def t(self):
                print("Test task is running")
        """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless -u 10 -r 10 --loglevel INFO",
            ) as tp:
                tp.expect("Ramping to 10 users at a rate of 10.00 per second")
                tp.expect('All users spawned: {"User1": 2, "User2": 4, "User3": 4} (10 total users)')
                tp.expect("Test task is running", stream="stdout")

                # ensure stats printer printed at least one report before shutting down and that there was a final report printed as well
                tp.expect_any("Aggregated")
                if not IS_WINDOWS:
                    tp.terminate()
                    tp.expect("Shutting down (exit code 0)")
                    tp.expect("Aggregated")

    def test_spawing_with_fixed_multiple_locustfiles(self):
        with mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_A) as mocked1:
            with mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_B) as mocked2:
                with TestProcess(
                    f"locust -f {mocked1.file_path},{mocked2.file_path} --headless -u 10 -r 10 --loglevel INFO",
                ) as tp:
                    tp.expect("Ramping to 10 users at a rate of 10.00 per second")
                    tp.expect('All users spawned: {"TestUser1": 5, "TestUser2": 5} (10 total users)')
                    tp.expect("running my_task()", stream="stdout")

                    # ensure stats printer printed at least one report before shutting down and that there was a final report printed as well
                    tp.expect("Aggregated")
                    if not IS_WINDOWS:
                        tp.terminate()
                        tp.expect("Shutting down (exit code 0)")
                        tp.expect("Aggregated")

    def test_warning_with_lower_user_count_than_fixed_count(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
        from locust import User, task, constant

        class User1(User):
            fixed_count = 2
            wait_time = constant(1)

            @task
            def t(self):
                pass

        class User2(User):
            fixed_count = 2
            wait_time = constant(1)

            @task
            def t(self):
                pass
        """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(f"locust -f {mocked.file_path} --headless -u 3") as tp:
                tp.expect("Total fixed_count of User classes (4) is greater than ")
                tp.expect("Aggregated")

    def test_with_package_as_locustfile(self):
        with TemporaryDirectory() as temp_dir:
            with open(f"{temp_dir}/__init__.py", mode="w"):
                with mock_locustfile(dir=temp_dir):
                    with TestProcess(f"locust -f {temp_dir} --headless --exit-code-on-error 0") as tp:
                        tp.expect("Starting Locust")
                        tp.expect('All users spawned: {"UserSubclass": 1} (1 total users)')

    def test_command_line_user_selection(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
        from locust import User, task, constant

        class User1(User):
            wait_time = constant(1)
            @task
            def t(self):
                print("User1 is running")

        class User2(User):
            wait_time = constant(1)
            @task
            def t(self):
                print("User2 is running")

        class User3(User):
            wait_time = constant(1)
            @task
            def t(self):
                print("User3 is running")
        """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless -u 5 -r 10 User2 User3",
            ) as tp:
                tp.expect('All users spawned: {"User2": 3, "User3": 2} (5 total users)')
                tp.expect("User2 is running", stream="stdout")
                tp.expect("User3 is running", stream="stdout")
                tp.terminate()
                tp.not_expect_any("User1 is running", stream="stdout")

    def test_html_report_option(self):
        html_template = "some_name_{u}_{r}_{t}.html"
        expected_filename = "some_name_11_5_1.html"

        with mock_locustfile() as mocked:
            # Get system temp directory
            temp_dir = tempfile.gettempdir()

            # Define the input filename as well as the resulting filename within the temp directory
            html_report_file_path = os.path.join(temp_dir, html_template)
            output_html_report_file_path = os.path.join(temp_dir, expected_filename)

            with TestProcess(
                f"locust -f {mocked.file_path} --host https://test.com/ -u 11 -r 5 -t 1s --headless --exit-code-on-error 0 --html {html_report_file_path}",
                sigint_on_exit=False,
            ) as tp:
                # make sure correct name is generated based on filename arguments
                tp.expect(expected_filename)
                tp.expect("Shutting down (exit code 0)")

            with open(output_html_report_file_path, encoding="utf-8") as f:
                html_report_content = f.read()

            _, locustfile = os.path.split(mocked.file_path)
            self.assertIn(locustfile, html_report_content)

            # make sure host appears in the report
            self.assertIn("https://test.com/", html_report_content)
            self.assertIn('"show_download_link": false', html_report_content)
            self.assertRegex(html_report_content, r'"start_time": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"')
            self.assertRegex(html_report_content, r'"end_time": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"')
            self.assertRegex(html_report_content, r'"duration": "\d* seconds?"')

    def test_run_with_userclass_picker(self):
        with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_A) as file1:
            with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_B) as file2:
                with TestProcess(f"locust -f {file1},{file2} --class-picker -L DEBUG") as tp:
                    tp.expect("Starting Locust")
                    tp.expect("Starting web interface at")
                    tp.expect("Locust is running with the UserClass Picker Enabled")

    def test_error_when_duplicate_userclass_names(self):
        MOCK_LOCUSTFILE_CONTENT_C = textwrap.dedent(
            """
            from locust import User, task, constant, events
            class TestUser1(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """
        )
        with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_A) as file1:
            with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_C) as file2:
                with TestProcess(f"locust -f {file1},{file2}", expect_return_code=1, sigint_on_exit=False) as tp:
                    tp.expect("Duplicate user class names: TestUser1 is defined")

    def test_no_error_when_same_userclass_in_two_files(self):
        with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_A) as file1:
            MOCK_LOCUSTFILE_CONTENT_C = textwrap.dedent(
                f"""
                from {os.path.basename(file1)[:-3]} import TestUser1
            """
            )
            print(MOCK_LOCUSTFILE_CONTENT_C)
            with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_C) as file2:
                with TestProcess(f"locust -f {file1},{file2} -u 5 -r 5 --headless") as tp:
                    tp.expect("running my_task", stream="stdout")

    def test_error_when_duplicate_shape_class_names(self):
        MOCK_LOCUSTFILE_CONTENT_C = MOCK_LOCUSTFILE_CONTENT_A + textwrap.dedent(
            """
            from locust import LoadTestShape
            class TestShape(LoadTestShape):
                def tick(self):
                    run_time = self.get_run_time()
                    if run_time < 2:
                        return (10, 1)

                    return None
            """
        )
        MOCK_LOCUSTFILE_CONTENT_D = MOCK_LOCUSTFILE_CONTENT_B + textwrap.dedent(
            """
            from locust import LoadTestShape
            class TestShape(LoadTestShape):
                def tick(self):
                    run_time = self.get_run_time()
                    if run_time < 2:
                        return (10, 1)

                    return None
            """
        )
        with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_C) as file1:
            with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_D) as file2:
                with TestProcess(f"locust -f {file1},{file2}", sigint_on_exit=False, expect_return_code=1) as tp:
                    tp.expect("Duplicate shape classes: TestShape")

    def test_error_when_providing_both_run_time_and_a_shape_class(self):
        content = MOCK_LOCUSTFILE_CONTENT + textwrap.dedent(
            """
            from locust import LoadTestShape
            class TestShape(LoadTestShape):
                def tick(self):
                    return None
            """
        )
        with mock_locustfile(content=content) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --run-time 1s --headless --exit-code-on-error 0",
                sigint_on_exit=False,
            ) as tp:
                tp.expect("--run-time, --users or --spawn-rate have no impact on LoadShapes")
                tp.expect("The following option(s) will be ignored: --run-time")

    def test_shape_class_log_disabled_parameters(self):
        content = MOCK_LOCUSTFILE_CONTENT + textwrap.dedent(
            """
            from locust import LoadTestShape

            class TestShape(LoadTestShape):
                def tick(self):
                    return None
            """
        )
        with mock_locustfile(content=content) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless --exit-code-on-error 0 --users 1 --spawn-rate 1",
                sigint_on_exit=False,
            ) as tp:
                tp.expect("Shape test starting.")
                tp.expect("--run-time, --users or --spawn-rate have no impact on LoadShapes")
                tp.expect("The following option(s) will be ignored: --users, --spawn-rate")

    def test_shape_class_with_use_common_options(self):
        content = MOCK_LOCUSTFILE_CONTENT + textwrap.dedent(
            """
            from locust import LoadTestShape

            class TestShape(LoadTestShape):
                use_common_options = True

                def tick(self):
                    return None
            """
        )
        with mock_locustfile(content=content) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --run-time 1s --users 1 --spawn-rate 1 --headless --exit-code-on-error 0",
                sigint_on_exit=False,
            ) as tp:
                tp.expect("Shape test starting.")
                tp.proc.wait(1)
                tp.not_expect_any("--run-time, --users or --spawn-rate have no impact on LoadShapes")
                tp.not_expect_any("The following option(s) will be ignored:")

    def test_error_when_locustfiles_directory_is_empty(self):
        with TemporaryDirectory() as temp_dir:
            with TestProcess(f"locust -f {temp_dir}", expect_return_code=1) as tp:
                tp.expect(f"Could not find any locustfiles in directory '{temp_dir}'")

    def test_error_when_no_tasks_match_tags(self):
        content = """
from locust import HttpUser, TaskSet, task, constant, LoadTestShape, tag
class MyUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = constant(1)
    @tag("tag1")
    @task
    def task1(self):
        print("task1")
    """
        with mock_locustfile(content=content) as mocked:
            with TestProcess(f"locust -f {mocked.file_path} --headless --tags tag2", expect_return_code=1) as tp:
                tp.expect("MyUser had no tasks left after filtering")
                tp.expect("No tasks defined on MyUser")

    @unittest.skipIf(IS_WINDOWS, reason="Signal handling on windows is hard")
    def test_graceful_exit_when_keyboard_interrupt(self):
        with temporary_file(
            content=textwrap.dedent(
                """
                from locust import User, events, task, constant, LoadTestShape
                @events.test_stop.add_listener
                def on_test_stop(environment, **kwargs) -> None:
                    print("Test Stopped")

                class LoadTestShape(LoadTestShape):
                    def tick(self):
                        run_time = self.get_run_time()
                        if run_time < 3:
                            return (10, 1)

                        return None

                class TestUser(User):
                    wait_time = constant(3)
                    @task
                    def my_task(self):
                        print("running my_task()")
            """
            )
        ) as mocked:
            with TestProcess(f"locust -f {mocked} --headless") as tp:
                tp.expect("Shape test starting")
                tp.expect("Ramping to 10 users at a rate of 1.00 per second")
                tp.terminate()
                tp.expect("Exiting due to CTRL+C interruption")
                tp.expect("Test Stopped", stream="stdout")

                tp.expect("Shutting down")
                tp.expect("Aggregated")

    def test_exception_in_init_event(self):
        with mock_locustfile(
            content=textwrap.dedent(
                """
            from locust import User, task, constant, events
            @events.init.add_listener
            def _(*args, **kw):
                raise Exception("something went wrong")

            class TestUser(User):
                wait_time = constant(10)
                @task
                def my_task(self):
                    pass
                    """
            )
        ) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --host https://test.com", expect_return_code=1, sigint_on_exit=False
            ) as tp:
                tp.expect("something went wrong")

    def test_json_schema(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
            from locust import HttpUser, task, constant

            class QuickstartUser(HttpUser):
                wait_time = constant(1)

                @task
                def hello_world(self):
                    self.client.get("/")

            """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            proc = TestProcess(
                f"locust -f {mocked.file_path} --host http://google.com --headless -u 5 -r 5 -t 1 --json",
                sigint_on_exit=False,
                join_timeout=2,
            )
            proc.close()
            stdout = "\n".join(proc.stdout_output)

            try:
                data = json.loads(stdout)
            except json.JSONDecodeError:
                self.fail(f"Trying to parse {stdout} as json failed")

            if not data:
                self.fail(f"No data in json: {stdout}")

            result = data[0]
            self.assertEqual(float, type(result["last_request_timestamp"]))
            self.assertEqual(float, type(result["start_time"]))
            self.assertEqual(int, type(result["num_requests"]))
            self.assertEqual(int, type(result["num_none_requests"]))
            self.assertEqual(float, type(result["total_response_time"]))
            self.assertEqual(float, type(result["max_response_time"]))
            self.assertEqual(float, type(result["min_response_time"]))
            self.assertEqual(int, type(result["total_content_length"]))
            self.assertEqual(dict, type(result["response_times"]))
            self.assertEqual(dict, type(result["num_reqs_per_sec"]))
            self.assertEqual(dict, type(result["num_fail_per_sec"]))

    def test_json_file(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
            from locust import HttpUser, task, constant

            class QuickstartUser(HttpUser):
                wait_time = constant(1)

                @task
                def hello_world(self):
                    self.client.get("/")

            """
        )
        output_base = "locust_output"
        output_filepath = f"{output_base}.json"
        if os.path.exists(output_filepath):
            os.remove(output_filepath)
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --host http://google.com --headless -u 5 -r 5 -t 2 --json-file {output_base}",
                sigint_on_exit=False,
            ) as tp:
                tp.proc.wait(3)
                tp.not_expect_any("error: argument --json-file: expected one argument")

            self.assertTrue(os.path.exists(output_filepath))
            with open(output_filepath, encoding="utf-8") as file:
                [stats] = json.load(file)
                self.assertEqual(stats["name"], "/")

        if os.path.exists(output_filepath):
            os.remove(output_filepath)

    def test_pytest_style_locustfile(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
import time

def test_first(session):
    resp = session.get("/")
    resp.raise_for_status()
    resp = session.get("/doesntexist")
    time.sleep(10)

def test_second(fastsession):
    resp = fastsession.get("/")
    resp.raise_for_status()
    resp = fastsession.get("/doesntexist")
    time.sleep(10)

def test_xxcrash(session):
    raise Exception("Only two users launched, and pytest sorts them alphabetically, this should never be called")
"""
        )
        output_base = "locust_output"
        output_filepath = f"{output_base}.json"
        if os.path.exists(output_filepath):
            os.remove(output_filepath)
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} -H https://www.locust.io --headless -u 2 -r 10 -t 3 --exit-code-on-error 0",
            ) as tp:
                tp.expect(
                    "/                                                                                  2     0(0.00%)",
                )
                tp.expect(
                    "/doesntexist                                                                       2   2(100.00%)"
                )
                tp.not_expect_any("Traceback")
                assert tp.proc.wait(3) == 0

    def test_no_host_should_quit_test(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
            from locust import HttpUser, task, constant

            class QuickstartUser(HttpUser):
                wait_time = constant(1)

                @task
                def hello_world(self):
                    self.client.get("/")

            """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless",
                sigint_on_exit=False,
            ) as tp:
                tp.expect("Starting Locust")
                tp.expect(
                    "You must specify the base host. Either in the host attribute in the User class, or on the command line using the --host option."
                )
                tp.expect("Stopping Locust...")
                tp.expect("Shutting down")

    def test_no_host_should_stop_test(self):
        port = get_free_tcp_port()

        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
            from locust import HttpUser, task, constant

            class QuickstartUser(HttpUser):
                wait_time = constant(1)

                @task
                def hello_world(self):
                    self.client.get("/")

            """
        )

        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --autostart --web-port {port} --run-time 1s --autoquit 0",
                sigint_on_exit=False,
            ) as tp:
                tp.expect("Starting Locust")
                tp.expect("Starting web interface")
                tp.expect(
                    "You must specify the base host. Either in the host attribute in the User class, or on the command line using the --host option."
                )
                tp.expect("Stopping Locust...")
                tp.not_expect_any("Shutting down")
                tp.expect("--run-time limit reached")
                tp.expect("Shutting down")


class DistributedIntegrationTests(ProcessIntegrationTest):
    failed_port_check = False

    def setUp(self):
        if self.failed_port_check:
            # fail immediately
            raise Exception("Port 5557 was (still) busy when starting a new test case")
        for _ in range(5):
            if not is_port_in_use(5557):
                break
            else:
                gevent.sleep(1)
        else:
            self.failed_port_check = True
            raise Exception("Port 5557 was (still) busy when starting a new test case")
        super().setUp()

    def test_expect_workers(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless --master --expect-workers 2 --expect-workers-max-wait 1 -L DEBUG",
                expect_return_code=1,
                sigint_on_exit=False,
            ) as tp:
                tp.expect("Waiting for workers to be ready, 0 of 2 connected")
                tp.expect("Gave up waiting for workers to connect")
                tp.expect("Quitting")
                tp.not_expect_any("Traceback")

    def test_distributed_events(self):
        content = (
            MOCK_LOCUSTFILE_CONTENT
            + """
from locust import events
from locust.runners import MasterRunner
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner):
        print("test_start on master")
    else:
        print("test_start on worker")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner):
        print("test_stop on master")
    else:
        print("test_stop on worker")
"""
        )
        with mock_locustfile(content=content) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless --master --expect-workers 1 -t 1 --exit-code-on-error 0 -L DEBUG",
                sigint_on_exit=False,
                join_timeout=2,
            ) as tp:
                with TestProcess(f"locust -f {mocked.file_path} --worker -L DEBUG", sigint_on_exit=False) as tp_worker:
                    tp.expect("test_start on master", stream="stdout")
                    tp_worker.expect("test_start on worker", stream="stdout")
                    tp.expect("test_stop on master", stream="stdout")
                    tp_worker.expect("test_stop on worker", stream="stdout")
                    tp.not_expect_any("Traceback")
                    tp_worker.not_expect_any("Traceback")

    def test_distributed_tags(self):
        content = """
from locust import HttpUser, TaskSet, task, between, LoadTestShape, tag
class SecondUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(0, 0.1)
    @tag("tag1")
    @task
    def task1(self):
        print("task1")

    @tag("tag2")
    @task
    def task2(self):
        print("task2")
"""
        with mock_locustfile(content=content) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless --master -t 1 --expect-workers 1 -u 2 --exit-code-on-error 0 -L DEBUG --tags tag1",
                join_timeout=2,
            ):
                with TestProcess(f"locust -f {mocked.file_path} --worker -L DEBUG", sigint_on_exit=False) as tp_worker:
                    tp_worker.expect("task1", stream="stdout")
                    tp_worker.proc.wait(2)
                    tp_worker.not_expect_any("task2", stream="stdout")
                    tp_worker.not_expect_any("ERROR")
                    tp_worker.not_expect_any("Traceback")

    def test_distributed(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    pass
            """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless --master --expect-workers 1 -u 3 -r 99 -t 1",
                join_timeout=2,
                sigint_on_exit=False,
            ) as tp:
                with TestProcess(f"locust -f {mocked.file_path} --worker", sigint_on_exit=False, join_timeout=3):
                    tp.expect('All users spawned: {"User1": 3} (3 total users)')
                    tp.expect("Shutting down (exit code 0)")

    def test_distributed_report_timeout_expired(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    pass
            """
        )
        with (
            mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked,
            patch_env("LOCUST_WAIT_FOR_WORKERS_REPORT_AFTER_RAMP_UP", "0.01") as _,
        ):
            with TestProcess(
                f"locust -f {mocked.file_path} --headless --master --expect-workers 1 -u 3 -r 99 -t 1",
                sigint_on_exit=False,
            ) as tp:
                with TestProcess(f"locust -f {mocked.file_path} --worker", sigint_on_exit=False, join_timeout=2):
                    tp.expect(
                        "Spawning is complete and report waittime is expired, but not all reports received from workers:",
                    )
                    tp.expect("Shutting down (exit code 0)")

    def test_locustfile_distribution(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    pass
            """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            proc = TestProcess(
                f"locust -f {mocked.file_path} --headless --master --expect-workers 2 -t 1s", sigint_on_exit=False
            )
            proc_worker = TestProcess("locust -f - --worker", sigint_on_exit=False)
            proc_worker_2 = TestProcess("locust -f - --worker", sigint_on_exit=False)

            proc.expect('All users spawned: {"User1": 1} (1 total users)')
            proc.expect("Shutting down (exit code 0)")

            for p in [proc, proc_worker, proc_worker_2]:
                p.close()
                proc.not_expect_any("Traceback")

    def test_locustfile_distribution_with_workers_started_first(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    print("hello")
            """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess("locust -f - --worker", sigint_on_exit=False) as tp_worker:
                with TestProcess(
                    f"locust -f {mocked.file_path} --headless --master -u 5 -r 5 --expect-workers 1 -t 1",
                    sigint_on_exit=False,
                ) as tp:
                    tp.expect('All users spawned: {"User1": ')
                    tp.expect("Shutting down (exit code 0)")

                tp_worker.expect("hello", stream="stdout")

    def test_distributed_with_locustfile_distribution_not_plain_filename(self):
        LOCUSTFILE_CONTENT = textwrap.dedent(
            """
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    pass
            """
        )
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path},{mocked.file_path} --headless --master --expect-workers 1 -t 1",
                sigint_on_exit=False,
                join_timeout=2,
            ) as tp:
                with TestProcess("locust -f - --worker", sigint_on_exit=False) as tp_worker:
                    tp.expect('All users spawned: {"User1": 1} (1 total users)')
                    tp_worker.proc.wait(2)
                    tp_worker.not_expect_any("Traceback")

                tp.not_expect_any("Traceback")

    def test_worker_indexes(self):
        content = """
from locust import HttpUser, task, between

class AnyUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(0, 0.1)
    @task
    def my_task(self):
        print("worker index:", self.environment.runner.worker_index)
"""
        with mock_locustfile(content=content) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless --master --expect-workers 2 -u 2 -L DEBUG -t 2",
                join_timeout=3,
                sigint_on_exit=False,
            ) as tp:
                with TestProcess(
                    f"locust -f {mocked.file_path} --worker -L DEBUG", sigint_on_exit=False, join_timeout=2
                ) as tp_worker_1:
                    with TestProcess(
                        f"locust -f {mocked.file_path} --worker -L DEBUG", sigint_on_exit=False, join_timeout=2
                    ) as tp_worker_2:
                        tp.expect("All users spawned")

                        # worker index: {id}
                        indexes = [int(tp_worker_1.stdout_output[0][-1]), int(tp_worker_2.stdout_output[0][-1])]
                        indexes.sort()
                        self.assertEqual(0, indexes[0], f"expected index 0 but got {indexes[0]}")
                        self.assertEqual(1, indexes[1], f"expected index 1 but got {indexes[1]}")

    @unittest.skipIf(IS_WINDOWS, reason="--processes doesnt work on windows")
    def test_processes(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --processes 4 --headless --exit-code-on-error 0", join_timeout=2
            ) as tp:
                tp.expect("(index 3) reported as ready")
                tp.expect("All users spawned")
                tp.terminate()
                tp.expect("The last worker quit, stopping test")
                tp.not_expect_any("Traceback")

    @unittest.skipIf(IS_WINDOWS, reason="--processes doesnt work on windows")
    def test_processes_autodetect(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --processes -1 --headless --exit-code-on-error 0", join_timeout=2
            ) as tp:
                tp.expect("(index 0) reported as ready")
                tp.expect("All users spawned")
                tp.terminate()
                tp.expect("The last worker quit, stopping test")
                tp.not_expect_any("Traceback")

    @unittest.skipIf(IS_WINDOWS, reason="--processes doesnt work on windows")
    def test_processes_separate_worker(self):
        with mock_locustfile() as mocked:
            master_proc = TestProcess(
                f"locust -f {mocked.file_path} --master --headless --run-time 1 --exit-code-on-error 0 --expect-workers-max-wait 2",
                sigint_on_exit=False,
                join_timeout=3,
            )
            worker_parent_proc = TestProcess(
                f"locust -f {mocked.file_path} --processes 4 --worker", sigint_on_exit=False, join_timeout=3
            )

            worker_parent_proc.close()
            master_proc.close()

            worker_parent_proc.not_expect_any("Traceback")
            master_proc.not_expect_any("Traceback")
            master_proc.not_expect_any("Gave up waiting for workers to connect")
            master_proc.expect("(index 3) reported as ready")
            master_proc.expect("Shutting down (exit code 0)")

    @unittest.skipIf(IS_WINDOWS, reason="--processes doesnt work on windows")
    def test_processes_ctrl_c(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --processes 4 --headless -L DEBUG", expect_return_code=1
            ) as tp:
                tp.expect("Starting Locust")
                tp.expect("Started child worker")
                tp.expect("Started child worker")
                tp.expect("Started child worker")
                tp.expect("Started child worker")
                tp.expect("Waiting for workers to be ready, 0 of 4 connected")

                children: list[psutil.Process] = psutil.Process(tp.proc.pid).children(recursive=True)
                self.assertEqual(len(children), 4, "unexpected number of child worker processes")

                tp.expect("(index 3) reported as ready")
                tp.expect("All users spawned")

                tp.terminate()

                tp.expect("Shutting down (exit code 0)")
                tp.expect("The last worker quit, stopping test.")

                gone, alive = psutil.wait_procs(children, timeout=2)
                # Be good boys and cleanup if needed
                for p in alive:
                    p.kill()

                self.assertEqual(len(gone), len(children), "child processes failed to terminate")

                # ensure no weird escaping in error report. Not really related to ctrl-c...
                tp.expect(", 'Connection refused') ")

                tp.not_expect_any("Traceback")

    @unittest.skipIf(IS_WINDOWS, reason="--processes doesnt work on windows")
    def test_workers_shut_down_if_master_is_gone(self):
        content = """
from locust import HttpUser, task, constant, runners
runners.MASTER_HEARTBEAT_TIMEOUT = 2

class AnyUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = constant(1)
    @task
    def my_task(self):
        print("worker index:", self.environment.runner.worker_index)
"""
        with mock_locustfile(content=content) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --master --headless --expect-workers 2",
                sigint_on_exit=False,
                expect_return_code=None,
            ) as tp_master:
                with TestProcess(
                    f"locust -f {mocked.file_path} --worker --processes 2 --headless",
                    sigint_on_exit=False,
                    join_timeout=2,
                ) as tp_worker_parent:
                    tp_master.expect("All users spawned")
                    tp_master.proc.kill()
                    tp_master.proc.wait(2)

                    tp_worker_parent.expect("worker index:", stream="stdout")
                    tp_worker_parent.expect("Didn't get heartbeat from master in over ")
                    tp_worker_parent.expect("Shutting down")
                    tp_worker_parent.not_expect_any("Traceback")

    @unittest.skipIf(IS_WINDOWS, reason="--processes doesnt work on windows")
    def test_processes_error_doesnt_blow_up_completely(self):
        with mock_locustfile() as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --processes 4 -L DEBUG UserThatDoesntExist",
                expect_return_code=1,
                sigint_on_exit=False,
            ) as tp:
                tp.expect("Unknown User(s): UserThatDoesntExist")
                tp.proc.wait(1)
                # the error message should repeat 4 times for the workers and once for the master
                total_logs = sum(
                    [1 if ("Unknown User(s): UserThatDoesntExist" in line) else 0 for line in tp.stderr_output]
                )
                self.assertEqual(total_logs, 5)
                tp.not_expect_any("Traceback")

    @unittest.skipIf(IS_WINDOWS, reason="--processes doesnt work on windows")
    @unittest.skipIf(sys.platform == "darwin", reason="Flaky on macOS :-/")
    def test_processes_workers_quit_unexpected(self):
        content = """
from locust import runners, events, User, task
import sys
runners.HEARTBEAT_INTERVAL = 0.1

@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    if isinstance(environment.runner, runners.WorkerRunner):
        sys.exit(42)

class AnyUser(User):
    @task
    def mytask(self):
        pass
"""
        with mock_locustfile(content=content) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --processes 2 --worker", sigint_on_exit=False, expect_return_code=42
            ) as tp_worker:
                with TestProcess(f"locust -f {mocked.file_path} --master --headless -t 1") as tp_master:
                    tp_worker.expect("INFO/locust.runners: sys.exit(42) called")
                    tp_worker.proc.wait(2)
                    tp_worker.not_expect_any("Traceback")
                    tp_master.expect("failed to send heartbeat, setting state to missing")
                    tp_master.terminate()
                    tp_master.expect("Shutting down")
                    tp_master.not_expect_any("Traceback")


class TelemetryTests(ProcessIntegrationTest):
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
                f"locust -f {mocked.file_path} --headless -u 5 -r 5 --otel --run-time 1s --stop-timeout 5s",
                expect_return_code=None,
                extra_env={
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
                host = "http://www.locust.io"
                wait_time = constant(1)

                @task
                def t(self):
                    self.client.get("/hello")
                    self.client.get("/world", name="/custom-name")
            """
        )
        with mock_locustfile(content=locustfile) as mocked:
            with TestProcess(
                f"locust -f {mocked.file_path} --headless -u 5 -r 5 --otel --run-time 1s",
                expect_return_code=None,
                extra_env={
                    "OTEL_METRICS_EXPORTER": "none",
                    "OTEL_TRACES_EXPORTER": "console",
                },
            ) as tp:
                tp.expect("GET /hello", stream="stdout")
                tp.expect("GET /custom-name", stream="stdout")
                tp.not_expect_any("GET /world", stream="stdout")
