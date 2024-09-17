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
import textwrap
import time
import unittest
from contextlib import contextmanager
from subprocess import DEVNULL, PIPE, STDOUT
from tempfile import NamedTemporaryFile, TemporaryDirectory
from threading import Thread
from typing import IO, Callable, Optional, cast
from unittest import TestCase

import gevent
import psutil
import requests
from gevent.fileobject import FileObject

# from gevent.subprocess import PIPE, Popen
from pyquery import PyQuery as pq
from requests.exceptions import RequestException

from .mock_locustfile import MOCK_LOCUSTFILE_CONTENT, mock_locustfile
from .util import get_free_tcp_port, patch_env, temporary_file

SHORT_SLEEP = 2 if sys.platform == "darwin" else 1  # macOS is slow on GH, give it some extra time


class PollingTimeoutError(Exception):
    """Custom exception for polling timeout."""

    pass


def poll_until(condition_func: Callable[[], bool], timeout: float = 10, sleep_time: float = 0.01) -> None:
    """
    Polls the condition_func at regular intervals until it returns True or timeout is reached.
    Fixed short sleep time ensures faster polling with early exit when condition is met.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return
        time.sleep(sleep_time)

    raise PollingTimeoutError(f"Condition not met within {timeout} seconds")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
            return False
        except OSError:
            return True


def web_interface_ready(host: str, port: int) -> bool:
    try:
        response = requests.get(f"http://{host}:{port}/", timeout=0.1)
        return response.status_code == 200
    except requests.RequestException:
        return False


def all_users_spawned(proc, output):
    if platform.system() == "Windows":
        while True:
            line = proc.stderr.readline()
            if not line:
                break
            output.append(line)
            if "All users spawned" in line:
                return True
    else:
        stderr = proc.stderr
        ready, _, _ = select.select([stderr], [], [], 0.1)
        if ready:
            line = stderr.readline()
            output.append(line)
            if "All users spawned" in line:
                return True
    return False


def read_output(proc: subprocess.Popen) -> list[str]:
    output: list[str] = []

    stdout = cast(IO[str], proc.stdout)

    ready, _, _ = select.select([stdout], [], [], 0.1)
    if ready:
        line = stdout.readline().strip()
        output.append(line)

    return output


def read_nonblocking(proc: subprocess.Popen, output: list[str]) -> bool:
    assert proc.stdout and proc.stderr, "proc.stdout or proc.stderr is None, cannot read from them"

    if platform.system() == "Windows":
        while True:
            stdout_line = proc.stdout.readline()
            if not stdout_line:
                break
            output.append(stdout_line)
            if "All users spawned" in stdout_line:
                return True
            stderr_line = proc.stderr.readline()
            if stderr_line:
                output.append(stderr_line)
    else:
        ready_to_read, _, _ = select.select([proc.stdout, proc.stderr], [], [], 0.1)
        for pipe in ready_to_read:
            pipe_line = pipe.readline()
            output.append(pipe_line)
            if "All users spawned" in pipe_line:
                return True
    return False


def read_output_non_blocking(proc, output_list):
    """
    Reads real-time output from a subprocess in a non-blocking way using gevent.
    :param proc: Subprocess object
    :param output_list: List to store the real-time output.
    """
    while proc.poll() is None:  # Keep reading while the process is still running
        line = proc.stdout.readline()
        if line:
            output_list.append(line)
            print(line.strip())  # Optional: for real-time feedback
        gevent.sleep(0.1)  # Yield control to allow other greenlets to run


def wait_for_output_condition_non_threading(proc, output_lines, condition, timeout=30):
    start_time = time.time()
    while True:
        combined_output = "\n".join(output_lines)
        if condition in combined_output:
            return True
        if time.time() - start_time >= timeout:
            return False
        gevent.sleep(0.1)


class ProcessManager:
    def __init__(self, proc, stdout_reader, stderr_reader, temp_file_path, output_lines):
        self.proc = proc
        self.stdout_reader = stdout_reader
        self.stderr_reader = stderr_reader
        self.temp_file_path = temp_file_path
        self.output_lines = output_lines

    def cleanup(self):
        if self.temp_file_path is not None and os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)


@contextmanager
def run_locust_process(file_content=None, args=None, port=None):
    temp_file_path = None
    locust_command = ["locust"]

    if file_content is not None:
        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_file_path = temp_file.name
        locust_command += ["-f", temp_file_path]

    if args:
        locust_command += args

    if port is not None:
        locust_command += ["--web-port", str(port)]

    proc = subprocess.Popen(
        locust_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )

    output_lines = []

    def read_output(process_stdout):
        for line in iter(process_stdout.readline, ""):
            output_lines.append(line.rstrip("\n"))

    stdout_reader = gevent.spawn(read_output, proc.stdout)
    stderr_reader = gevent.spawn(read_output, proc.stderr)

    manager = ProcessManager(proc, stdout_reader, stderr_reader, temp_file_path, output_lines)

    try:
        yield manager
    finally:
        if manager.proc.poll() is None:
            manager.proc.terminate()
            manager.proc.wait()
        manager.stdout_reader.join()
        manager.stderr_reader.join()
        manager.cleanup()


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
    def test_help_arg(self):
        with run_locust_process(file_content=None, args=["--help"]) as manager:
            manager.proc.wait()

        output = "\n".join(manager.output_lines).strip()

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

        with run_locust_process(
            file_content=file_content, args=["--custom-string-arg", "command_line_value"], port=port
        ) as manager:
            if not wait_for_output_condition_non_threading(
                manager.proc, manager.output_lines, "Starting Locust", timeout=30
            ):
                self.fail("Timeout waiting for Locust to start.")

            if not wait_for_output_condition_non_threading(
                manager.proc, manager.output_lines, "Starting web interface at", timeout=30
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

        with run_locust_process(file_content=file_content, args=[], port=port) as manager:
            if not wait_for_output_condition_non_threading(
                manager.proc, manager.output_lines, "Starting Locust", timeout=30
            ):
                self.fail("Timeout waiting for Locust to start.")

            if not wait_for_output_condition_non_threading(
                manager.proc, manager.output_lines, "Starting web interface at", timeout=30
            ):
                self.fail("Timeout waiting for web interface to start.")

            manager.proc.send_signal(signal.SIGTERM)

            manager.proc.wait(timeout=3)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Shutting down (exit code 42)", combined_output)
        self.assertIn("Exit code in quit event 42", combined_output)
        self.assertEqual(42, manager.proc.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_webserver_multiple_locustfiles(self):
        with (
            mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_A) as mocked1,
            mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_B) as mocked2,
        ):
            port = get_free_tcp_port()
            print(f"Selected free TCP port: {port}")

            args = ["-f", mocked1.file_path, "-f", mocked2.file_path, "--web-port", str(port)]

            with run_locust_process(file_content=None, args=args, port=None) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Starting Locust", timeout=30
                ):
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to start.")

                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Starting web interface at", timeout=30
                ):
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for web interface to start.")

                try:
                    response = requests.get(f"http://localhost:{port}/", timeout=10)
                    self.assertEqual(
                        200, response.status_code, msg=f"Expected status code 200, got {response.status_code}"
                    )
                except requests.exceptions.RequestException as e:
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail(f"Failed to connect to Locust web interface: {e}")

                manager.proc.send_signal(signal.SIGTERM)

                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Shutting down (exit code 0)", timeout=30
                ):
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
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

        self.assertEqual(
            0, manager.proc.returncode, msg=f"Locust process exited with return code {manager.proc.returncode}"
        )

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

        with run_locust_process(file_content=file_content, args=["--autostart"], port=port) as manager:
            if not wait_for_output_condition_non_threading(
                manager.proc, manager.output_lines, "Starting Locust", timeout=30
            ):
                self.fail("Timeout waiting for Locust to start.")

            if not wait_for_output_condition_non_threading(
                manager.proc, manager.output_lines, "Starting web interface at", timeout=30
            ):
                self.fail("Timeout waiting for web interface to start.")

            try:
                response = requests.get(f"http://localhost:{port}/", timeout=10)
                self.assertEqual(200, response.status_code)
            except requests.exceptions.RequestException as e:
                self.fail(f"Failed to connect to Locust web interface: {e}\nLocust output: {manager.output_lines}")

            manager.proc.send_signal(signal.SIGTERM)

            manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Starting web interface at", combined_output)
        self.assertIn("Starting Locust", combined_output)

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

        with run_locust_process(file_content=file_content, args=["--autostart"], port=port) as manager:
            if not wait_for_output_condition_non_threading(
                manager.proc, manager.output_lines, "Starting Locust", timeout=30
            ):
                self.fail("Timeout waiting for Locust to start.")

            if not wait_for_output_condition_non_threading(
                manager.proc, manager.output_lines, "Starting web interface at", timeout=30
            ):
                self.fail("Timeout waiting for web interface to start.")

            response = requests.get(f"http://localhost:{port}/")
            self.assertEqual(200, response.status_code)

            manager.proc.send_signal(signal.SIGTERM)

            manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Starting web interface at", combined_output)
        self.assertIn("Starting Locust", combined_output)

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

        with run_locust_process(file_content=file_content, args=["--autostart"]) as manager:
            if not wait_for_output_condition_non_threading(
                manager.proc, manager.output_lines, "parameter need to be float", timeout=30
            ):
                self.fail("Timeout waiting for invalid percentile error message.")

            manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("parameter need to be float and value between. 0 < percentile < 1 Eg 0.95", combined_output)
        self.assertEqual(1, manager.proc.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_webserver_multiple_locustfiles_in_directory(self):
        """
        Test that Locust can start with multiple Locustfiles located in a directory
        and that the web interface functions correctly.
        """
        with TemporaryDirectory() as temp_dir:
            # Create multiple locustfiles within the temporary directory
            with (
                mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_A, dir=temp_dir),
                mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_B, dir=temp_dir),
            ):
                port = get_free_tcp_port()

                args = ["-f", temp_dir, "--web-port", str(port)]

                with run_locust_process(file_content=None, args=args, port=None) as manager:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, "Starting Locust", timeout=30
                    ):
                        manager.proc.terminate()
                        manager.proc.wait(timeout=5)
                        self.fail("Timeout waiting for Locust to start.")

                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, "Starting web interface at", timeout=30
                    ):
                        manager.proc.terminate()
                        manager.proc.wait(timeout=5)
                        self.fail("Timeout waiting for web interface to start.")

                    try:
                        response = requests.get(f"http://localhost:{port}/", timeout=10)
                        self.assertEqual(
                            200, response.status_code, msg=f"Expected status code 200, got {response.status_code}"
                        )
                    except requests.exceptions.RequestException as e:
                        manager.proc.terminate()
                        manager.proc.wait(timeout=5)
                        self.fail(f"Failed to connect to Locust web interface: {e}")

                    manager.proc.send_signal(signal.SIGTERM)

                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, "Shutting down (exit code 0)", timeout=30
                    ):
                        manager.proc.terminate()
                        manager.proc.wait(timeout=5)
                        self.fail("Timeout waiting for Locust to shut down.")

                    try:
                        manager.proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        manager.proc.terminate()
                        manager.proc.wait(timeout=5)
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

        self.assertEqual(
            0, manager.proc.returncode, msg=f"Locust process exited with return code {manager.proc.returncode}"
        )

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_webserver_multiple_locustfiles_with_shape(self):
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

        with (
            mock_locustfile(content=user_file_content) as mocked1,
            temporary_file(content=shape_file_content) as mocked2,
        ):
            port = get_free_tcp_port()

            args = ["-f", mocked1.file_path, "-f", mocked2, "--web-port", str(port)]

            with run_locust_process(file_content=None, args=args, port=None) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Starting Locust", timeout=30
                ):
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to start.")

                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Starting web interface at", timeout=30
                ):
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for web interface to start.")

                try:
                    response = requests.get(f"http://localhost:{port}/", timeout=10)
                    self.assertEqual(
                        200, response.status_code, msg=f"Expected status code 200, got {response.status_code}"
                    )
                except requests.exceptions.RequestException as e:
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail(f"Failed to connect to Locust web interface: {e}")

                manager.proc.send_signal(signal.SIGTERM)

                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Shutting down (exit code 0)", timeout=30
                ):
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
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

        self.assertEqual(
            0, manager.proc.returncode, msg=f"Locust process exited with return code {manager.proc.returncode}"
        )

    def test_default_headless_spawn_options(self):
        with mock_locustfile() as mocked:
            proc = subprocess.Popen(
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
                    # just to test --stop-timeout argument parsing, doesnt actually validate its function:
                    "--stop-timeout",
                    "1s",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            stdout, stderr = proc.communicate(timeout=4)
            self.assertNotIn("Traceback", stderr)
            self.assertIn('Spawning additional {"UserSubclass": 1} ({"UserSubclass": 0} already running)...', stderr)
            self.assertEqual(0, proc.returncode)

    def test_invalid_stop_timeout_string(self):
        with mock_locustfile() as mocked:
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--host",
                    "https://test.com/",
                    "--stop-timeout",
                    "asdf1",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            _, stderr = proc.communicate()
            self.assertIn("ERROR/locust.main: Valid --stop-timeout formats are", stderr)
            self.assertEqual(1, proc.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_headless_spawn_options_wo_run_time(self):
        """
        Test Locust's headless mode with spawn options without specifying run time.
        Ensures that Locust starts, spawns all users, and shuts down gracefully.
        """
        with mock_locustfile() as mocked:
            args = [
                "-f",
                mocked.file_path,
                "--host",
                "https://test.com/",
                "--headless",
                "--exit-code-on-error",
                "0",
            ]

            with run_locust_process(file_content=None, args=args, port=None) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "All users spawned", timeout=30
                ):
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to spawn all users.")

                manager.proc.send_signal(signal.SIGTERM)

                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Shutting down (exit code 0)", timeout=30
                ):
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Locust process did not terminate gracefully after SIGTERM.")

        combined_output = "\n".join(manager.output_lines)
        print(f"Combined Locust Output:\n{combined_output}")

        self.assertIn("All users spawned", combined_output, msg="Expected 'All users spawned' not found in output.")
        self.assertIn(
            "Shutting down (exit code 0)",
            combined_output,
            msg="Expected 'Shutting down (exit code 0)' not found in output.",
        )
        self.assertEqual(
            0, manager.proc.returncode, msg=f"Locust process exited with return code {manager.proc.returncode}"
        )
        self.assertNotIn(
            "Locust is running with the UserClass Picker Enabled",
            combined_output,
            msg="Unexpected 'UserClass Picker Enabled' message found in output.",
        )
        self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

    @unittest.skipIf(os.name == "nt", reason="Signal handling on windows is hard")
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
                    args = [
                        "-f",
                        temp_dir,
                        "--headless",
                        "-u",
                        "2",
                        "--exit-code-on-error",
                        "0",
                    ]

                    with run_locust_process(file_content=None, args=args, port=None) as manager:
                        if not wait_for_output_condition_non_threading(
                            manager.proc, manager.output_lines, "All users spawned", timeout=30
                        ):
                            manager.proc.terminate()
                            manager.proc.wait(timeout=5)
                            self.fail("Timeout waiting for Locust to spawn all users.")

                        manager.proc.send_signal(signal.SIGTERM)

                        if not wait_for_output_condition_non_threading(
                            manager.proc, manager.output_lines, "Shutting down (exit code 0)", timeout=30
                        ):
                            manager.proc.terminate()
                            manager.proc.wait(timeout=5)
                            self.fail("Timeout waiting for Locust to shut down.")

                        try:
                            manager.proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            manager.proc.terminate()
                            manager.proc.wait(timeout=5)
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
                    self.assertEqual(
                        0,
                        manager.proc.returncode,
                        msg=f"Locust process exited with return code {manager.proc.returncode}.",
                    )
                    self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

    @unittest.skipIf(os.name == "nt", reason="Signal handling on windows is hard")
    def test_default_headless_spawn_options_with_shape(self):
        """
        Test Locust with default headless spawn options and a custom LoadTestShape.
        Ensures that Locust runs the shape and properly shuts down with exit code 0.
        """
        # Define the content for the custom LoadTestShape with a unique class name
        content = MOCK_LOCUSTFILE_CONTENT + textwrap.dedent(
            """
            from locust import LoadTestShape

            class MyLoadTestShape(LoadTestShape):
                def tick(self):
                    run_time = self.get_run_time()
                    if run_time < 2:
                        return (10, 1)  # (users, spawn rate)
                    return None  # Stop the test
            """
        )

        with mock_locustfile(content=content) as mocked:
            args = ["-f", mocked.file_path, "--host", "https://test.com/", "--headless", "--exit-code-on-error", "0"]

            with run_locust_process(file_content=None, args=args, port=None) as manager:
                shape_update_message = "Shape test updating to 10 users at 1.00 spawn rate"
                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, shape_update_message, timeout=10
                ):
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to run the shape test.")

                shutdown_message = "Shutting down (exit code 0)"
                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, shutdown_message, timeout=10
                ):
                    print("Locust output after expected shutdown time:")
                    print("\n".join(manager.output_lines))

                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.proc.terminate()
                    manager.proc.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully after SIGTERM.")

        combined_output = "\n".join(manager.output_lines)

        self.assertIn(shape_update_message, combined_output, msg="Shape test output not found.")
        self.assertRegex(
            combined_output,
            r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*",
            msg="Aggregated output not found before shutdown.",
        )
        self.assertIn(shutdown_message, combined_output, msg="Expected shutdown message not found.")
        self.assertEqual(
            0, manager.proc.returncode, msg=f"Locust process exited with return code {manager.proc.returncode}."
        )
        self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_run_headless_with_multiple_locustfiles_with_shape(self):
        with TemporaryDirectory() as temp_dir:
            with mock_locustfile(
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
                with temporary_file(
                    content=textwrap.dedent("""
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
                    """),
                    dir=temp_dir,
                ) as mocked2:
                    args = [
                        "-f",
                        f"{mocked1.file_path},{mocked2}",
                        "--host",
                        "https://test.com/",
                        "--headless",
                        "--exit-code-on-error",
                        "0",
                    ]

                    with run_locust_process(file_content=None, args=args, port=None) as manager:
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
                                manager.proc, manager.output_lines, message, timeout=10
                            ):
                                print(f"Locust output after expected '{message}' time:")
                                print("\n".join(manager.output_lines))
                                manager.proc.terminate()
                                manager.proc.wait(timeout=5)
                                self.fail(f"Timeout waiting for Locust to output: {message}")

                        try:
                            manager.proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            print("Locust did not terminate within the expected time.")
                            manager.proc.terminate()
                            manager.proc.wait(timeout=10)
                            self.fail("Locust process did not terminate gracefully after SIGTERM.")

                    combined_output = "\n".join(manager.output_lines)

                    self.assertIn("running my_task()", combined_output, msg="TestUser task output not found.")
                    self.assertIn("running my_task() again", combined_output, msg="TestUser2 task output not found.")
                    self.assertRegex(
                        combined_output,
                        r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*",
                        msg="Aggregated output not found before shutdown.",
                    )
                    self.assertEqual(
                        0,
                        manager.proc.returncode,
                        msg=f"Locust process exited with return code {manager.proc.returncode}.",
                    )
                    self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_autostart_wo_run_time(self):
        port = get_free_tcp_port()
        with mock_locustfile() as mocked:
            args = [
                "-f",
                mocked.file_path,
                "--web-port",
                str(port),
                "--autostart",
            ]

            with run_locust_process(file_content=None, args=args, port=port) as manager:
                start_message = "Starting Locust"
                no_run_time_message = "No run time limit set, use CTRL+C to interrupt"

                messages_to_check = [
                    start_message,
                    no_run_time_message,
                ]

                for message in messages_to_check:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, message, timeout=10
                    ):
                        print(f"Locust output after expected '{message}' time:")
                        print("\n".join(manager.output_lines))
                        manager.proc.terminate()
                        manager.proc.wait(timeout=5)
                        self.fail(f"Timeout waiting for Locust to output: {message}")

                response = requests.get(f"http://localhost:{port}/")
                self.assertEqual(200, response.status_code)

                manager.proc.send_signal(signal.SIGTERM)

                shutdown_message = "Shutting down"
                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, shutdown_message, timeout=10
                ):
                    print("Locust output after expected shutdown time:")
                    print("\n".join(manager.output_lines))
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.proc.terminate()
                    manager.proc.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully after SIGTERM.")

            combined_output = "\n".join(manager.output_lines)

            self.assertIn(start_message, combined_output, msg="Start message not found in output.")
            self.assertIn(no_run_time_message, combined_output, msg="No run time message not found in output.")
            self.assertIn(shutdown_message, combined_output, msg="Shutdown message not found in output.")
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

            d = pq(response.content.decode("utf-8"))
            self.assertIn('"state": "running"', str(d), msg="Expected 'running' state not found in response.")

            self.assertEqual(
                0, manager.proc.returncode, msg=f"Locust process exited with return code {manager.proc.returncode}."
            )

    @unittest.skipIf(sys.platform == "darwin", reason="This is too messy on macOS")
    def test_autostart_w_run_time(self):
        port = get_free_tcp_port()
        with mock_locustfile() as mocked:
            args = [
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

            with run_locust_process(file_content=None, args=args, port=port) as manager:
                start_message = "Starting Locust"
                run_time_message = "Run time limit set to 3 seconds"
                shutdown_message = "Shutting down"

                messages_to_check = [
                    start_message,
                    run_time_message,
                ]

                for message in messages_to_check:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, message, timeout=10
                    ):
                        print(f"Locust output after expected '{message}' time:")
                        print("\n".join(manager.output_lines))
                        manager.proc.terminate()
                        manager.proc.wait(timeout=5)
                        self.fail(f"Timeout waiting for Locust to output: {message}")

                response = requests.get(f"http://localhost:{port}/")
                self.assertEqual(200, response.status_code)

                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, shutdown_message, timeout=10
                ):
                    print("Locust output after expected shutdown time:")
                    print("\n".join(manager.output_lines))
                    manager.proc.terminate()
                    manager.proc.wait(timeout=5)
                    self.fail("Timeout waiting for Locust to shut down.")

                try:
                    manager.proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.proc.terminate()
                    manager.proc.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully.")

            combined_output = "\n".join(manager.output_lines)

            self.assertIn(start_message, combined_output, msg="Start message not found in output.")
            self.assertIn(run_time_message, combined_output, msg="Run time message not found in output.")
            self.assertIn(shutdown_message, combined_output, msg="Shutdown message not found in output.")
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

            # Check response content
            d = pq(response.content.decode("utf-8"))
            self.assertIn('"state": "running"', str(d), msg="Expected 'running' state not found in response.")

            self.assertEqual(
                0, manager.proc.returncode, msg=f"Locust process exited with return code {manager.proc.returncode}."
            )

    @unittest.skipIf(os.name == "nt", reason="Signal handling on windows is hard")
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
                    port = get_free_tcp_port()
                    proc = subprocess.Popen(
                        [
                            "locust",
                            "-f",
                            temp_dir,
                            "--autostart",
                            "-u",
                            "2",
                            "--exit-code-on-error",
                            "0",
                            "--web-port",
                            str(port),
                        ],
                        stdout=PIPE,
                        stderr=PIPE,
                        text=True,
                        env=os.environ.copy(),
                    )

                    output = []
                    try:
                        poll_until(lambda: is_port_in_use(port), timeout=10)
                        poll_until(lambda: all_users_spawned(proc, output), timeout=10)

                        proc.send_signal(signal.SIGTERM)

                        stdout, stderr = proc.communicate(timeout=5)
                        output.extend(stdout.splitlines())
                        output.extend(stderr.splitlines())

                        output_text = "\n".join(output)
                        self.assertIn("Starting Locust", output_text)
                        self.assertIn("All users spawned:", output_text)
                        self.assertIn('"TestUser": 1', output_text)
                        self.assertIn('"UserSubclass": 1', output_text)
                        self.assertIn("Shutting down (exit code 0)", output_text)
                        self.assertIn("running my_task()", output_text)
                        self.assertEqual(0, proc.returncode)

                    finally:
                        if proc.poll() is None:
                            proc.terminate()
                            proc.wait(timeout=5)

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
                    if run_time < 2:
                        return (10, 1)

                    return None
            """
            )
        ) as mocked:
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--web-port",
                    str(port),
                    "--autostart",
                    "--autoquit",
                    "3",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )

            poll_until(lambda: web_interface_ready("localhost", port))

            response = requests.get(f"http://localhost:{port}/")
            success = True

            try:
                _, stderr = proc.communicate(timeout=50)
            except subprocess.TimeoutExpired:
                success = False
                proc.send_signal(signal.SIGTERM)
                _, stderr = proc.communicate()

            self.assertIn("Starting Locust", stderr)
            self.assertIn("Shape test starting", stderr)
            self.assertIn("Shutting down ", stderr)
            self.assertIn("autoquit time reached", stderr)
            self.assertEqual(200, response.status_code)
            self.assertTrue(success, "got timeout and had to kill the process")

    def test_autostart_multiple_locustfiles_with_shape(self):
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
                port = get_free_tcp_port()
                proc = subprocess.Popen(
                    [
                        "locust",
                        "-f",
                        f"{mocked1.file_path},{mocked2}",
                        "--web-port",
                        str(port),
                        "--autostart",
                        "--autoquit",
                        "10",
                    ],
                    stdout=PIPE,
                    stderr=PIPE,
                    text=True,
                    env=os.environ.copy(),
                )

                try:
                    poll_until(lambda: web_interface_ready("localhost", port), timeout=60)
                    response = requests.get(f"http://localhost:{port}/")
                    self.assertEqual(200, response.status_code)

                    stdout, stderr = proc.communicate(timeout=50)

                    print("----- Locust STDOUT -----")
                    print(stdout)
                    print("----- Locust STDERR -----")
                    print(stderr)

                    self.assertIn("Starting Locust", stderr)
                    self.assertIn("Shape test starting", stderr)
                    self.assertIn("Shutting down", stderr)
                    self.assertIn("autoquit time reached", stderr)

                    self.assertEqual(0, proc.returncode, f"Process failed with return code {proc.returncode}")

                finally:
                    proc.terminate()
                    proc.wait(timeout=5)

    @unittest.skipIf(platform.system() == "Darwin", reason="Messy on macOS on GH")
    @unittest.skipIf(os.name == "nt", reason="Signal handling on windows is hard")
    def test_web_options(self):
        port = get_free_tcp_port()
        if platform.system() != "Darwin":
            # MacOS only sets up the loopback interface for 127.0.0.1 and not for 127.*.*.*, so we can't test this
            with mock_locustfile() as mocked:
                proc = subprocess.Popen(
                    ["locust", "-f", mocked.file_path, "--web-host", "127.0.0.2", "--web-port", str(port)],
                    stdout=PIPE,
                    stderr=PIPE,
                    env=os.environ.copy(),
                )
                try:
                    poll_until(lambda: web_interface_ready("127.0.0.2", port), timeout=5)

                    response = requests.get(f"http://127.0.0.2:{port}/", timeout=1)
                    self.assertEqual(200, response.status_code)
                finally:
                    proc.terminate()
                    proc.wait(timeout=5)

        with mock_locustfile() as mocked:
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--web-host",
                    "*",
                    "--web-port",
                    str(port),
                ],
                stdout=PIPE,
                stderr=PIPE,
                env=os.environ.copy(),
            )
            try:
                poll_until(lambda: web_interface_ready("127.0.0.1", port), timeout=5)

                response = requests.get(f"http://127.0.0.1:{port}/", timeout=1)
                self.assertEqual(200, response.status_code)
            finally:
                proc.terminate()
                proc.wait(timeout=5)

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
        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            proc = subprocess.Popen(
                " ".join(
                    [
                        "locust",
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
                ),
                stderr=STDOUT,
                stdout=PIPE,
                shell=True,
                text=True,
                env=os.environ.copy(),
            )

            output = proc.communicate()[0]
            self.assertIn("Ramping to 10 users at a rate of 10.00 per second", output)
            self.assertIn('All users spawned: {"User1": 2, "User2": 4, "User3": 4} (10 total users)', output)
            self.assertIn("Test task is running", output)
            # ensure stats printer printed at least one report before shutting down and that there was a final report printed as well
            self.assertRegex(output, r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*")
            self.assertIn("Shutting down (exit code 0)", output)
            self.assertEqual(0, proc.returncode)

    def test_spawing_with_fixed_multiple_locustfiles(self):
        with mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_A) as mocked1:
            with mock_locustfile(content=MOCK_LOCUSTFILE_CONTENT_B) as mocked2:
                proc = subprocess.Popen(
                    " ".join(
                        [
                            "locust",
                            "-f",
                            f"{mocked1.file_path},{mocked2.file_path}",
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
                    ),
                    stderr=STDOUT,
                    stdout=PIPE,
                    shell=True,
                    text=True,
                    env=os.environ.copy(),
                )

                output = proc.communicate()[0]
                self.assertIn("Ramping to 10 users at a rate of 10.00 per second", output)
                self.assertIn('All users spawned: {"TestUser1": 5, "TestUser2": 5} (10 total users)', output)
                self.assertIn("running my_task()", output)
                # ensure stats printer printed at least one report before shutting down and that there was a final report printed as well
                self.assertRegex(output, r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*")
                self.assertIn("Shutting down (exit code 0)", output)
                self.assertEqual(0, proc.returncode)

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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "--run-time",
                    "1s",
                    "-u",
                    "3",
                ],
                stderr=STDOUT,
                stdout=PIPE,
                text=True,
                env=os.environ.copy(),
            )

            output = proc.communicate()[0]
            self.assertIn("Total fixed_count of User classes (4) is greater than ", output)

    def test_with_package_as_locustfile(self):
        with TemporaryDirectory() as temp_dir:
            with open(f"{temp_dir}/__init__.py", mode="w"):
                with mock_locustfile(dir=temp_dir):
                    proc = subprocess.Popen(
                        [
                            "locust",
                            "-f",
                            temp_dir,
                            "--headless",
                            "--exit-code-on-error",
                            "0",
                            "--run-time",
                            "2",
                        ],
                        stdout=PIPE,
                        stderr=PIPE,
                        text=True,
                        env=os.environ.copy(),
                    )
                    _, stderr = proc.communicate()
                    self.assertIn("Starting Locust", stderr)
                    self.assertIn("All users spawned:", stderr)
                    self.assertIn('"UserSubclass": 1', stderr)
                    self.assertIn("Shutting down (exit code 0)", stderr)
                    self.assertEqual(0, proc.returncode)

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
            proc = subprocess.Popen(
                " ".join(
                    [
                        "locust",
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
                ),
                stderr=STDOUT,
                stdout=PIPE,
                shell=True,
                text=True,
                env=os.environ.copy(),
            )

            output = proc.communicate()[0]
            self.assertNotIn("User1 is running", output)
            self.assertIn("User2 is running", output)
            self.assertIn("User3 is running", output)
            self.assertEqual(0, proc.returncode)

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

    @unittest.skipIf(os.name == "nt", reason="Signal handling on windows is hard")
    def test_run_with_userclass_picker(self):
        with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_A) as file1:
            with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_B) as file2:
                port = get_free_tcp_port()
                proc = subprocess.Popen(
                    ["locust", "-f", f"{file1},{file2}", "--class-picker", "--web-port", str(port)],
                    stdout=PIPE,
                    stderr=PIPE,
                    text=True,
                    env=os.environ.copy(),
                )

                poll_until(lambda: is_port_in_use(port), timeout=20)

                proc.send_signal(signal.SIGTERM)
                _, stderr = proc.communicate()

                self.assertIn("Locust is running with the UserClass Picker Enabled", stderr)
                self.assertIn("Starting Locust", stderr)
                self.assertIn("Starting web interface at", stderr)

                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)

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
                proc = subprocess.Popen(
                    ["locust", "-f", f"{file1},{file2}"], stdout=PIPE, stderr=PIPE, text=True, env=os.environ.copy()
                )

                _, stderr = proc.communicate(timeout=5)
                self.assertIn("Duplicate user class names: TestUser1 is defined", stderr)
                self.assertEqual(1, proc.returncode)

                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)

    def test_no_error_when_same_userclass_in_two_files(self):
        with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_A) as file1:
            MOCK_LOCUSTFILE_CONTENT_C = textwrap.dedent(
                f"""
                from {os.path.basename(file1)[:-3]} import TestUser1
            """
            )
            print(MOCK_LOCUSTFILE_CONTENT_C)
            with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_C) as file2:
                proc = subprocess.Popen(
                    ["locust", "-f", f"{file1},{file2}", "-t", "1", "--headless"],
                    stdout=PIPE,
                    stderr=PIPE,
                    text=True,
                    env=os.environ.copy(),
                )

                stdout, _ = proc.communicate(timeout=50)

                self.assertIn("running my_task", stdout)
                self.assertEqual(0, proc.returncode)

                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()

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
                proc = subprocess.Popen(
                    ["locust", "-f", f"{file1},{file2}"], stdout=PIPE, stderr=PIPE, text=True, env=os.environ.copy()
                )

                _, stderr = proc.communicate(timeout=5)

                self.assertIn("Duplicate shape classes: TestShape", stderr)
                self.assertEqual(1, proc.returncode)

                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()

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
            out = self.assert_run(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--run-time=1s",
                    "--headless",
                    "--exit-code-on-error",
                    "0",
                ]
            )

            self.assertIn("--run-time, --users or --spawn-rate have no impact on LoadShapes", out.stderr)
            self.assertIn("The following option(s) will be ignored: --run-time", out.stderr)

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
            out = self.assert_run(
                [
                    "locust",
                    "--headless",
                    "-f",
                    mocked.file_path,
                    "--exit-code-on-error=0",
                    "--users=1",
                    "--spawn-rate=1",
                ]
            )
            self.assertIn("Shape test starting.", out.stderr)
            self.assertIn("--run-time, --users or --spawn-rate have no impact on LoadShapes", out.stderr)
            self.assertIn("The following option(s) will be ignored: --users, --spawn-rate", out.stderr)

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
            out = self.assert_run(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--run-time=1s",
                    "--users=1",
                    "--spawn-rate=1",
                    "--headless",
                    "--exit-code-on-error=0",
                ]
            )
            self.assertIn("Shape test starting.", out.stderr)
            self.assertNotIn("--run-time, --users or --spawn-rate have no impact on LoadShapes", out.stderr)
            self.assertNotIn("The following option(s) will be ignored:", out.stderr)

    def test_error_when_locustfiles_directory_is_empty(self):
        with TemporaryDirectory() as temp_dir:
            proc = subprocess.Popen(
                ["locust", "-f", temp_dir],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )

            _, stderr = proc.communicate(timeout=5)

            self.assertIn(f"Could not find any locustfiles in directory '{temp_dir}'", stderr)
            self.assertEqual(1, proc.returncode)

            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()

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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "-t",
                    "1",
                    "--tags",
                    "tag2",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            _, stderr = proc.communicate()
            self.assertIn("MyUser had no tasks left after filtering", stderr)
            self.assertIn("No tasks defined on MyUser", stderr)
            self.assertEqual(1, proc.returncode)

    @unittest.skipIf(os.name == "nt", reason="Signal handling on windows is hard")
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
                        if run_time < 2:
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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked,
                    "--headless",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            gevent.sleep(1.9)
            proc.send_signal(signal.SIGINT)
            stdout, stderr = proc.communicate()
            print(stderr, stdout)
            self.assertIn("Shape test starting", stderr)
            self.assertIn("Exiting due to CTRL+C interruption", stderr)
            self.assertIn("Test Stopped", stdout)
            # ensure stats printer printed at least one report before shutting down and that there was a final report printed as well
            self.assertRegex(stderr, r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*")


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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "2",
                    "--expect-workers-max-wait",
                    "1",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )

            def check_output():
                return proc.stderr.readline().strip()

            output = ""
            start_time = time.time()

            while time.time() - start_time < 3:
                line = check_output()
                if line:
                    output += line + "\n"
                    if "Gave up waiting for workers to connect" in line:
                        break

            proc_returncode = proc.wait(timeout=3)

            self.assertTrue(
                "Waiting for workers to be ready, 0 of 2 connected" in output
                and "Gave up waiting for workers to connect" in output,
                f"Expected output not found. Actual output: {output}",
            )
            self.assertNotIn("Traceback", output)
            self.assertEqual(1, proc_returncode, "Locust process did not exit with the expected return code")

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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-t",
                    "1",
                    "--exit-code-on-error",
                    "0",
                    "-L",
                    "DEBUG",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            proc_worker = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--worker",
                    "-L",
                    "DEBUG",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate()
            stdout_worker, stderr_worker = proc_worker.communicate()
            self.assertIn("test_start on master", stdout)
            self.assertIn("test_stop on master", stdout)
            self.assertIn("test_stop on worker", stdout_worker)
            self.assertIn("test_start on worker", stdout_worker)
            self.assertNotIn("Traceback", stderr)
            self.assertNotIn("Traceback", stderr_worker)
            self.assertEqual(0, proc.returncode)
            self.assertEqual(0, proc_worker.returncode)

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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-t",
                    "1",
                    "-u",
                    "2",
                    "--exit-code-on-error",
                    "0",
                    "-L",
                    "DEBUG",
                    "--tags",
                    "tag1",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            proc_worker = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--worker",
                    "-L",
                    "DEBUG",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            stdout, stderr = proc.communicate()
            stdout_worker, stderr_worker = proc_worker.communicate()
            self.assertNotIn("ERROR", stderr_worker)
            self.assertIn("task1", stdout_worker)
            self.assertNotIn("task2", stdout_worker)
            self.assertNotIn("Traceback", stderr)
            self.assertNotIn("Traceback", stderr_worker)
            self.assertEqual(0, proc.returncode)
            self.assertEqual(0, proc_worker.returncode)

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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-u",
                    "3",
                    "-t",
                    "5s",
                ],
                stderr=STDOUT,
                stdout=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            proc_worker = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--worker",
                ],
                stderr=STDOUT,
                stdout=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            try:
                stdout = proc.communicate(timeout=9)[0]
            except Exception:
                proc.kill()
                proc_worker.kill()
                stdout = proc.communicate()[0]
                worker_stdout = proc_worker.communicate()[0]
                assert False, f"master never finished: {stdout}, worker output: {worker_stdout}"
            stdout = proc.communicate()[0]
            proc_worker.communicate()

            self.assertIn('All users spawned: {"User1": 3} (3 total users)', stdout)
            self.assertIn("Shutting down (exit code 0)", stdout)

            self.assertEqual(0, proc.returncode)
            self.assertEqual(0, proc_worker.returncode)

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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-u",
                    "3",
                    "-t",
                    "5s",
                ],
                stderr=STDOUT,
                stdout=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            proc_worker = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--worker",
                ],
                stderr=STDOUT,
                stdout=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            stdout = proc.communicate()[0]
            proc_worker.communicate()

            self.assertIn(
                'Spawning is complete and report waittime is expired, but not all reports received from workers: {"User1": 2} (2 total users)',
                stdout,
            )
            self.assertIn("Shutting down (exit code 0)", stdout)

            self.assertEqual(0, proc.returncode)
            self.assertEqual(0, proc_worker.returncode)

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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "2",
                    "-t",
                    "5s",
                ],
                stderr=PIPE,
                stdout=PIPE,
                text=True,
                bufsize=1,
                env=os.environ.copy(),
            )
            proc_worker = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    "-",
                    "--worker",
                ],
                stderr=PIPE,
                stdout=PIPE,
                text=True,
                bufsize=1,
                env=os.environ.copy(),
            )
            proc_worker2 = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    "-",
                    "--worker",
                ],
                stderr=PIPE,
                stdout=PIPE,
                text=True,
                bufsize=1,
                env=os.environ.copy(),
            )

            output = []

            poll_until(lambda: all_users_spawned(proc, output), timeout=30)

            stdout, stderr = proc.communicate(timeout=30)
            stdout_worker, stderr_worker = proc_worker.communicate(timeout=10)
            stdout_worker2, stderr_worker2 = proc_worker2.communicate(timeout=10)

            output.extend(stdout.splitlines())
            output.extend(stderr.splitlines())
            output.extend(stdout_worker.splitlines())
            output.extend(stderr_worker.splitlines())
            output.extend(stdout_worker2.splitlines())
            output.extend(stderr_worker2.splitlines())

            self.assertTrue(
                any("Shutting down" in line for line in output),
                f"'Shutting down' not found in output:\n{''.join(output)}",
            )
            self.assertIn('All users spawned: {"User1": 1} (1 total users)', "\n".join(output))
            self.assertNotIn("Traceback", "\n".join(output))

            self.assertEqual(0, proc.returncode)
            self.assertEqual(0, proc_worker.returncode)
            self.assertEqual(0, proc_worker2.returncode)

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
            proc_worker = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    "-",
                    "--worker",
                ],
                stderr=STDOUT,
                stdout=PIPE,
                text=True,
            )
            gevent.sleep(2)
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-t",
                    "1",
                ],
                stderr=STDOUT,
                stdout=PIPE,
                text=True,
            )

            stdout = proc.communicate()[0]
            worker_stdout = proc_worker.communicate()[0]

            self.assertIn('All users spawned: {"User1": ', stdout)
            self.assertIn("Shutting down (exit code 0)", stdout)

            self.assertEqual(0, proc.returncode)
            self.assertEqual(0, proc_worker.returncode)
            self.assertIn("hello", worker_stdout)

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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    f"{mocked.file_path},{mocked.file_path}",
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-t",
                    "3s",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=os.environ.copy(),
            )

            proc_worker = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    "-",
                    "--worker",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            output_master = []
            output_worker = []

            poll_until(lambda: all_users_spawned(proc, output_master), timeout=20)

            end_time = time.time() + 15
            while time.time() < end_time:
                read_nonblocking(proc, output_master)
                read_nonblocking(proc_worker, output_worker)

                if "Shutting down" in "\n".join(output_master) or "Shutting down" in "\n".join(output_worker):
                    break

                time.sleep(0.1)

            stdout_master, stderr_master = proc.communicate(timeout=20)
            stdout_worker, stderr_worker = proc_worker.communicate(timeout=5)

            output_master.extend(stdout_master.splitlines())
            output_master.extend(stderr_master.splitlines())

            output_worker.extend(stdout_worker.splitlines())
            output_worker.extend(stderr_worker.splitlines())

            self.assertTrue(
                any("Shutting down" in line for line in output_master),
                f"'Shutting down' not found in master output:\n{''.join(output_master)}",
            )
            self.assertNotIn("Traceback", "\n".join(output_master))
            self.assertEqual(0, proc.returncode)

            self.assertNotIn("Traceback", "\n".join(output_worker))
            self.assertEqual(0, proc_worker.returncode)

            for p in [proc, proc_worker]:
                if p.poll() is None:
                    p.terminate()
                    try:
                        p.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        p.wait()

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
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--host",
                    "http://google.com",
                    "--headless",
                    "-u",
                    "1",
                    "-t",
                    "2s",
                    "--json",
                ],
                stderr=PIPE,
                stdout=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            stdout, stderr = proc.communicate()

            try:
                data = json.loads(stdout)
            except json.JSONDecodeError:
                self.fail(f"Trying to parse {stdout} as json failed")

            self.assertEqual(0, proc.returncode)

            if not data:
                self.fail(f"No data in json: {stdout}, stderr: {stderr}")

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
            master = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "2",
                    "-t",
                    "5",
                    "-u",
                    "2",
                    "-L",
                    "DEBUG",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            proc_worker_1 = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--worker",
                    "-L",
                    "DEBUG",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            proc_worker_2 = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--worker",
                    "-L",
                    "DEBUG",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            stdout, stderr = master.communicate()
            self.assertNotIn("Traceback", stderr)
            self.assertIn("Shutting down (exit code 0)", stderr)
            self.assertEqual(0, master.returncode)

            stdout_worker_1, stderr_worker_1 = proc_worker_1.communicate()
            stdout_worker_2, stderr_worker_2 = proc_worker_2.communicate()
            self.assertEqual(0, proc_worker_1.returncode)
            self.assertEqual(0, proc_worker_2.returncode)
            self.assertNotIn("Traceback", stderr_worker_1)
            self.assertNotIn("Traceback", stderr_worker_2)

            PREFIX = "worker index: "
            p1 = stdout_worker_1.find(PREFIX)
            if p1 == -1:
                raise Exception(stdout_worker_1 + stderr_worker_1)
            self.assertNotEqual(-1, p1)
            p2 = stdout_worker_2.find(PREFIX)
            if p2 == -1:
                raise Exception(stdout_worker_2 + stderr_worker_2)
            self.assertNotEqual(-1, p2)
            found = [
                int(stdout_worker_1[p1 + len(PREFIX) :].split("\n")[0]),
                int(stdout_worker_2[p1 + len(PREFIX) :].split("\n")[0]),
            ]
            found.sort()
            for i in range(2):
                if found[i] != i:
                    raise Exception(f"expected index {i} but got", found[i])

    @unittest.skipIf(os.name == "nt", reason="--processes doesnt work on windows")
    def test_processes(self):
        with mock_locustfile() as mocked:
            command = f"locust -f {mocked.file_path} --processes 4 --headless --run-time 1 --exit-code-on-error 0"
            proc = subprocess.Popen(
                command,
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            try:
                _, stderr = proc.communicate(timeout=9)
            except Exception:
                proc.kill()
                assert False, f"locust process never finished: {command}"
            self.assertNotIn("Traceback", stderr)
            self.assertIn("(index 3) reported as ready", stderr)
            self.assertIn("Shutting down (exit code 0)", stderr)

    @unittest.skipIf(os.name == "nt", reason="--processes doesnt work on windows")
    def test_processes_autodetect(self):
        with mock_locustfile() as mocked:
            command = f"locust -f {mocked.file_path} --processes -1 --headless --run-time 1 --exit-code-on-error 0"
            proc = subprocess.Popen(
                command,
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            try:
                _, stderr = proc.communicate(timeout=9)
            except Exception:
                proc.kill()
                assert False, f"locust process never finished: {command}"
            self.assertNotIn("Traceback", stderr)
            self.assertIn("(index 0) reported as ready", stderr)
            self.assertIn("Shutting down (exit code 0)", stderr)

    @unittest.skipIf(os.name == "nt", reason="--processes doesnt work on windows")
    def test_processes_separate_worker(self):
        with mock_locustfile() as mocked:
            master_proc = subprocess.Popen(
                f"locust -f {mocked.file_path} --master --headless --run-time 1 --exit-code-on-error 0 --expect-workers-max-wait 2",
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )

            worker_parent_proc = subprocess.Popen(
                f"locust -f {mocked.file_path} --processes 4 --worker",
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )

            try:
                _, worker_stderr = worker_parent_proc.communicate(timeout=9)
            except Exception:
                master_proc.kill()
                worker_parent_proc.kill()
                _, worker_stderr = worker_parent_proc.communicate()
                _, master_stderr = master_proc.communicate()
                assert False, f"worker never finished: {worker_stderr}"

            try:
                _, master_stderr = master_proc.communicate(timeout=9)
            except Exception:
                master_proc.kill()
                worker_parent_proc.kill()
                _, worker_stderr = worker_parent_proc.communicate()
                _, master_stderr = master_proc.communicate()
                assert False, f"master never finished: {master_stderr}"

            _, worker_stderr = worker_parent_proc.communicate()
            _, master_stderr = master_proc.communicate()
            self.assertNotIn("Traceback", worker_stderr)
            self.assertNotIn("Traceback", master_stderr)
            self.assertNotIn("Gave up waiting for workers to connect", master_stderr)
            self.assertIn("(index 3) reported as ready", master_stderr)
            self.assertIn("Shutting down (exit code 0)", master_stderr)

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
            master_proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--master",
                    "--headless",
                    "--expect-workers",
                    "2",
                    "-L",
                    "DEBUG",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=os.environ.copy(),
            )

            worker_parent_proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--worker",
                    "--processes",
                    "2",
                    "--headless",
                    "-L",
                    "DEBUG",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                start_new_session=True,
                env=os.environ.copy(),
            )

            try:
                output_master = []
                output_worker = []

                def read_output(proc, output_list, proc_name):
                    while True:
                        line = proc.stdout.readline()
                        if not line:
                            if proc.poll() is not None:
                                break
                            else:
                                continue
                        output_list.append(line)
                        print(f"{proc_name}: {line.strip()}")

                master_thread = Thread(target=read_output, args=(master_proc, output_master, "MASTER"))
                worker_thread = Thread(target=read_output, args=(worker_parent_proc, output_worker, "WORKER"))
                master_thread.start()
                worker_thread.start()

                start_time = time.time()
                while time.time() - start_time < 30:
                    if any("All users spawned" in line for line in output_master):
                        break
                    if master_proc.poll() is not None:
                        break
                    time.sleep(0.1)
                else:
                    self.fail("Timeout waiting for workers to be ready.")

                master_proc.kill()
                master_proc.wait()

                start_time = time.time()
                while time.time() - start_time < 30:
                    if worker_parent_proc.poll() is not None:
                        break
                    time.sleep(0.1)
                else:
                    self.fail("Timeout waiting for workers to shut down.")

                master_thread.join(timeout=5)
                worker_thread.join(timeout=5)

                worker_output = "".join(output_worker)

                self.assertNotIn("Traceback", worker_output)
                self.assertIn("Didn't get heartbeat from master in over", worker_output)
                self.assertIn("worker index:", worker_output)

            finally:
                for proc in [master_proc, worker_parent_proc]:
                    if proc.poll() is None:
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            proc.wait()

    @unittest.skipIf(os.name == "nt", reason="--processes doesnt work on windows")
    def test_processes_error_doesnt_blow_up_completely(self):
        with mock_locustfile() as mocked:
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--processes",
                    "4",
                    "-L",
                    "DEBUG",
                    "UserThatDoesntExist",
                ],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            _, stderr = proc.communicate()
            self.assertIn("Unknown User(s): UserThatDoesntExist", stderr)
            # the error message should repeat 4 times for the workers and once for the master
            self.assertEqual(stderr.count("Unknown User(s): UserThatDoesntExist"), 5)
            self.assertNotIn("Traceback", stderr)

    @unittest.skipIf(os.name == "nt", reason="--processes doesnt work on windows")
    # @unittest.skipIf(sys.platform == "darwin", reason="Flaky on macOS :-/")
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
            worker_proc = subprocess.Popen(
                ["locust", "-f", mocked.file_path, "--processes", "2", "--worker"],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            master_proc = subprocess.Popen(
                ["locust", "-f", mocked.file_path, "--master", "--headless", "-t", "5"],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                env=os.environ.copy(),
            )
            try:
                poll_until(lambda: worker_proc.poll() is not None, timeout=5)
                status_code = worker_proc.returncode
                _, worker_stderr = worker_proc.communicate()

                master_stderr = ""

                def master_detected_missing_worker():
                    nonlocal master_stderr
                    new_stderr = master_proc.stderr.read()
                    master_stderr += new_stderr
                    return "failed to send heartbeat, setting state to missing" in new_stderr

                poll_until(master_detected_missing_worker, timeout=5)

            finally:
                master_proc.kill()
                _, additional_stderr = master_proc.communicate()
                master_stderr += additional_stderr

            self.assertNotIn("Traceback", worker_stderr)
            self.assertIn("INFO/locust.runners: sys.exit(42) called", worker_stderr)
            self.assertEqual(status_code, 42)
            self.assertNotIn("Traceback", master_stderr)
            self.assertIn("failed to send heartbeat, setting state to missing", master_stderr)
