from __future__ import annotations

import json
import os
import platform
import re
import select
import selectors
import signal
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from contextlib import ExitStack, contextmanager
from subprocess import DEVNULL, PIPE, STDOUT, Popen
from tempfile import NamedTemporaryFile, TemporaryDirectory
from threading import Thread
from typing import IO, Callable, Optional, Union, cast
from unittest import TestCase

import gevent
import gevent.monkey
import psutil
import requests
from gevent.fileobject import FileObject

gevent.monkey.patch_all()

# from gevent.subprocess import PIPE, Popen
from pyquery import PyQuery as pq
from requests.exceptions import RequestException

from .mock_locustfile import MOCK_LOCUSTFILE_CONTENT, mock_locustfile
from .util import get_free_tcp_port, patch_env, temporary_file

SHORT_SLEEP = 2 if sys.platform == "darwin" else 1  # macOS is slow on GH, give it some extra time


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def wait_for_output_condition_non_threading(
    proc: Popen, output_lines: list[str], condition: str, timeout: int | float = 30
) -> bool:
    start_time = time.time()
    while True:
        combined_output = "\n".join(output_lines)
        if condition in combined_output:
            return True
        if time.time() - start_time >= timeout:
            return False
        gevent.sleep(0.1)


def assert_return_code(test_case, process_returncode, acceptable_codes=None):
    if acceptable_codes is None:
        acceptable_codes = [0]

    test_case.assertIn(process_returncode, acceptable_codes, f"Process failed with return code {process_returncode}")


class PopenContextManager:
    def __init__(self, args=None, file_content=None, port=None, **kwargs):
        self.args = ["locust"] if args is None else args
        self.kwargs = kwargs
        self.process = None
        self.output_lines = []
        self.temp_file_path = None

        if file_content is not None:
            self.temp_file_path = self.create_temp_file(file_content)
            self.args += ["-f", self.temp_file_path]

        if port is not None:
            self.args += ["--web-port", str(port)]

        print(f"PopenContextManager initialized with args: {self.args} and kwargs: {self.kwargs}")

    def create_temp_file(self, content):
        fd, path = tempfile.mkstemp(suffix=".py", text=True)
        with os.fdopen(fd, "w") as temp_file:
            temp_file.write(content)
        print(f"Temporary file created at: {path}")
        return path

    def __enter__(self):
        shell = sys.platform == "win32"
        print(f"Starting subprocess with shell={shell}")

        # Log the environment variables being used
        print(f"Environment variables for subprocess: {self.kwargs.get('env', os.environ)}")

        try:
            self.process = subprocess.Popen(
                self.args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=shell,
                **self.kwargs,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
            print(f"Subprocess started with PID: {self.process.pid}")
            print(f"Subprocess arguments: {self.args}")
        except Exception as e:
            print(f"Failed to start subprocess: {e}")
            raise

        # Spawn gevent greenlets to read the output
        self.stdout_reader = gevent.spawn(self._read_output, self.process.stdout, "STDOUT")
        self.stderr_reader = gevent.spawn(self._read_output, self.process.stderr, "STDERR")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Entering __exit__ of PopenContextManager")

        if self.process:
            try:
                # First, wait a short period to allow the process to exit gracefully
                print("Waiting for subprocess to exit gracefully...")
                self.process.wait(timeout=5)
                print(f"Subprocess exited with return code {self.process.returncode}")
            except subprocess.TimeoutExpired:
                # If the process hasn't exited, attempt to terminate it
                print("Subprocess did not exit within timeout; attempting to terminate")
                self.terminate_process()
                try:
                    self.process.wait(timeout=5)
                    print(f"Subprocess terminated with return code {self.process.returncode}")
                except subprocess.TimeoutExpired:
                    print("Subprocess did not terminate after terminate signal")

        # Ensure readers are joined
        gevent.joinall([self.stdout_reader, self.stderr_reader])

        # Log collected outputs
        print(f"Collected STDOUT lines: {self.output_lines}")

        # Close the stdout and stderr streams explicitly
        self.close_pipes()

        # Remove the temporary file if it exists
        self.remove_temp_file()

        # Log the final return code
        if self.process:
            print(f"Subprocess with PID {self.process.pid} exited with return code {self.process.returncode}")

    def terminate_process(self):
        try:
            if sys.platform == "win32":
                self.process.terminate()
                print("Called process.terminate() on Windows")
            else:
                self.process.send_signal(subprocess.signal.SIGTERM)
                print("Sent SIGTERM to subprocess")
            self.process.wait(timeout=5)
            print("Subprocess terminated gracefully")
        except subprocess.TimeoutExpired:
            print("Subprocess did not terminate in time; killing it")
            self.process.kill()
            self.process.wait()
            print("Subprocess killed")
        except Exception as e:
            print(f"Error while terminating subprocess: {e}")

    def close_pipes(self):
        for pipe in [self.process.stdout, self.process.stderr]:
            if pipe:
                pipe.close()
                print(f"Closed pipe: {pipe}")

    def remove_temp_file(self):
        if self.temp_file_path:
            try:
                os.remove(self.temp_file_path)
                print(f"Removed temporary file: {self.temp_file_path}")
            except OSError as e:
                print(f"Error removing temporary file: {e}")

    def _read_output(self, pipe, pipe_name):
        try:
            for line in iter(pipe.readline, ""):
                line = line.rstrip("\n")
                self.output_lines.append(line)
                print(f"{pipe_name}: {line}")
        except Exception as e:
            print(f"Error reading {pipe_name}: {e}")
        finally:
            pipe.close()
            print(f"{pipe_name} pipe closed")


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
        self.timeout = gevent.Timeout(60)
        self.timeout.start()
        os.environ["PYTHONUNBUFFERED"] = "1"

    def tearDown(self):
        self.timeout.cancel()
        super().tearDown()

    def assert_run(self, cmd: list[str], timeout: int = 5) -> subprocess.CompletedProcess[str]:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        self.assertEqual(0, out.returncode, f"locust run failed with exit code {out.returncode}:\n{out.stderr}")
        return out


class StandaloneIntegrationTests(ProcessIntegrationTest):
    @contextmanager
    def create_temp_locustfile(self, content, dir=None):
        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py", dir=dir) as temp_file:
            temp_file.write(content)
            temp_file.flush()
            yield temp_file.name
        os.unlink(temp_file.name)

    def make_http_request(self, port, method="GET", path="/", data=None, timeout=10):
        url = f"http://localhost:{port}{path}"
        if method.upper() == "GET":
            return requests.get(url, timeout=timeout)
        elif method.upper() == "POST":
            return requests.post(url, data=data, timeout=timeout)
        else:
            raise ValueError("Unsupported HTTP method.")

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_help_arg(self):
        """
        Test that running 'locust --help' displays the correct help message.
        """
        args = [sys.executable, "-m", "locust", "--help"]

        with PopenContextManager(args) as manager:
            manager.process.wait()

        output = "\n".join(manager.output_lines).strip()

        # Assertions
        self.assertTrue(output.startswith("Usage: locust [options] [UserClass ...]"))
        self.assertIn("Common options:", output)
        self.assertIn("-f <filename>, --locustfile <filename>", output)
        self.assertIn("Logging options:", output)
        self.assertIn("--skip-log-setup", output)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_custom_arguments(self):
        port = get_free_tcp_port()
        file_content = textwrap.dedent("""
            from locust import User, task, constant, events
            @events.init_command_line_parser.add_listener
            def _(parser, **kw):
                parser.add_argument("--custom-string-arg")
            class TestUser(User):
                wait_time = constant(10)
                @task
                def my_task(self):
                    print(self.environment.parsed_options.custom_string_arg)
        """)

        with PopenContextManager(
            file_content=file_content,
            args=[
                sys.executable,
                "-m",
                "locust",
                "--custom-string-arg",
                "command_line_value",
                "--web-port",
                str(port),
            ],
        ) as manager:
            if not wait_for_output_condition_non_threading(
                manager.process, manager.output_lines, "Starting Locust", timeout=30
            ):
                self.fail("Timeout waiting for Locust to start.")

            if not wait_for_output_condition_non_threading(
                manager.process, manager.output_lines, "Starting web interface at", timeout=30
            ):
                self.fail("Timeout waiting for web interface to start.")

            response = requests.post(
                f"http://127.0.0.1:{port}/swarm",
                data={
                    "user_count": 1,
                    "spawn_rate": 1,
                    "host": "https://localhost",
                    "custom_string_arg": "web_form_value",
                },
            )

            self.assertEqual(response.status_code, 200)

        combined_output = "\n".join(manager.output_lines)
        self.assertRegex(
            combined_output, r".*Shutting down[\S\s]*Aggregated.*", "No stats table printed after shutting down"
        )
        self.assertNotRegex(
            combined_output, r".*Aggregated[\S\s]*Shutting down.*", "Stats table printed BEFORE shutting down"
        )
        self.assertNotIn("command_line_value", combined_output)
        self.assertIn("web_form_value", combined_output)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_custom_exit_code(self):
        port = get_free_tcp_port()
        file_content = textwrap.dedent("""
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
        """)

        with PopenContextManager(
            file_content=file_content,
            args=[
                sys.executable,
                "-m",
                "locust",
                "--web-port",
                str(port),
            ],
        ) as manager:
            if not wait_for_output_condition_non_threading(
                manager.process, manager.output_lines, "Starting Locust", timeout=30
            ):
                self.fail("Timeout waiting for Locust to start.")

            if not wait_for_output_condition_non_threading(
                manager.process, manager.output_lines, "Starting web interface at", timeout=30
            ):
                self.fail("Timeout waiting for web interface to start.")

            manager.process.send_signal(signal.SIGTERM)

            manager.process.wait(timeout=3)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Shutting down (exit code 42)", combined_output)
        self.assertIn("Exit code in quit event 42", combined_output)
        self.assertEqual(42, manager.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_percentile_parameter(self):
        port = get_free_tcp_port()

        file_content = textwrap.dedent("""
            from locust import User, task, constant, events
            from locust import stats
            stats.PERCENTILES_TO_CHART = [0.9, 0.4]
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """)

        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_file_path = temp_file.name

        try:
            args = [sys.executable, "-m", "locust", "-f", temp_file_path, "--autostart", "--web-port", str(port)]

            with PopenContextManager(args) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Starting Locust", timeout=30
                ):
                    manager.process.terminate()
                    manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to start.")

                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Starting web interface at", timeout=30
                ):
                    manager.process.terminate()
                    manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for web interface to start.")

                try:
                    response = requests.get(f"http://localhost:{port}/", timeout=10)
                    self.assertEqual(200, response.status_code)
                except requests.exceptions.RequestException as e:
                    manager.process.terminate()
                    manager.process.wait(timeout=5)
                    self.fail(f"Failed to connect to Locust web interface: {e}\nLocust output: {manager.output_lines}")

                manager.process.send_signal(signal.SIGTERM)

                manager.process.wait(timeout=5)

            combined_output = "\n".join(manager.output_lines)

            self.assertIn("Starting web interface at", combined_output)
            self.assertIn("Starting Locust", combined_output)
        finally:
            os.unlink(temp_file_path)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_percentiles_to_statistics(self):
        port = get_free_tcp_port()

        file_content = textwrap.dedent("""
            from locust import User, task, constant, events
            from locust.stats import PERCENTILES_TO_STATISTICS
            PERCENTILES_TO_STATISTICS = [0.9, 0.99]
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """)

        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_file_path = temp_file.name

        try:
            args = [sys.executable, "-m", "locust", "-f", temp_file_path, "--autostart", "--web-port", str(port)]

            with PopenContextManager(args) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Starting Locust", timeout=30
                ):
                    manager.process.terminate()
                    manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to start.")

                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Starting web interface at", timeout=30
                ):
                    manager.process.terminate()
                    manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for web interface to start.")

                response = requests.get(f"http://localhost:{port}/")
                self.assertEqual(200, response.status_code)

                manager.process.send_signal(signal.SIGTERM)

                manager.process.wait(timeout=5)

            combined_output = "\n".join(manager.output_lines)

            self.assertIn("Starting web interface at", combined_output)
            self.assertIn("Starting Locust", combined_output)
        finally:
            os.unlink(temp_file_path)

    def test_invalid_percentile_parameter(self):
        file_content = textwrap.dedent("""
                from locust import User, task, constant, events
                from locust import stats
                stats.PERCENTILES_TO_CHART  = [1.2]
                class TestUser(User):
                    wait_time = constant(3)
                    @task
                    def my_task(self):
                        print("running my_task()")
            """)

        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_file_path = temp_file.name

        try:
            args = [sys.executable, "-m", "locust", "-f", temp_file_path, "--autostart"]

            with PopenContextManager(args) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "parameter need to be float", timeout=30
                ):
                    manager.process.terminate()
                    manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for invalid percentile error message.")

                manager.process.wait(timeout=5)

            combined_output = "\n".join(manager.output_lines)

            self.assertIn("parameter need to be float and value between. 0 < percentile < 1 Eg 0.95", combined_output)
            self.assertEqual(1, manager.process.returncode)
        finally:
            os.unlink(temp_file_path)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_webserver_multiple_locustfiles_in_directory(self):
        """
        Test that Locust can start with multiple Locustfiles located in a directory
        and that the web interface functions correctly.
        """
        with TemporaryDirectory() as temp_dir:
            with (
                mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_A, dir=temp_dir),
                mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_B, dir=temp_dir),
            ):
                port = get_free_tcp_port()

                args = [sys.executable, "-m", "locust", "-f", temp_dir, "--web-port", str(port)]

                with PopenContextManager(args) as manager:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Starting Locust", timeout=30
                    ):
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail("Timeout waiting for Locust to start.")

                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Starting web interface at", timeout=30
                    ):
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail("Timeout waiting for web interface to start.")

                    try:
                        response = requests.get(f"http://localhost:{port}/", timeout=10)
                        self.assertEqual(
                            200, response.status_code, msg=f"Expected status code 200, got {response.status_code}"
                        )
                    except requests.exceptions.RequestException as e:
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail(f"Failed to connect to Locust web interface: {e}")

                    manager.process.send_signal(signal.SIGTERM)

                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Shutting down (exit code 0)", timeout=30
                    ):
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail("Timeout waiting for Locust to shut down.")

                    try:
                        manager.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail("Locust process did not terminate gracefully after SIGTERM.")

            combined_output = "\n".join(manager.output_lines)

            self.assertIn(
                "Starting web interface at",
                combined_output,
                msg="Expected 'Starting web interface at' not found in output.",
            )
            self.assertIn("Starting Locust", combined_output, msg="Expected 'Starting Locust' not found in output.")
            self.assertIn(
                "Shutting down (exit code 0)",
                combined_output,
                msg="Expected 'Shutting down (exit code 0)' not found in output.",
            )
            self.assertNotIn(
                "Locust is running with the UserClass Picker Enabled",
                combined_output,
                msg="Unexpected 'UserClass Picker Enabled' message found in output.",
            )
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

            assert_return_code(self, manager.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_webserver_multiple_locustfiles_with_shape(self):
        """
        Test that Locust can start with multiple Locustfiles and a shape file,
        and that the web interface functions correctly.
        """
        shape_file_content = textwrap.dedent(
            """
            from locust import User, task, between, LoadTestShape

            class LoadTestShape(LoadTestShape):
                def tick(self):
                    run_time = self.get_run_time()
                    if run_time < 2:
                        return (10, 1)  # (users, spawn rate)
                    return None  # Stop the test

            class TestUser(User):
                wait_time = between(2, 4)

                @task
                def my_task(self):
                    print("running my_task()")
            """
        )
        user_file_content = textwrap.dedent(
            """
            from locust import User, task, between

            class TestUser2(User):
                wait_time = between(2, 4)

                @task
                def my_task(self):
                    print("running my_task() again")
            """
        )

        with TemporaryDirectory() as temp_dir:
            with (
                mock_locustfile(content=user_file_content, dir=temp_dir),
                mock_locustfile(content=shape_file_content, dir=temp_dir),
            ):
                port = get_free_tcp_port()

                args = [
                    sys.executable,
                    "-m",
                    "locust",
                    "-f",
                    temp_dir,
                    "--web-port",
                    str(port),
                ]

                with PopenContextManager(args) as manager:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Starting Locust", timeout=30
                    ):
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail("Timeout waiting for Locust to start.")

                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Starting web interface at", timeout=30
                    ):
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail("Timeout waiting for web interface to start.")

                    try:
                        response = requests.get(f"http://localhost:{port}/", timeout=10)
                        self.assertEqual(
                            200, response.status_code, msg=f"Expected status code 200, got {response.status_code}"
                        )
                    except requests.exceptions.RequestException as e:
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail(f"Failed to connect to Locust web interface: {e}")

                    manager.process.send_signal(signal.SIGTERM)

                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Shutting down (exit code 0)", timeout=30
                    ):
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail("Timeout waiting for Locust to shut down.")

                    try:
                        manager.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        manager.process.terminate()
                        manager.process.wait(timeout=5)
                        self.fail("Locust process did not terminate gracefully after SIGTERM.")

        combined_output = "\n".join(manager.output_lines)

        self.assertIn(
            "Starting web interface at",
            combined_output,
            msg="Expected 'Starting web interface at' not found in output.",
        )
        self.assertIn("Starting Locust", combined_output, msg="Expected 'Starting Locust' not found in output.")
        self.assertIn(
            "Shutting down (exit code 0)",
            combined_output,
            msg="Expected 'Shutting down (exit code 0)' not found in output.",
        )
        self.assertNotIn(
            "Locust is running with the UserClass Picker Enabled",
            combined_output,
            msg="Unexpected 'UserClass Picker Enabled' message found in output.",
        )
        self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

        assert_return_code(self, manager.process.returncode)

    def test_default_headless_spawn_options(self):
        with mock_locustfile() as mocked:
            with PopenContextManager(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--host",
                    "https://test.com/",
                    "--run-time",
                    "1s",
                    "--headless",
                    "--loglevel",
                    "DEBUG",
                    "--exit-code-on-error",
                    "0",
                    "--stop-timeout",
                    "1s",
                ],
            ) as popen_ctx:
                popen_ctx.process.wait(timeout=4)

                all_output = "\n".join(popen_ctx.output_lines)

                self.assertNotIn("Traceback", all_output)

                expected_message = 'Spawning additional {"UserSubclass": 1} ({"UserSubclass": 0} already running)...'
                self.assertIn(expected_message, all_output)

                assert_return_code(self, popen_ctx.process.returncode)

    def test_invalid_stop_timeout_string(self):
        with mock_locustfile() as mocked:
            with PopenContextManager(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--host",
                    "https://test.com/",
                    "--stop-timeout",
                    "asdf1",
                ],
            ) as popen_ctx:
                popen_ctx.process.wait()

                all_output = "\n".join(popen_ctx.output_lines)

                self.assertIn("ERROR/locust.main: Valid --stop-timeout formats are", all_output)

                self.assertEqual(1, popen_ctx.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_headless_spawn_options_wo_run_time(self):
        """
        Test Locust's headless mode with spawn options without specifying run time.
        Ensures that Locust starts, spawns all users, and shuts down gracefully.
        """
        with mock_locustfile() as mocked:
            args = [
                sys.executable,
                "-m",
                "locust",
                "-f",
                mocked.file_path,
                "--host",
                "https://test.com/",
                "--headless",
                "--exit-code-on-error",
                "0",
            ]

            with PopenContextManager(args) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "All users spawned", timeout=30
                ):
                    manager.process.terminate()
                    try:
                        manager.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        manager.process.kill()
                        manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to spawn all users.")

                manager.process.send_signal(signal.SIGTERM)

                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Shutting down (exit code 0)", timeout=30
                ):
                    manager.process.terminate()
                    try:
                        manager.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        manager.process.kill()
                        manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    manager.process.terminate()
                    manager.process.wait(timeout=5)
                    self.fail("Locust process did not terminate gracefully after SIGTERM.")

            combined_output = "\n".join(manager.output_lines)

            self.assertIn("All users spawned", combined_output, msg="Expected 'All users spawned' not found in output.")
            self.assertIn(
                "Shutting down (exit code 0)",
                combined_output,
                msg="Expected 'Shutting down (exit code 0)' not found in output.",
            )

            self.assertNotIn(
                "Locust is running with the UserClass Picker Enabled",
                combined_output,
                msg="Unexpected 'UserClass Picker Enabled' message found in output.",
            )
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

            assert_return_code(self, manager.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_run_headless_with_multiple_locustfiles(self):
        """
        Test Locust's headless mode with multiple Locustfiles.
        Ensures that Locust starts, spawns users from multiple Locustfiles, and shuts down gracefully.
        """
        with TemporaryDirectory() as temp_dir:
            with mock_locustfile(dir=temp_dir):
                user_file_content = textwrap.dedent("""
                    from locust import User, task, constant

                    class TestUser(User):
                        wait_time = constant(1)

                        @task
                        def my_task(self):
                            print("running my_task()")
                """)
                with self.create_temp_locustfile(content=user_file_content, dir=temp_dir):
                    args = [
                        sys.executable,
                        "-m",
                        "locust",
                        "-f",
                        temp_dir,
                        "--headless",
                        "-u",
                        "2",
                        "--exit-code-on-error",
                        "0",
                    ]

                    with PopenContextManager(args) as manager:
                        if not wait_for_output_condition_non_threading(
                            manager.process, manager.output_lines, "All users spawned", timeout=30
                        ):
                            manager.process.terminate()
                            try:
                                manager.process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                manager.process.kill()
                                manager.process.wait(timeout=5)
                            self.fail("Timeout waiting for Locust to spawn all users.")

                        manager.process.send_signal(signal.SIGTERM)

                        if not wait_for_output_condition_non_threading(
                            manager.process, manager.output_lines, "Shutting down (exit code 0)", timeout=30
                        ):
                            manager.process.terminate()
                            try:
                                manager.process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                manager.process.kill()
                                manager.process.wait(timeout=5)
                            self.fail("Timeout waiting for Locust to shut down.")

                        try:
                            manager.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            manager.process.terminate()
                            manager.process.wait(timeout=5)
                            self.fail("Locust process did not terminate gracefully after SIGTERM.")

                    combined_output = "\n".join(manager.output_lines)

                    self.assertIn(
                        '"TestUser": 1', combined_output, msg="Expected 'TestUser' user count not found in output."
                    )
                    self.assertIn(
                        '"UserSubclass": 1', combined_output, msg="Expected 'UserSubclass' user count not found."
                    )
                    self.assertIn(
                        "Shutting down (exit code 0)", combined_output, msg="Expected shutdown message not found."
                    )

                    self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

                    assert_return_code(self, manager.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_default_headless_spawn_options_with_shape(self):
        """
        Test Locust with default headless spawn options and a custom LoadTestShape.
        Ensures that Locust runs the shape and properly shuts down with exit code 0.
        """
        MOCK_LOCUSTFILE_CONTENT = textwrap.dedent("""
            from locust import User, task, constant

            class TestUser(User):
                wait_time = constant(1)

                @task
                def my_task(self):
                    print("running my_task()")
        """)

        shape_content = textwrap.dedent("""
            from locust import LoadTestShape

            class MyLoadTestShape(LoadTestShape):
                def tick(self):
                    run_time = self.get_run_time()
                    if run_time < 2:
                        return (10, 1)  # (users, spawn rate)
                    return None  # Stop the test
        """)

        combined_content = MOCK_LOCUSTFILE_CONTENT + shape_content

        with self.create_temp_locustfile(content=combined_content) as mocked:
            args = [
                sys.executable,
                "-m",
                "locust",
                "-f",
                mocked,
                "--host",
                "https://test.com/",
                "--headless",
                "--exit-code-on-error",
                "0",
            ]

            with PopenContextManager(args) as manager:
                shape_update_message = "Shape test updating to 10 users at 1.00 spawn rate"
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, shape_update_message, timeout=10
                ):
                    manager.process.terminate()
                    try:
                        manager.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        manager.process.kill()
                        manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to run the shape test.")

                shutdown_message = "Shutting down (exit code 0)"
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, shutdown_message, timeout=10
                ):
                    print("Locust output after expected shutdown time:")
                    print("\n".join(manager.output_lines))

                    manager.process.terminate()
                    try:
                        manager.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        manager.process.kill()
                        manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.process.terminate()
                    manager.process.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully after SIGTERM.")

            combined_output = "\n".join(manager.output_lines)

            self.assertIn(shape_update_message, combined_output, msg="Shape test output not found.")
            self.assertRegex(
                combined_output,
                r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*",
                msg="Aggregated output not found before shutdown.",
            )
            self.assertIn(shutdown_message, combined_output, msg="Expected shutdown message not found.")
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

            assert_return_code(self, manager.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_run_headless_with_multiple_locustfiles_with_shape(self):
        """
        Test Locust's headless mode with multiple Locustfiles including a LoadTestShape.
        Ensures that Locust starts, runs the shape, spawns users from multiple Locustfiles, and shuts down gracefully.
        """
        with TemporaryDirectory() as temp_dir:
            with self.create_temp_locustfile(
                content=textwrap.dedent("""
                    from locust import User, task, between

                    class TestUser2(User):
                        wait_time = between(2, 4)

                        @task
                        def my_task(self):
                            print("running my_task() again")
                """),
                dir=temp_dir,
            ) as mocked1:
                shape_file_content = textwrap.dedent("""
                    from locust import User, task, between, LoadTestShape

                    class MyLoadTestShape(LoadTestShape):
                        def tick(self):
                            run_time = self.get_run_time()
                            if run_time < 2:
                                return (10, 1)  # (users, spawn rate)
                            return None  # Stop the test

                    class TestUser(User):
                        wait_time = between(2, 4)

                        @task
                        def my_task(self):
                            print("running my_task()")
                """)

                with self.create_temp_locustfile(
                    content=shape_file_content,
                    dir=temp_dir,
                ) as mocked2:
                    args = [
                        sys.executable,
                        "-m",
                        "locust",
                        "-f",
                        f"{mocked1},{mocked2}",
                        "--host",
                        "https://test.com/",
                        "--headless",
                        "--exit-code-on-error",
                        "0",
                    ]

                    with PopenContextManager(args) as manager:
                        shape_start_message = "Shape test starting"
                        shape_update_message = "Shape test updating to 10 users at 1.00 spawn rate"
                        shape_stop_message = "Shape test stopping"
                        shutdown_message = "Shutting down (exit code 0)"

                        messages_to_check = [
                            shape_start_message,
                            shape_update_message,
                            shape_stop_message,
                            shutdown_message,
                        ]

                        for message in messages_to_check:
                            if not wait_for_output_condition_non_threading(
                                manager.process, manager.output_lines, message, timeout=10
                            ):
                                print(f"Locust output after expected '{message}' time:")
                                print("\n".join(manager.output_lines))
                                manager.process.terminate()
                                try:
                                    manager.process.wait(timeout=5)
                                except subprocess.TimeoutExpired:
                                    manager.process.kill()
                                    manager.process.wait(timeout=5)
                                self.fail(f"Timeout waiting for Locust to output: {message}")

                        try:
                            manager.process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            print("Locust did not terminate within the expected time.")
                            manager.process.terminate()
                            manager.process.wait(timeout=10)
                            self.fail("Locust process did not terminate gracefully after SIGTERM.")

                    combined_output = "\n".join(manager.output_lines)

                    self.assertIn("running my_task()", combined_output, msg="TestUser task output not found.")
                    self.assertIn("running my_task() again", combined_output, msg="TestUser2 task output not found.")
                    self.assertRegex(
                        combined_output,
                        r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*",
                        msg="Aggregated output not found before shutdown.",
                    )

                    self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

                    assert_return_code(self, manager.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_autostart_wo_run_time(self):
        """
        Test Locust's autostart functionality without specifying run time.
        Ensures that Locust starts automatically, informs about no run time limit,
        and shuts down gracefully upon receiving a termination signal.
        """
        port = get_free_tcp_port()
        with mock_locustfile() as mocked:
            args = [
                sys.executable,
                "-m",
                "locust",
                "-f",
                mocked.file_path,
                "--web-port",
                str(port),
                "--autostart",
            ]

            with PopenContextManager(args) as manager:
                start_message = "Starting Locust"
                no_run_time_message = "No run time limit set, use CTRL+C to interrupt"

                messages_to_check = [
                    start_message,
                    no_run_time_message,
                ]

                for message in messages_to_check:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, message, timeout=10
                    ):
                        print(f"Locust output after expected '{message}' time:")
                        print("\n".join(manager.output_lines))
                        manager.process.terminate()
                        try:
                            manager.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            manager.process.kill()
                            manager.process.wait(timeout=5)
                        self.fail(f"Timeout waiting for Locust to output: {message}")

                try:
                    response = self.make_http_request(f"{port}", method="GET", path="/")
                    self.assertEqual(200, response.status_code, "Locust web interface did not return status code 200.")
                except requests.exceptions.RequestException as e:
                    manager.process.terminate()
                    self.fail(f"Failed to connect to Locust web interface: {e}")

                manager.process.send_signal(signal.SIGTERM)

                shutdown_message = "Shutting down"

                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, shutdown_message, timeout=10
                ):
                    print("Locust output after expected shutdown time:")
                    print("\n".join(manager.output_lines))
                    manager.process.terminate()
                    try:
                        manager.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        manager.process.kill()
                        manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.process.terminate()
                    manager.process.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully after SIGTERM.")

            combined_output = "\n".join(manager.output_lines)

            self.assertIn(start_message, combined_output, msg="Start message not found in output.")
            self.assertIn(no_run_time_message, combined_output, msg="No run time message not found in output.")
            self.assertIn(shutdown_message, combined_output, msg="Shutdown message not found in output.")
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

            d = pq(response.content.decode("utf-8"))
            self.assertIn('"state": "running"', str(d), msg="Expected 'running' state not found in response.")

    @unittest.skipIf(sys.platform == "darwin", reason="This is too messy on macOS")
    def test_autostart_w_run_time(self):
        """
        Test Locust's autostart functionality with a specified run time.
        Ensures that Locust starts automatically, applies the run time limit,
        and shuts down gracefully after the run time.
        """
        port = get_free_tcp_port()
        with mock_locustfile() as mocked:
            args = [
                sys.executable,
                "-m",
                "locust",
                "-f",
                mocked.file_path,
                "--web-port",
                str(port),
                "-t",
                "3",
                "--autostart",
                "--autoquit",
                "1",
            ]

            with PopenContextManager(args) as manager:
                start_message = "Starting Locust"
                run_time_message = "Run time limit set to 3 seconds"
                shutdown_message = "Shutting down"

                messages_to_check = [
                    start_message,
                    run_time_message,
                ]

                for message in messages_to_check:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, message, timeout=10
                    ):
                        print(f"Locust output after expected '{message}' time:")
                        print("\n".join(manager.output_lines))
                        manager.process.terminate()
                        try:
                            manager.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            manager.process.kill()
                            manager.process.wait(timeout=5)
                        self.fail(f"Timeout waiting for Locust to output: {message}")

                try:
                    response = self.make_http_request(f"{port}", method="GET", path="/")
                    self.assertEqual(200, response.status_code, "Locust web interface did not return status code 200.")
                except requests.exceptions.RequestException as e:
                    manager.process.terminate()
                    self.fail(f"Failed to connect to Locust web interface: {e}")

                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, shutdown_message, timeout=10
                ):
                    print("Locust output after expected shutdown time:")
                    print("\n".join(manager.output_lines))
                    manager.process.terminate()
                    try:
                        manager.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        manager.process.kill()
                        manager.process.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.process.terminate()
                    manager.process.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully.")

            combined_output = "\n".join(manager.output_lines)

            self.assertIn(start_message, combined_output, msg="Start message not found in output.")
            self.assertIn(run_time_message, combined_output, msg="Run time message not found in output.")
            self.assertIn(shutdown_message, combined_output, msg="Shutdown message not found in output.")
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

            d = pq(response.content.decode("utf-8"))
            self.assertIn('"state": "running"', str(d), msg="Expected 'running' state not found in response.")

            # assert_return_code(self, manager.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_run_autostart_with_multiple_locustfiles(self):
        """
        Test Locust's autostart functionality with multiple Locustfiles.
        Ensures that Locust starts automatically, spawns users from multiple Locustfiles,
        and shuts down gracefully.
        """
        with TemporaryDirectory() as temp_dir:
            with self.create_temp_locustfile(
                content=textwrap.dedent("""
                    from locust import User, task, constant

                    class TestUser(User):
                        wait_time = constant(1)

                        @task
                        def my_task(self):
                            print("running my_task()")
                """),
                dir=temp_dir,
            ) as mocked1:
                with self.create_temp_locustfile(
                    content=textwrap.dedent("""
                        from locust import User, task, constant

                        class UserSubclass(User):
                            wait_time = constant(1)

                            @task
                            def my_task(self):
                                print("running my_task()")
                    """),
                    dir=temp_dir,
                ) as mocked2:
                    port = get_free_tcp_port()
                    args = [
                        sys.executable,
                        "-m",
                        "locust",
                        "-f",
                        f"{mocked1},{mocked2}",
                        "--autostart",
                        "-u",
                        "2",
                        "--exit-code-on-error",
                        "0",
                        "--web-port",
                        str(port),
                    ]

                    with PopenContextManager(args) as manager:
                        start_message = "Starting Locust"
                        all_users_spawned_message = "All users spawned:"
                        user_count_messages = ['"TestUser": 1', '"UserSubclass": 1']
                        task_running_message = "running my_task()"
                        shutdown_message = "Shutting down (exit code 0)"

                        messages_to_check = [
                            start_message,
                            all_users_spawned_message,
                            *user_count_messages,
                            task_running_message,
                        ]

                        for message in messages_to_check:
                            if not wait_for_output_condition_non_threading(
                                manager.process, manager.output_lines, message, timeout=10
                            ):
                                print(f"Locust output after expected '{message}' time:")
                                manager.process.terminate()
                                try:
                                    manager.process.wait(timeout=5)
                                except subprocess.TimeoutExpired:
                                    manager.process.kill()
                                    manager.process.wait(timeout=5)
                                self.fail(f"Timeout waiting for Locust to output: {message}")

                        manager.process.send_signal(signal.SIGTERM)

                        if not wait_for_output_condition_non_threading(
                            manager.process, manager.output_lines, shutdown_message, timeout=10
                        ):
                            manager.process.terminate()
                            try:
                                manager.process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                manager.process.kill()
                                manager.process.wait(timeout=5)
                            self.fail("Timeout waiting for Locust to shut down.")

                        try:
                            manager.process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            manager.process.terminate()
                            manager.process.wait(timeout=10)
                            self.fail("Locust process did not terminate gracefully after SIGTERM.")

                    combined_output = "\n".join(manager.output_lines)

                    for message in messages_to_check + [shutdown_message]:
                        self.assertIn(
                            message, combined_output, msg=f"Expected message '{message}' not found in output."
                        )

                    self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")
                    assert_return_code(self, manager.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_autostart_w_load_shape(self):
        """
        Test Locust's autostart functionality with a custom LoadTestShape.
        Ensures that Locust starts automatically, applies the load shape,
        and shuts down gracefully after the autoquit time.
        """
        port = get_free_tcp_port()
        locustfile_content = textwrap.dedent("""
            from locust import User, task, constant, LoadTestShape

            class TestUser(User):
                wait_time = constant(1)

                @task
                def my_task(self):
                    print("running my_task()")

            class LoadTestShape(LoadTestShape):
                def tick(self):
                    run_time = self.get_run_time()
                    if run_time < 2:
                        return (10, 1)  # (users, spawn rate)
                    return None  # Stop the test
        """)

        with mock_locustfile(content=locustfile_content) as mocked:
            args = [
                sys.executable,
                "-m",
                "locust",
                "-f",
                mocked.file_path,
                "--web-port",
                str(port),
                "--autostart",
                "--autoquit",
                "3",
            ]

            with PopenContextManager(args) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Starting web interface at", timeout=30
                ):
                    manager.process.terminate()
                    self.fail("Timeout waiting for Locust web interface to start.")

                try:
                    response = self.make_http_request(f"{port}", method="GET", path="/", timeout=10)
                    self.assertEqual(200, response.status_code, "Locust web interface did not return status code 200.")
                except requests.exceptions.RequestException as e:
                    manager.process.terminate()
                    self.fail(f"Failed to connect to Locust web interface: {e}")

                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Starting Locust", timeout=30
                ):
                    manager.process.terminate()
                    self.fail("Timeout waiting for Locust to start.")

                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Shutting down (exit code 0)", timeout=50
                ):
                    manager.process.terminate()
                    self.fail("Timeout waiting for Locust to shut down after autoquit time.")

                try:
                    manager.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.process.terminate()
                    manager.process.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully after autoquit.")

            combined_output = "\n".join(manager.output_lines)

            self.assertIn("Starting Locust", combined_output, msg="Expected 'Starting Locust' not found in output.")
            self.assertIn(
                "Shape test starting", combined_output, msg="Expected 'Shape test starting' not found in output."
            )
            self.assertIn("Shutting down", combined_output, msg="Expected 'Shutting down' not found in output.")
            self.assertIn(
                "autoquit time reached", combined_output, msg="Expected 'autoquit time reached' not found in output."
            )
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")
            assert_return_code(self, manager.process.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_autostart_multiple_locustfiles_with_shape(self):
        """
        Test Locust's autostart functionality with multiple Locustfiles including a LoadTestShape.
        Ensures that Locust starts automatically, applies the load shape, spawns users from multiple Locustfiles,
        and shuts down gracefully after the autoquit time.
        """
        content1 = textwrap.dedent("""
            from locust import User, task, between

            class TestUser2(User):
                wait_time = between(2, 4)

                @task
                def my_task(self):
                    print("running my_task() again")
        """)
        content2 = textwrap.dedent("""
            from locust import User, task, between, LoadTestShape

            class CustomLoadTestShape(LoadTestShape):
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
        """)

        expected_outputs = [
            "Starting web interface at",
            "Shape test starting",
            "autoquit time reached",
            "Shutting down",
            "Starting Locust",
        ]

        with TemporaryDirectory() as temp_dir:
            with self.create_temp_locustfile(content=content1, dir=temp_dir) as mocked1:
                with self.create_temp_locustfile(content=content2, dir=temp_dir) as mocked2:
                    port = get_free_tcp_port()
                    args = [
                        sys.executable,
                        "-m",
                        "locust",
                        "-f",
                        f"{mocked1},{mocked2}",
                        "--autostart",
                        "--autoquit",
                        "3",
                        "--web-port",
                        str(port),
                    ]

                    with PopenContextManager(args) as manager:
                        try:
                            for output in expected_outputs:
                                if not wait_for_output_condition_non_threading(
                                    manager.process, manager.output_lines, output, timeout=60
                                ):
                                    self.fail(f"Timeout waiting for: {output}")

                        except Exception as e:
                            print(f"Test failed with exception: {e}")
                            print("Process output:")
                            print("\n".join(manager.output_lines))
                            raise

                        finally:
                            if manager.process.poll() is None:
                                manager.process.terminate()
                                try:
                                    manager.process.wait(timeout=5)
                                except subprocess.TimeoutExpired:
                                    manager.process.kill()

        combined_output = "\n".join(manager.output_lines)

        for output in expected_outputs:
            self.assertIn(output, combined_output, f"Expected output not found: {output}")

        self.assertIn("running my_task()", combined_output, msg="TestUser task output not found.")
        self.assertIn("running my_task() again", combined_output, msg="TestUser2 task output not found.")

        self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

        assert_return_code(self, manager.process.returncode)

    @unittest.skipIf(platform.system() == "Darwin", reason="Messy on macOS on GH")
    @unittest.skipIf(os.name == "nt", reason="Signal handling on windows is hard")
    def test_web_options(self):
        """
        Test Locust's web host options.
        Ensures that Locust starts with different web host configurations and the web interface is accessible.
        """
        expected_outputs = [
            "Starting web interface at",
            "Starting Locust",
        ]

        port = get_free_tcp_port()

        if platform.system() != "Darwin":
            with mock_locustfile() as mocked:
                args = [
                    sys.executable,
                    "-m",
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--web-host",
                    "127.0.0.2",
                    "--web-port",
                    str(port),
                ]

                with PopenContextManager(args) as manager:
                    for output in expected_outputs:
                        if not wait_for_output_condition_non_threading(
                            manager.process, manager.output_lines, output, timeout=30
                        ):
                            print(f"Locust output after expected '{output}' time:")
                            print("\n".join(manager.output_lines))
                            manager.process.terminate()
                            try:
                                manager.process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                manager.process.kill()
                                manager.process.wait(timeout=5)
                            self.fail(f"Timeout waiting for Locust to output: {output}")

                    try:
                        response = requests.get(f"http://127.0.0.2:{port}/", timeout=1)
                        self.assertEqual(
                            200, response.status_code, "Locust web interface did not return status code 200."
                        )
                    except requests.exceptions.RequestException as e:
                        self.fail(f"Failed to connect to Locust web interface: {e}")

        # Test with --web-host="*"
        with mock_locustfile() as mocked:
            args = [
                sys.executable,
                "-m",
                "locust",
                "-f",
                mocked.file_path,
                "--web-host",
                "*",
                "--web-port",
                str(port),
            ]

            with PopenContextManager(args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, output, timeout=30
                    ):
                        print(f"Locust output after expected '{output}' time:")
                        print("\n".join(manager.output_lines))
                        manager.process.terminate()
                        try:
                            manager.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            manager.process.kill()
                            manager.process.wait(timeout=5)
                        self.fail(f"Timeout waiting for Locust to output: {output}")

                try:
                    response = requests.get(f"http://127.0.0.1:{port}/", timeout=1)
                    self.assertEqual(200, response.status_code, "Locust web interface did not return status code 200.")
                except requests.exceptions.RequestException as e:
                    self.fail(f"Failed to connect to Locust web interface: {e}")

        all_output_lines = []

        if platform.system() != "Darwin":
            with mock_locustfile() as mocked:
                args = [
                    sys.executable,
                    "-m",
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--web-host",
                    "127.0.0.2",
                    "--web-port",
                    str(port),
                ]

                with PopenContextManager(args) as manager:
                    for output in expected_outputs:
                        if not wait_for_output_condition_non_threading(
                            manager.process, manager.output_lines, output, timeout=30
                        ):
                            print(f"Locust output after expected '{output}' time:")
                            print("\n".join(manager.output_lines))
                            manager.process.terminate()
                            try:
                                manager.process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                manager.process.kill()
                                manager.process.wait(timeout=5)
                            self.fail(f"Timeout waiting for Locust to output: {output}")

                    try:
                        response = requests.get(f"http://127.0.0.2:{port}/", timeout=1)
                        self.assertEqual(
                            200, response.status_code, "Locust web interface did not return status code 200."
                        )
                    except requests.exceptions.RequestException as e:
                        self.fail(f"Failed to connect to Locust web interface: {e}")

                    all_output_lines.extend(manager.output_lines)

        # Second run with --web-host="*"
        with mock_locustfile() as mocked:
            args = [
                sys.executable,
                "-m",
                "locust",
                "-f",
                mocked.file_path,
                "--web-host",
                "*",
                "--web-port",
                str(port),
            ]

            with PopenContextManager(args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, output, timeout=30
                    ):
                        print(f"Locust output after expected '{output}' time:")
                        print("\n".join(manager.output_lines))
                        manager.process.terminate()
                        try:
                            manager.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            manager.process.kill()
                            manager.process.wait(timeout=5)
                        self.fail(f"Timeout waiting for Locust to output: {output}")

                try:
                    response = requests.get(f"http://127.0.0.1:{port}/", timeout=1)
                    self.assertEqual(200, response.status_code, "Locust web interface did not return status code 200.")
                except requests.exceptions.RequestException as e:
                    self.fail(f"Failed to connect to Locust web interface: {e}")

                all_output_lines.extend(manager.output_lines)

        combined_output = "\n".join(all_output_lines)

        for output in expected_outputs:
            self.assertIn(output, combined_output, f"Expected output not found: {output}")

    @unittest.skipIf(os.name == "nt", reason="termios doesnt exist on windows, and thus we cannot import pty")
    def test_input(self):
        import pty

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
            stdin_m, stdin_s = pty.openpty()
            stdin = os.fdopen(stdin_m, "wb", 0)

            proc = subprocess.Popen(
                " ".join(
                    [
                        "locust",
                        "-f",
                        mocked.file_path,
                        "--headless",
                        "--run-time",
                        "7s",
                        "-u",
                        "0",
                        "--loglevel",
                        "INFO",
                    ]
                ),
                stderr=STDOUT,
                stdin=stdin_s,
                stdout=PIPE,
                shell=True,
                text=True,
                env=os.environ.copy(),
            )
            gevent.sleep(1)

            stdin.write(b"w")
            gevent.sleep(1)
            stdin.write(b"W")
            gevent.sleep(1)
            stdin.write(b"s")
            gevent.sleep(1)
            stdin.write(b"S")
            gevent.sleep(1)

            # This should not do anything since we are already at zero users
            stdin.write(b"S")
            gevent.sleep(1)

            output = proc.communicate()[0]
            stdin.close()
            self.assertIn("Ramping to 1 users at a rate of 100.00 per second", output)
            self.assertIn('All users spawned: {"UserSubclass": 1} (1 total users)', output)
            self.assertIn("Ramping to 11 users at a rate of 100.00 per second", output)
            self.assertIn('All users spawned: {"UserSubclass": 11} (11 total users)', output)
            self.assertIn("Ramping to 10 users at a rate of 100.00 per second", output)
            self.assertIn('All users spawned: {"UserSubclass": 10} (10 total users)', output)
            self.assertIn("Ramping to 0 users at a rate of 100.00 per second", output)
            self.assertIn('All users spawned: {"UserSubclass": 0} (0 total users)', output)
            self.assertIn("Test task is running", output)
            # ensure stats printer printed at least one report before shutting down and that there was a final report printed as well
            self.assertRegex(output, r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*")
            self.assertIn("Shutting down (exit code 0)", output)
            self.assertEqual(0, proc.returncode)

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

        expected_outputs = [
            "Ramping to 10 users at a rate of 10.00 per second",
            'All users spawned: {"User1": 2, "User2": 4, "User3": 4} (10 total users)',
            "Test task is running",
            "Shutting down (exit code 0)",
        ]

        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            args = [
                "-f",
                mocked.file_path,
                "--headless",
                "--run-time",
                "5s",
                "-u",
                "10",
                "-r",
                "10",
                "--loglevel",
                "INFO",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, output, timeout=30
                    ):
                        self.fail(f"Timeout waiting for: {output}")

            combined_output = "\n".join(manager.output_lines)

            for output in expected_outputs:
                self.assertIn(output, combined_output, f"Expected output not found: {output}")

            self.assertRegex(combined_output, r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*")

    def test_spawning_with_fixed_multiple_locustfiles(self):
        expected_outputs = [
            "Ramping to 10 users at a rate of 10.00 per second",
            'All users spawned: {"TestUser1": 5, "TestUser2": 5} (10 total users)',
            "running my_task()",
            "Shutting down (exit code 0)",
        ]

        with (
            mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_A) as mocked1,
            mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_B) as mocked2,
        ):
            args = [
                "-f",
                f"{mocked1.file_path},{mocked2.file_path}",
                "--headless",
                "--run-time",
                "5s",
                "-u",
                "10",
                "-r",
                "10",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, output, timeout=30
                    ):
                        self.fail(f"Timeout waiting for: {output}")

            combined_output = "\n".join(manager.output_lines)

            for output in expected_outputs:
                self.assertIn(output, combined_output, f"Expected output not found: {output}")

            self.assertRegex(combined_output, r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*")

            assert_return_code(self, manager.process.returncode)

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

        expected_outputs = [
            "Total fixed_count of User classes (4) is greater than ",
            "Shutting down (exit code 0)",
        ]

        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            args = [
                "-f",
                mocked.file_path,
                "--headless",
                "--run-time",
                "1s",
                "-u",
                "3",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, output, timeout=30
                    ):
                        self.fail(f"Timeout waiting for: {output}")

            combined_output = "\n".join(manager.output_lines)

            for output in expected_outputs:
                self.assertIn(output, combined_output, f"Expected output not found: {output}")

            assert_return_code(self, manager.process.returncode)

    def test_with_package_as_locustfile(self):
        expected_outputs = [
            "Starting Locust",
            "All users spawned:",
            '"UserSubclass": 1',
            "Shutting down (exit code 0)",
        ]

        with TemporaryDirectory() as temp_dir:
            init_path = os.path.join(temp_dir, "__init__.py")
            with open(init_path, mode="w"):
                pass

            with mock_locustfile(dir=temp_dir):
                args = [
                    "-f",
                    temp_dir,
                    "--headless",
                    "--exit-code-on-error",
                    "0",
                    "--run-time",
                    "2s",
                ]

                with PopenContextManager(["locust"] + args) as manager:
                    for output in expected_outputs:
                        if not wait_for_output_condition_non_threading(
                            manager.process, manager.output_lines, output, timeout=30
                        ):
                            self.fail(f"Timeout waiting for: {output}")

            combined_output = "\n".join(manager.output_lines)

            for output in expected_outputs:
                self.assertIn(output, combined_output, f"Expected output not found: {output}")

            assert_return_code(self, manager.process.returncode)

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

        expected_outputs = ["User2 is running", "User3 is running", "Shutting down (exit code 0)"]
        unexpected_output = "User1 is running"

        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            args = [
                "-f",
                mocked.file_path,
                "--headless",
                "--run-time",
                "2s",
                "-u",
                "5",
                "-r",
                "10",
                "User2",
                "User3",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, output, timeout=30
                    ):
                        self.fail(f"Timeout waiting for: {output}")

        combined_output = "\n".join(manager.output_lines)

        for output in expected_outputs:
            self.assertIn(output, combined_output, f"Expected output not found: {output}")

        self.assertNotIn(unexpected_output, combined_output, f"Unexpected output found: {unexpected_output}")

    def test_html_report_option(self):
        with mock_locustfile() as mocked:
            with temporary_file("", suffix=".html") as html_report_file_path:
                try:
                    subprocess.check_output(
                        [
                            "locust",
                            "-f",
                            mocked.file_path,
                            "--host",
                            "https://test.com/",
                            "--run-time",
                            "2s",
                            "--headless",
                            "--exit-code-on-error",
                            "0",
                            "--html",
                            html_report_file_path,
                        ],
                        stderr=subprocess.STDOUT,
                        timeout=10,
                        text=True,
                    ).strip()
                except subprocess.CalledProcessError as e:
                    raise AssertionError(f"Running locust command failed. Output was:\n\n{e.stdout}") from e

                with open(html_report_file_path, encoding="utf-8") as f:
                    html_report_content = f.read()

        # make sure title appears in the report
        _, locustfile = os.path.split(mocked.file_path)
        self.assertIn(locustfile, html_report_content)

        # make sure host appears in the report
        self.assertIn("https://test.com/", html_report_content)
        self.assertIn('"show_download_link": false', html_report_content)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_run_with_userclass_picker(self):
        port = get_free_tcp_port()

        with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_A) as file1:
            with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_B) as file2:
                args = ["locust", "-f", f"{file1},{file2}", "--class-picker", "--web-port", str(port)]
                with PopenContextManager(args) as manager:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Starting Locust", timeout=20
                    ):
                        self.fail("Timeout waiting for Locust to start.")

                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Starting web interface at", timeout=20
                    ):
                        self.fail("Timeout waiting for web interface to start.")

                    if not wait_for_output_condition_non_threading(
                        manager.process,
                        manager.output_lines,
                        "Locust is running with the UserClass Picker Enabled",
                        timeout=20,
                    ):
                        self.fail("Timeout waiting for UserClass Picker message.")

                    manager.process.send_signal(signal.SIGTERM)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Locust is running with the UserClass Picker Enabled", combined_output)
        self.assertIn("Starting Locust", combined_output)
        self.assertIn("Starting web interface at", combined_output)
        self.assertIn("Shutting down (exit code 0)", combined_output)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_error_when_duplicate_userclass_names(self):
        MOCK_LOCUSTFILE_CONTENT_C = textwrap.dedent("""
            from locust import User, task, constant, events

            class TestUser1(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """)

        with (
            temporary_file(content=MOCK_LOCUSTFILE_CONTENT_A) as file1,
            temporary_file(content=MOCK_LOCUSTFILE_CONTENT_C) as file2,
        ):
            args = [
                "-f",
                f"{file1},{file2}",
                "--headless",
                "--run-time",
                "5s",
                "-u",
                "1",
                "-r",
                "1",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.process,
                    manager.output_lines,
                    "Duplicate user class names: TestUser1 is defined",
                    timeout=5,
                ):
                    self.fail("Timeout waiting for duplicate user class error message.")

                try:
                    manager.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail("Locust process did not terminate as expected.")

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Duplicate user class names: TestUser1 is defined", combined_output)
        self.assertEqual(1, manager.process.returncode, "Process did not exit with return code 1 as expected.")

    def test_no_error_when_same_userclass_in_two_files(self):
        with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_A) as file1:
            MOCK_LOCUSTFILE_CONTENT_C = textwrap.dedent(f"""
                    from {os.path.basename(file1)[:-3]} import TestUser1
                """)
            print(MOCK_LOCUSTFILE_CONTENT_C)
            with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_C) as file2:
                args = [
                    "-f",
                    f"{file1},{file2}",
                    "--headless",
                    "--run-time",
                    "1s",
                    "-u",
                    "1",
                    "-r",
                    "1",
                ]

                with PopenContextManager(["locust"] + args) as manager:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "running my_task", timeout=50
                    ):
                        self.fail("Timeout waiting for 'running my_task' message.")

                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Shutting down (exit code 0)", timeout=10
                    ):
                        self.fail("Timeout waiting for Locust to shut down.")

        combined_output = "\n".join(manager.output_lines)
        self.assertIn("running my_task", combined_output)
        self.assertEqual(0, manager.process.returncode)

    def test_error_when_duplicate_shape_class_names(self):
        MOCK_LOCUSTFILE_CONTENT_C = MOCK_LOCUSTFILE_CONTENT_A + textwrap.dedent("""
                from locust import LoadTestShape
                class TestShape(LoadTestShape):
                    def tick(self):
                        run_time = self.get_run_time()
                        if run_time < 2:
                            return (10, 1)

                        return None
            """)
        MOCK_LOCUSTFILE_CONTENT_D = MOCK_LOCUSTFILE_CONTENT_B + textwrap.dedent("""
                from locust import LoadTestShape
                class TestShape(LoadTestShape):
                    def tick(self):
                        run_time = self.get_run_time()
                        if run_time < 2:
                            return (10, 1)

                        return None
            """)
        with (
            temporary_file(content=MOCK_LOCUSTFILE_CONTENT_C) as file1,
            temporary_file(content=MOCK_LOCUSTFILE_CONTENT_D) as file2,
        ):
            args = [
                "-f",
                f"{file1},{file2}",
                "--headless",
                "--run-time",
                "5s",
                "-u",
                "1",
                "-r",
                "1",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Duplicate shape classes: TestShape", timeout=5
                ):
                    self.fail("Timeout waiting for duplicate shape class error message.")

                try:
                    manager.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail("Locust process did not terminate as expected.")

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Duplicate shape classes: TestShape", combined_output)
        self.assertEqual(1, manager.process.returncode, "Process did not exit with return code 1 as expected.")

    def test_error_when_providing_both_run_time_and_a_shape_class(self):
        """
        Tests that providing both --run-time and a LoadTestShape class produces appropriate warning messages
        and that the process exits successfully.
        """
        content = MOCK_LOCUSTFILE_CONTENT + textwrap.dedent("""
                from locust import LoadTestShape

                class TestShape(LoadTestShape):
                    def tick(self):
                        return None
            """)

        with mock_locustfile(content=content) as mocked:
            args = [
                "-f",
                mocked.file_path,
                "--run-time=1s",
                "--headless",
                "--exit-code-on-error",
                "0",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.process,
                    manager.output_lines,
                    "--run-time, --users or --spawn-rate have no impact on LoadShapes",
                    timeout=5,
                ):
                    self.fail("Timeout waiting for LoadShapes impact message.")

                if not wait_for_output_condition_non_threading(
                    manager.process,
                    manager.output_lines,
                    "The following option(s) will be ignored: --run-time",
                    timeout=5,
                ):
                    self.fail("Timeout waiting for ignored options message.")

                try:
                    manager.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail("Locust process did not terminate as expected.")

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("--run-time, --users or --spawn-rate have no impact on LoadShapes", combined_output)
        self.assertIn("The following option(s) will be ignored: --run-time", combined_output)
        assert_return_code(self, manager.process.returncode)

    def test_shape_class_log_disabled_parameters(self):
        """
        Tests that providing both --run-time and a LoadTestShape class logs appropriate warning messages
        and that the process exits successfully with return code 0.
        """
        content = MOCK_LOCUSTFILE_CONTENT + textwrap.dedent("""
                from locust import LoadTestShape

                class TestShape(LoadTestShape):
                    def tick(self):
                        return None
            """)

        with mock_locustfile(content=content) as mocked:
            args = [
                "--headless",
                "-f",
                mocked.file_path,
                "--exit-code-on-error=0",
                "--users=1",
                "--spawn-rate=1",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                expected_messages = [
                    "Shape test starting.",
                    "--run-time, --users or --spawn-rate have no impact on LoadShapes",
                    "The following option(s) will be ignored: --users, --spawn-rate",
                ]

                for message in expected_messages:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, message, timeout=5
                    ):
                        self.fail(f"Timeout waiting for message: {message}")

                try:
                    manager.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail("Locust process did not terminate as expected.")

        combined_output = "\n".join(manager.output_lines)

        for message in expected_messages:
            self.assertIn(message, combined_output)

        assert_return_code(self, manager.process.returncode)

    def test_shape_class_with_use_common_options(self):
        """
        Tests that providing both --run-time and a LoadTestShape class with use_common_options=True
        does not produce warnings about ignored options and that the process exits successfully.
        """
        content = MOCK_LOCUSTFILE_CONTENT + textwrap.dedent("""
                from locust import LoadTestShape

                class TestShape(LoadTestShape):
                    use_common_options = True

                    def tick(self):
                        return None
            """)

        with mock_locustfile(content=content) as mocked:
            args = [
                "--headless",
                "-f",
                mocked.file_path,
                "--exit-code-on-error=0",
                "--users=1",
                "--spawn-rate=1",
                "--run-time=1s",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                expected_messages = [
                    "Shape test starting.",
                ]

                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Shape test starting.", timeout=5
                ):
                    self.fail("Timeout waiting for 'Shape test starting.' message.")

                unwanted_messages = [
                    "--run-time, --users or --spawn-rate have no impact on LoadShapes",
                    "The following option(s) will be ignored:",
                ]

                for message in unwanted_messages:
                    if any(message in line for line in manager.output_lines):
                        self.fail(f"Unexpected message found: {message}")

                try:
                    manager.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail("Locust process did not terminate as expected.")

        combined_output = "\n".join(manager.output_lines)

        for message in expected_messages:
            self.assertIn(message, combined_output)

        for message in [
            "--run-time, --users or --spawn-rate have no impact on LoadShapes",
            "The following option(s) will be ignored:",
        ]:
            self.assertNotIn(message, combined_output, f"Unexpected message found: {message}")

        assert_return_code(self, manager.process.returncode)

    def test_error_when_locustfiles_directory_is_empty(self):
        """
        Tests that providing an empty directory for locustfiles results in an appropriate error message and exit code.
        """
        with TemporaryDirectory() as temp_dir:
            args = [
                "-f",
                temp_dir,
                "--headless",
                "--exit-code-on-error=1",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                expected_error_message = f"Could not find any locustfiles in directory '{temp_dir}'"

                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, expected_error_message, timeout=5
                ):
                    self.fail(f"Timeout waiting for error message: {expected_error_message}")

                try:
                    manager.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail("Locust process did not terminate as expected.")

        combined_output = "\n".join(manager.output_lines)

        self.assertIn(expected_error_message, combined_output)
        self.assertEqual(1, manager.process.returncode, "Process did not exit with return code 1 as expected.")

    def test_error_when_no_tasks_match_tags(self):
        """
        Tests that providing tags that do not match any tasks results in appropriate error messages and exit code.
        """
        content = textwrap.dedent("""
            from locust import HttpUser, task, constant, LoadTestShape, tag

            class MyUser(HttpUser):
                host = "http://127.0.0.1:8089"
                wait_time = constant(1)

                @tag("tag1")
                @task
                def task1(self):
                    print("task1")
        """)

        with mock_locustfile(content=content) as mocked:
            args = [
                "locust",
                "-f",
                mocked.file_path,
                "--headless",
                "-t",
                "1",
                "--tags",
                "tag2",
            ]

            with PopenContextManager(args) as manager:
                expected_error_messages = [
                    "MyUser had no tasks left after filtering",
                    "No tasks defined on MyUser",
                ]

                for message in expected_error_messages:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, message, timeout=5
                    ):
                        self.fail(f"Timeout waiting for error message: {message}")

                try:
                    manager.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail("Locust process did not terminate as expected.")

        combined_output = "\n".join(manager.output_lines)

        for message in expected_error_messages:
            self.assertIn(message, combined_output)

        self.assertEqual(1, manager.process.returncode, "Process did not exit with return code 1 as expected.")

    @unittest.skipIf(os.name == "nt", reason="Signal handling on windows is hard")
    def test_graceful_exit_when_keyboard_interrupt(self):
        """
        Tests that Locust exits gracefully when a KeyboardInterrupt (SIGINT) is sent.
        """
        content = textwrap.dedent("""
                from locust import User, events, task, constant, LoadTestShape

                @events.test_stop.add_listener
                def on_test_stop(environment, **kwargs) -> None:
                    print("Test Stopped")

                class LoadTestShape(LoadTestShape):
                    def tick(self):
                        run_time = self.get_run_time()
                        if run_time < 2:
                            return (10, 1)
                        return None

                class TestUser(User):
                    wait_time = constant(3)
                    @task
                    def my_task(self):
                        print("running my_task()")
            """)

        with temporary_file(content=content) as mocked:
            args = [
                "-f",
                mocked,
                "--headless",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Shape test starting", timeout=5
                ):
                    self.fail("Timeout waiting for 'Shape test starting' message.")

                manager.process.send_signal(signal.SIGINT)

                expected_messages = [
                    "Shape test starting",
                    "Exiting due to CTRL+C interruption",
                    "Test Stopped",
                ]

                for message in expected_messages:
                    if not wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, message, timeout=5
                    ):
                        self.fail(f"Timeout waiting for message: {message}")

                try:
                    manager.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.fail("Locust process did not terminate as expected.")

        combined_output = "\n".join(manager.output_lines)

        for message in expected_messages:
            self.assertIn(message, combined_output)

        # Check for the stats printer output using regex
        self.assertRegex(combined_output, r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*")


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
        file_content = textwrap.dedent("""
            from locust import User, task, constant
            class TestUser(User):
                wait_time = constant(1)
                @task
                def my_task(self):
                    print("running my_task()")
        """)

        with mock_locustfile(content=file_content) as mocked:
            args = [
                "-f",
                mocked.file_path,
                "--headless",
                "--master",
                "--expect-workers",
                "2",
                "--expect-workers-max-wait",
                "1",
            ]

            with PopenContextManager(["locust"] + args) as manager:
                self.assertTrue(
                    wait_for_output_condition_non_threading(
                        manager.process,
                        manager.output_lines,
                        "Waiting for workers to be ready, 0 of 2 connected",
                        timeout=5,
                    ),
                    "Timeout waiting for 'Waiting for workers' message",
                )

                self.assertTrue(
                    wait_for_output_condition_non_threading(
                        manager.process, manager.output_lines, "Gave up waiting for workers to connect", timeout=5
                    ),
                    "Timeout waiting for 'Gave up waiting' message",
                )

                combined_output = "\n".join(manager.output_lines)
                self.assertNotIn("Traceback", combined_output)

            self.assertIn(
                manager.process.returncode,
                [1, -15],
                f"Locust process exited with unexpected return code: {manager.process.returncode}",
            )
            self.assertIsNotNone(manager.process.returncode, "Locust process did not terminate")

    def test_distributed_events(self):
        content = (
            MOCK_LOCUSTFILE_CONTENT
            + """
from locust import events
from locust.runners import MasterRunner

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    try:
        if isinstance(environment.runner, MasterRunner):
            print("test_start on master")
        else:
            print("test_start on worker")
    except Exception as e:
        print(f"Error in test_start listener: {e}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    try:
        if isinstance(environment.runner, MasterRunner):
            print("test_stop on master")
        else:
            print("test_stop on worker")
    except Exception as e:
        print(f"Error in test_stop listener: {e}")
"""
        )

        with PopenContextManager(
            args=[
                "locust",
                "--headless",
                "--master",
                "--expect-workers",
                "1",
                "-t",
                "5",
                "--exit-code-on-error",
                "0",
                "-L",
                "DEBUG",
            ],
            file_content=content,
            port=get_free_tcp_port(),
        ) as master_manager:
            with PopenContextManager(
                args=["locust", "--worker", "--exit-code-on-error", "0", "-L", "DEBUG"],
                file_content=content,
            ) as worker_manager:
                master_finished = wait_for_output_condition_non_threading(
                    master_manager.process, master_manager.output_lines, "test_stop on master", timeout=7
                )
                self.assertTrue(master_finished, "Master did not finish as expected.")

                worker_finished = wait_for_output_condition_non_threading(
                    worker_manager.process, worker_manager.output_lines, "test_stop on worker", timeout=7
                )
                self.assertTrue(worker_finished, "Worker did not finish as expected.")

            self.assertIsNotNone(worker_manager.process.returncode, "Worker process did not terminate")

        master_output = "\n".join(master_manager.output_lines)
        worker_output = "\n".join(worker_manager.output_lines)

        self.assertIn("test_start on master", master_output)
        self.assertIn("test_stop on master", master_output)
        self.assertNotIn("Traceback", master_output)

        self.assertIn("test_start on worker", worker_output)
        self.assertIn("test_stop on worker", worker_output)
        self.assertNotIn("Traceback", worker_output)

        print("Master output:\n", master_output)
        print("Worker output:\n", worker_output)
        assert_return_code(self, worker_manager.process.returncode)

        assert_return_code(self, master_manager.process.returncode)

    def test_distributed_tags(self):
        """
        Tests that the master process correctly handles tag filtering,
        ensuring only tasks with specified tags are executed.
        """
        content = textwrap.dedent("""
                from locust import HttpUser, task, between, tag

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
            """)

        with PopenContextManager(
            args=[
                "locust",
                "--headless",
                "--master",
                "--expect-workers",
                "1",
                "-t",
                "5s",
                "-u",
                "2",
                "--exit-code-on-error",
                "0",
                "-L",
                "DEBUG",
                "--tags",
                "tag1",
            ],
            file_content=content,
            port=get_free_tcp_port(),
        ) as master_manager:
            with PopenContextManager(
                args=["locust", "--worker", "-L", "DEBUG"],
                file_content=content,
                port=None,
            ) as worker_manager:
                master_finished = wait_for_output_condition_non_threading(
                    master_manager.process, master_manager.output_lines, "Shutting down", timeout=10
                )
                self.assertTrue(master_finished, "Master did not shut down as expected.")

                worker_finished = wait_for_output_condition_non_threading(
                    worker_manager.process, worker_manager.output_lines, "Shutting down", timeout=10
                )
                self.assertTrue(worker_finished, "Worker did not shut down as expected.")

        master_output = "\n".join(master_manager.output_lines)
        worker_output = "\n".join(worker_manager.output_lines)

        self.assertIn("task1", worker_output, "Expected 'task1' not found in worker output")
        self.assertNotIn("task2", worker_output, "Unexpected 'task2' found in worker output")
        self.assertNotIn("Traceback", master_output, "Traceback found in master stderr/output")
        self.assertNotIn("Traceback", worker_output, "Traceback found in worker stderr/output")

        self.assertIn("task1", worker_output, "Master did not filter tasks correctly; 'task1' should be present")
        self.assertNotIn("task2", worker_output, "Master did not filter tasks correctly; 'task2' should not be present")

        assert_return_code(self, master_manager.process.returncode)
        assert_return_code(self, worker_manager.process.returncode)

    def test_distributed(self):
        """
        Tests the basic distributed Locust setup by spawning a master and a worker.
        Ensures that both processes shut down correctly with the expected exit codes.
        """
        LOCUSTFILE_CONTENT = textwrap.dedent("""
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    pass
        """)

        with PopenContextManager(
            args=[
                "locust",
                "--headless",
                "--master",
                "--expect-workers",
                "1",
                "-u",
                "3",
                "-t",
                "5s",
            ],
            file_content=LOCUSTFILE_CONTENT,
            port=get_free_tcp_port(),
        ) as master_manager:
            with PopenContextManager(
                args=["locust", "--worker"],
                file_content=LOCUSTFILE_CONTENT,
                port=None,
            ) as worker_manager:
                master_finished = wait_for_output_condition_non_threading(
                    master_manager.process,
                    master_manager.output_lines,
                    "Shutting down (exit code 0)",
                    timeout=10,
                )
                self.assertTrue(master_finished, "Master did not shut down as expected.")

                worker_finished = wait_for_output_condition_non_threading(
                    worker_manager.process,
                    worker_manager.output_lines,
                    "Shutting down (exit code 0)",
                    timeout=10,
                )
                self.assertTrue(worker_finished, "Worker did not shut down as expected.")

        master_output = "\n".join(master_manager.output_lines)
        worker_output = "\n".join(worker_manager.output_lines)

        self.assertIn(
            'All users spawned: {"User1": 3} (3 total users)',
            master_output,
            "Expected user spawn message not found in master output.",
        )
        self.assertIn(
            "Shutting down (exit code 0)", master_output, "Expected shutdown message not found in master output."
        )

        self.assertNotIn("Traceback", master_output, "Traceback found in master output.")
        self.assertNotIn("Traceback", worker_output, "Traceback found in worker output.")

        # assert_return_code(self, master_manager.process.returncode)
        # assert_return_code(self, worker_manager.process.returncode)

    def test_distributed_report_timeout_expired(self):
        """
        Tests that the master process correctly handles a timeout when waiting for worker reports
        after spawning users.
        """
        LOCUSTFILE_CONTENT = textwrap.dedent("""
                from locust import User, task, constant

                class User1(User):
                    wait_time = constant(1)

                    @task
                    def t(self):
                        pass
            """)

        env_var_key = "LOCUST_WAIT_FOR_WORKERS_REPORT_AFTER_RAMP_UP"
        env_var_value = "0.01"  # Very short wait time to trigger timeout

        with (
            mock_locustfile(content=LOCUSTFILE_CONTENT),
            patch_env(env_var_key, env_var_value),
        ):
            with PopenContextManager(
                args=[
                    "locust",
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-u",
                    "3",
                    "-t",
                    "5s",
                ],
                file_content=LOCUSTFILE_CONTENT,
                port=get_free_tcp_port(),
            ) as master_manager:
                with PopenContextManager(
                    args=["locust", "--worker"],
                    file_content=LOCUSTFILE_CONTENT,
                    port=None,
                ) as worker_manager:
                    master_finished = wait_for_output_condition_non_threading(
                        master_manager.process,
                        master_manager.output_lines,
                        'Spawning is complete and report waittime is expired, but not all reports received from workers: {"User1": 2} (2 total users)',
                        timeout=10,
                    )
                    self.assertTrue(master_finished, "Master did not report timeout as expected.")

                    shutting_down = wait_for_output_condition_non_threading(
                        master_manager.process, master_manager.output_lines, "Shutting down (exit code 0)", timeout=5
                    )
                    self.assertTrue(shutting_down, "Master did not shut down as expected.")

                    worker_finished = wait_for_output_condition_non_threading(
                        worker_manager.process, worker_manager.output_lines, "Shutting down (exit code 0)", timeout=5
                    )
                    self.assertTrue(worker_finished, "Worker did not shut down as expected.")

        master_output = "\n".join(master_manager.output_lines)
        worker_output = "\n".join(worker_manager.output_lines)

        expected_timeout_message = 'Spawning is complete and report waittime is expired, but not all reports received from workers: {"User1": 2} (2 total users)'
        self.assertIn(expected_timeout_message, master_output, "Expected timeout message not found in master output")
        self.assertIn("Shutting down (exit code 0)", master_output)
        self.assertIn("Shutting down (exit code 0)", worker_output)

        self.assertNotIn("Traceback", master_output, "Traceback found in master output")
        self.assertNotIn("Traceback", worker_output, "Traceback found in worker output")

        assert_return_code(self, master_manager.process.returncode)
        assert_return_code(self, worker_manager.process.returncode)

    def test_locustfile_distribution(self):
        """
        Tests that the Locust master and multiple worker processes correctly distribute users
        and handle shutdown as expected, with exit codes validated based on the operating system.
        """
        LOCUSTFILE_CONTENT = textwrap.dedent("""
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    pass
        """)

        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file.write(LOCUSTFILE_CONTENT)
            temp_file.flush()
            locustfile_path = temp_file.name

        try:
            with PopenContextManager(
                args=[
                    "locust",
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "2",
                    "-t",
                    "5s",
                    "-u",
                    "2",
                ],
                file_content=LOCUSTFILE_CONTENT,
                port=get_free_tcp_port(),
            ) as master_manager:
                with PopenContextManager(
                    args=["locust", "-f", locustfile_path, "--worker"],
                    file_content=LOCUSTFILE_CONTENT,
                    port=None,
                ) as worker_manager1:
                    with PopenContextManager(
                        args=["locust", "-f", locustfile_path, "--worker"],
                        file_content=LOCUSTFILE_CONTENT,
                        port=None,
                    ) as worker_manager2:
                        all_users_spawned = wait_for_output_condition_non_threading(
                            master_manager.process,
                            master_manager.output_lines,
                            'All users spawned: {"User1": 2} (2 total users)',
                            timeout=30,
                        )
                        self.assertTrue(all_users_spawned, "Timeout waiting for all users to be spawned.")
                        shutting_down = wait_for_output_condition_non_threading(
                            master_manager.process,
                            master_manager.output_lines,
                            "Shutting down (exit code 0)",
                            timeout=30,
                        )
                        self.assertTrue(shutting_down, "'Shutting down (exit code 0)' not found in master output.")

            master_output = "\n".join(master_manager.output_lines)
            worker_output1 = "\n".join(worker_manager1.output_lines)
            worker_output2 = "\n".join(worker_manager2.output_lines)
            combined_output = f"{master_output}\n{worker_output1}\n{worker_output2}"

            self.assertIn(
                'All users spawned: {"User1": 2} (2 total users)',
                master_output,
                "Expected user spawn message not found in master output.",
            )
            self.assertIn(
                "Shutting down (exit code 0)",
                combined_output,
                f"'Shutting down (exit code 0)' not found in output:\n{combined_output}",
            )

            self.assertNotIn("Traceback", combined_output, "Traceback found in output, indicating an error.")

            assert_return_code(self, master_manager.process.returncode)
            assert_return_code(self, worker_manager1.process.returncode)
            assert_return_code(self, worker_manager2.process.returncode)

        finally:
            os.remove(locustfile_path)

    def test_distributed_with_locustfile_distribution_not_plain_filename(self):
        """
        Tests distributed Locust setup using a locustfile with a non-plain filename.
        Ensures that both master and worker processes shut down correctly with expected exit codes based on the OS.
        """
        LOCUSTFILE_CONTENT = textwrap.dedent("""
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    print("hello")
        """)

        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file.write(LOCUSTFILE_CONTENT)
            temp_file.flush()
            locustfile_path = temp_file.name

        try:
            with PopenContextManager(
                args=["locust", "-f", locustfile_path, "--worker"],
                port=None,
            ) as worker_manager:
                print(f"DEBUG: Worker started with PID {worker_manager.process.pid}")

                with PopenContextManager(
                    args=[
                        "locust",
                        "-f",
                        locustfile_path,
                        "--headless",
                        "--master",
                        "--expect-workers",
                        "1",
                        "-t",
                        "5s",
                    ],
                    port=get_free_tcp_port(),
                ) as master_manager:
                    worker_connected = wait_for_output_condition_non_threading(
                        master_manager.process, master_manager.output_lines, "1 workers connected", timeout=30
                    )
                    self.assertTrue(worker_connected, "Worker did not connect to master.")

                    all_users_spawned = wait_for_output_condition_non_threading(
                        master_manager.process,
                        master_manager.output_lines,
                        'All users spawned: {"User1": 1} (1 total users)',
                        timeout=30,
                    )
                    self.assertTrue(all_users_spawned, "Timeout waiting for all users to be spawned.")

                    shutting_down = wait_for_output_condition_non_threading(
                        master_manager.process, master_manager.output_lines, "Shutting down (exit code 0)", timeout=30
                    )
                    self.assertTrue(shutting_down, "'Shutting down (exit code 0)' not found in master output.")

            master_output = "\n".join(master_manager.output_lines)
            worker_output = "\n".join(worker_manager.output_lines)
            combined_output = f"{master_output}\n{worker_output}"

            self.assertIn(
                'All users spawned: {"User1": 1} (1 total users)',
                master_output,
                "Expected user spawn message not found in master output.",
            )
            self.assertIn(
                "Shutting down (exit code 0)",
                master_output,
                f"'Shutting down (exit code 0)' not found in master output:\n{master_output}",
            )

            self.assertIn("hello", worker_output, "Expected 'hello' not found in worker output.")

            self.assertNotIn("Traceback", combined_output, "Traceback found in output, indicating an error.")

            assert_return_code(self, master_manager.process.returncode)
            assert_return_code(self, worker_manager.process.returncode)
        finally:
            os.remove(locustfile_path)

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

        with PopenContextManager(
            args=[
                "locust",
                "--host",
                "http://google.com",
                "--headless",
                "-u",
                "1",
                "-t",
                "2s",
                "--json",
            ],
            file_content=LOCUSTFILE_CONTENT,
        ) as manager:
            manager.process.wait()

            output = "\n".join(manager.output_lines)

            json_pattern = re.compile(r"(\[\s*\{.*?\}\s*\])", re.DOTALL)
            match = json_pattern.search(output)
            if match:
                json_output = match.group(1)
                try:
                    data = json.loads(json_output)
                except json.JSONDecodeError:
                    self.fail(f"Trying to parse JSON failed. JSON output was: {json_output}")
            else:
                self.fail(f"Could not find JSON output in process output. Output was: {output}")

            self.assertEqual(0, manager.process.returncode)

            if not data:
                self.fail(f"No data in JSON output: {output}")

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

    def test_worker_indexes(self):
        content = textwrap.dedent("""
            from locust import HttpUser, task, between

            class AnyUser(HttpUser):
                host = "http://127.0.0.1:8089"
                wait_time = between(0, 0.1)

                @task
                def my_task(self):
                    print("worker index:", self.environment.runner.worker_index)
        """)

        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file.write(content)
            temp_file.flush()
            temp_file_path = temp_file.name

        try:
            master_args = [
                "-f",
                temp_file_path,
                "--headless",
                "--master",
                "--expect-workers",
                "2",
                "-t",
                "5s",
                "-u",
                "2",
                "-L",
                "DEBUG",
            ]
            with PopenContextManager(args=["locust"] + master_args) as master_manager:
                master_ready = wait_for_output_condition_non_threading(
                    master_manager.process, master_manager.output_lines, "Waiting for workers to be ready", timeout=10
                )
                self.assertTrue(master_ready, "Master did not start properly")

                worker_args = [
                    "-f",
                    temp_file_path,
                    "--worker",
                    "--master-host",
                    "127.0.0.1",
                    "-L",
                    "DEBUG",
                ]
                with PopenContextManager(args=["locust"] + worker_args) as worker1_manager:
                    with PopenContextManager(args=["locust"] + worker_args) as worker2_manager:
                        workers_ready = wait_for_output_condition_non_threading(
                            master_manager.process, master_manager.output_lines, "Sending spawn jobs", timeout=10
                        )
                        self.assertTrue(workers_ready, "Workers did not connect properly")

                        master_manager.process.wait(timeout=15)
                        self.assertEqual(0, master_manager.process.poll(), "Master process did not exit cleanly")

                        worker1_manager.process.wait(timeout=5)
                        worker2_manager.process.wait(timeout=5)
                        self.assertEqual(0, worker1_manager.process.poll(), "Worker 1 did not exit cleanly")
                        self.assertEqual(0, worker2_manager.process.poll(), "Worker 2 did not exit cleanly")

                        master_output = "\n".join(master_manager.output_lines)
                        worker1_output = "\n".join(worker1_manager.output_lines)
                        worker2_output = "\n".join(worker2_manager.output_lines)

                        self.assertNotIn("Traceback", master_output, "Traceback found in master output")
                        self.assertNotIn("Traceback", worker1_output, "Traceback found in worker 1 output")
                        self.assertNotIn("Traceback", worker2_output, "Traceback found in worker 2 output")

                        def extract_worker_indexes(output):
                            PREFIX = "worker index:"
                            indexes = []
                            for line in output.splitlines():
                                if PREFIX in line:
                                    idx_str = line.split(PREFIX)[-1].strip()
                                    idx = int(idx_str)
                                    indexes.append(idx)
                            return indexes

                        indexes1 = extract_worker_indexes(worker1_output)
                        indexes2 = extract_worker_indexes(worker2_output)

                        found = set(indexes1 + indexes2)
                        expected = {0, 1}
                        self.assertEqual(found, expected, f"Expected worker indexes {expected}, but got {found}")
        finally:
            os.remove(temp_file_path)

    @unittest.skipIf(os.name == "nt", reason="--processes doesn't work on Windows")
    def test_processes(self):
        with mock_locustfile() as mocked:
            args = [
                "locust",
                "-f",
                mocked.file_path,
                "--processes",
                "4",
                "--headless",
                "--run-time",
                "1s",
                "--exit-code-on-error",
                "0",
            ]
            with PopenContextManager(args=args) as manager:
                process_finished = wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Shutting down (exit code 0)", timeout=9
                )
                if not process_finished:
                    manager.process.kill()
                    output = "\n".join(manager.output_lines)
                    print("Process output:\n", output)
                    self.fail(f"Locust process never finished: {' '.join(args)}")
                else:
                    output = "\n".join(manager.output_lines)
                    self.assertNotIn("Traceback", output)
                    self.assertIn("(index 3) reported as ready", output)
                    self.assertIn("Shutting down (exit code 0)", output)

    @unittest.skipIf(os.name == "nt", reason="--processes doesn't work on Windows")
    def test_processes_autodetect(self):
        with mock_locustfile() as mocked:
            args = [
                "locust",
                "-f",
                mocked.file_path,
                "--processes",
                "-1",
                "--headless",
                "--run-time",
                "1s",
                "--exit-code-on-error",
                "0",
            ]
            with PopenContextManager(args=args) as manager:
                process_finished = wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Shutting down (exit code 0)", timeout=9
                )
                if not process_finished:
                    manager.process.kill()
                    output = "\n".join(manager.output_lines)
                    print("Process output:\n", output)
                    self.fail(f"Locust process never finished: {' '.join(args)}")

                else:
                    manager.process.wait(timeout=5)
                    self.assertEqual(0, manager.process.poll(), "Locust process did not exit cleanly")

                    output = "\n".join(manager.output_lines)

                    self.assertNotIn("Traceback", output)
                    self.assertIn("(index 0) reported as ready", output)
                    self.assertIn("Shutting down (exit code 0)", output)

    @unittest.skipIf(os.name == "nt", reason="--processes doesn't work on Windows")
    def test_processes_separate_worker(self):
        with mock_locustfile() as mocked:
            master_args = [
                "locust",
                "-f",
                mocked.file_path,
                "--master",
                "--headless",
                "--run-time",
                "1",
                "--exit-code-on-error",
                "0",
                "--expect-workers-max-wait",
                "2",
            ]
            with PopenContextManager(args=master_args) as master_manager:
                worker_args = [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--processes",
                    "4",
                    "--worker",
                ]
                with PopenContextManager(args=worker_args) as worker_manager:
                    try:
                        worker_manager.process.wait(timeout=9)
                    except subprocess.TimeoutExpired:
                        master_manager.process.kill()
                        worker_manager.process.kill()
                        worker_output = "\n".join(worker_manager.output_lines)
                        master_output = "\n".join(master_manager.output_lines)
                        self.fail(f"Worker never finished: {worker_output}")

                    try:
                        master_manager.process.wait(timeout=9)
                    except subprocess.TimeoutExpired:
                        master_manager.process.kill()
                        worker_manager.process.kill()
                        worker_output = "\n".join(worker_manager.output_lines)
                        master_output = "\n".join(master_manager.output_lines)
                        self.fail(f"Master never finished: {master_output}")

                    worker_output = "\n".join(worker_manager.output_lines)
                    master_output = "\n".join(master_manager.output_lines)

                    self.assertNotIn("Traceback", worker_output, "Traceback found in worker output")
                    self.assertNotIn("Traceback", master_output, "Traceback found in master output")
                    self.assertNotIn(
                        "Gave up waiting for workers to connect",
                        master_output,
                        "Master gave up waiting for workers to connect",
                    )
                    self.assertIn(
                        "(index 3) reported as ready",
                        master_output,
                        "Expected '(index 3) reported as ready' in master output",
                    )
                    self.assertIn(
                        "Shutting down (exit code 0)",
                        master_output,
                        "Expected 'Shutting down (exit code 0)' in master output",
                    )

    @unittest.skipIf(os.name == "nt", reason="--processes doesnt work on windows")
    def test_processes_ctrl_c(self):
        with mock_locustfile() as mocked:
            proc = psutil.Popen(  # use psutil.Popen instead of subprocess.Popen to use extra features
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--processes",
                    "4",
                    "--headless",
                    "-L",
                    "DEBUG",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            gevent.sleep(3)
            children = proc.children(recursive=True)
            self.assertEqual(len(children), 4, "unexpected number of child worker processes")

            proc.send_signal(signal.SIGINT)
            gevent.sleep(2)

            for child in children:
                self.assertFalse(child.is_running(), "child processes failed to terminate")

            try:
                _, stderr = proc.communicate(timeout=5)
            except Exception:
                proc.kill()
                _, stderr = proc.communicate()
                assert False, f"locust process never finished: {stderr}"

            self.assertNotIn("Traceback", stderr)
            self.assertIn("(index 3) reported as ready", stderr)
            self.assertIn("The last worker quit, stopping test", stderr)
            self.assertIn("Shutting down (exit code 0)", stderr)
            # ensure no weird escaping in error report. Not really related to ctrl-c...
            self.assertIn(", 'Connection refused') ", stderr)

    @unittest.skipIf(os.name == "nt", reason="--processes doesn't work on Windows")
    def test_workers_shut_down_if_master_is_gone(self):
        content = textwrap.dedent(
            """
            from locust import HttpUser, task, constant, runners
            runners.MASTER_HEARTBEAT_TIMEOUT = 2  # Reduce heartbeat timeout for quicker test

            class AnyUser(HttpUser):
                host = "http://127.0.0.1:8089"
                wait_time = constant(1)

                @task
                def my_task(self):
                    print("worker index:", self.environment.runner.worker_index)
            """
        )
        with mock_locustfile(content=content) as mocked:
            master_args = [
                "locust",
                "-f",
                mocked.file_path,
                "--master",
                "--headless",
                "--expect-workers",
                "2",
                "-L",
                "DEBUG",
            ]
            with PopenContextManager(args=master_args) as master_manager:
                worker_args = [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--worker",
                    "--processes",
                    "2",
                    "--headless",
                    "-L",
                    "DEBUG",
                ]
                with PopenContextManager(args=worker_args, start_new_session=True) as worker_manager:
                    start_time = time.time()
                    while time.time() - start_time < 30:
                        if any("All users spawned" in line for line in master_manager.output_lines):
                            break
                        if master_manager.process.poll() is not None:
                            break
                        time.sleep(0.1)
                    else:
                        self.fail("Timeout waiting for workers to be ready.")

                    master_manager.process.kill()
                    master_manager.process.wait()

                    start_time = time.time()
                    while time.time() - start_time < 30:
                        if worker_manager.process.poll() is not None:
                            break
                        time.sleep(0.1)
                    else:
                        self.fail("Timeout waiting for workers to shut down.")

                    worker_output = "\n".join(worker_manager.output_lines)

                    self.assertNotIn("Traceback", worker_output, "Traceback found in worker output")
                    self.assertIn(
                        "Didn't get heartbeat from master in over",
                        worker_output,
                        "Expected heartbeat timeout message not found in worker output",
                    )
                    self.assertIn("worker index:", worker_output, "Expected 'worker index:' not found in worker output")

    @unittest.skipIf(os.name == "nt", reason="--processes doesn't work on Windows")
    def test_processes_error_doesnt_blow_up_completely(self):
        with mock_locustfile() as mocked:
            args = [
                "locust",
                "-f",
                mocked.file_path,
                "--processes",
                "4",
                "-L",
                "DEBUG",
                "UserThatDoesntExist",
            ]
            with PopenContextManager(args=args) as manager:
                manager.process.wait()
                stderr_output = "\n".join(manager.output_lines)
                self.assertIn("Unknown User(s): UserThatDoesntExist", stderr_output)
                self.assertEqual(stderr_output.count("Unknown User(s): UserThatDoesntExist"), 5)
                self.assertNotIn("Traceback", stderr_output)

    @unittest.skipIf(os.name == "nt", reason="--processes doesn't work on Windows")
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
            master_args = [
                "locust",
                "-f",
                mocked.file_path,
                "--master",
                "--headless",
                "-t",
                "5s",
            ]
            worker_args = [
                "locust",
                "-f",
                mocked.file_path,
                "--processes",
                "2",
                "--worker",
            ]

            with ExitStack() as stack:
                master_manager = stack.enter_context(PopenContextManager(args=master_args))

                worker_manager = stack.enter_context(PopenContextManager(args=worker_args))

                worker_exited = wait_for_output_condition_non_threading(
                    worker_manager.process,
                    worker_manager.output_lines,
                    "INFO/locust.runners: sys.exit(42) called",
                    timeout=10,
                )
                self.assertTrue(worker_exited, "Worker did not exit as expected")

                master_detected_missing = wait_for_output_condition_non_threading(
                    master_manager.process,
                    master_manager.output_lines,
                    "failed to send heartbeat, setting state to missing",
                    timeout=10,
                )
                self.assertTrue(master_detected_missing, "Master did not detect missing worker")

                master_manager.process.wait(timeout=15)
                worker_manager.process.wait(timeout=5)

                self.assertEqual(
                    worker_manager.process.returncode,
                    42,
                    f"Worker exited with unexpected return code: {worker_manager.process.returncode}",
                )

                self.assertEqual(
                    master_manager.process.returncode,
                    0,
                    f"Master process did not exit cleanly, return code: {master_manager.process.returncode}",
                )

                master_output = "\n".join(master_manager.output_lines)
                worker_output = "\n".join(worker_manager.output_lines)

                self.assertNotIn("Traceback", master_output, "Traceback found in master output")
                self.assertNotIn("Traceback", worker_output, "Traceback found in worker output")

                self.assertIn(
                    "failed to send heartbeat, setting state to missing",
                    master_output,
                    "Master did not log heartbeat timeout",
                )
                self.assertIn(
                    "INFO/locust.runners: sys.exit(42) called", worker_output, "Worker did not log sys.exit(42) call"
                )
