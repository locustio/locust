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


def wait_for_locust_to_start(port, max_retries=10, retry_delay=2):
    for attempt in range(max_retries):
        try:
            response = requests.get(f"http://localhost:{port}/", timeout=10)
            if response.status_code == 200:
                return True
        except requests.RequestException as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            time.sleep(retry_delay)
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


class PopenContextManager:
    def __init__(self, args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.process = None
        self.output_lines = []

    def __enter__(self):
        self.process = subprocess.Popen(
            self.args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
            **self.kwargs,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )

        self.stdout_reader = gevent.spawn(self._read_output, self.process.stdout)
        self.stderr_reader = gevent.spawn(self._read_output, self.process.stderr)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
        self.stdout_reader.join()
        self.stderr_reader.join()

    def _read_output(self, pipe):
        for line in iter(pipe.readline, ""):
            self.output_lines.append(line.rstrip("\n"))


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
    @contextmanager
    def create_temp_locustfile(self, content, dir=None):
        """
        Create a temporary Locustfile with the specified content.

        :param content: The Python code to write into the Locustfile.
        :param dir: Directory where the file should be created. Defaults to system temp directory.
        :yield: The path to the created Locustfile.
        """
        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py", dir=dir) as temp_file:
            temp_file.write(content)
            temp_file.flush()
            yield temp_file.name
        os.unlink(temp_file.name)

    def launch_locust(self, args, timeout_start=30, timeout_shutdown=30):
        """
        Launch the Locust subprocess with the given arguments and wait for it to start.

        :param args: List of command-line arguments to launch Locust.
        :param timeout_start: Time in seconds to wait for Locust to start.
        :param timeout_shutdown: Time in seconds to wait for Locust to shut down.
        :return: PopenContextManager instance.
        """
        manager = PopenContextManager(args)
        manager.__enter__()

        # Wait for Locust to start
        self.wait_for_output(manager, "Starting Locust", timeout=timeout_start)
        self.wait_for_output(manager, "Starting web interface at", timeout=timeout_start)

        return manager

    def wait_for_output(self, manager, condition, timeout=30):
        """
        Wait for a specific condition in the subprocess output.

        :param manager: The PopenContextManager instance.
        :param condition: The string to wait for in the output.
        :param timeout: Maximum time to wait in seconds.
        :raises AssertionError: If the condition is not met within the timeout.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if any(condition in line for line in manager.output_lines):
                return
            if manager.process.poll() is not None:
                break
            time.sleep(0.5)
        # If condition not met, terminate the process and fail the test
        manager.process.terminate()
        try:
            manager.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            manager.process.kill()
            manager.process.wait()
        self.fail(f"Timeout waiting for condition '{condition}'.")

    def terminate_locust(self, manager, shutdown_message="Shutting down (exit code 0)", timeout=30):
        """
        Gracefully terminate the Locust subprocess and wait for shutdown confirmation.

        :param manager: The PopenContextManager instance.
        :param shutdown_message: The shutdown message to wait for in the output.
        :param timeout: Maximum time to wait in seconds for shutdown.
        """
        # Send SIGTERM to gracefully shut down Locust
        manager.process.send_signal(signal.SIGTERM)

        # Wait for shutdown message
        self.wait_for_output(manager, shutdown_message, timeout=timeout)

        # Wait for the process to terminate
        try:
            manager.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            manager.process.terminate()
            manager.process.wait(timeout=5)
            self.fail("Locust process did not terminate gracefully after SIGTERM.")

    def make_http_request(self, port, method="GET", path="/", data=None, timeout=10):
        """
        Make an HTTP request to the Locust web interface.

        :param port: Port number where Locust web interface is running.
        :param method: HTTP method ("GET" or "POST").
        :param path: URL path.
        :param data: Data to send in the request (for POST).
        :param timeout: Timeout for the HTTP request in seconds.
        :return: Response object.
        :raises requests.exceptions.RequestException: If the request fails.
        """
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

        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_file_path = temp_file.name

        try:
            args = [
                sys.executable,
                "-m",
                "locust",
                "-f",
                temp_file_path,
                "--custom-string-arg",
                "command_line_value",
                "--web-port",
                str(port),
            ]

            with PopenContextManager(args) as manager:
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
        finally:
            os.unlink(temp_file_path)

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

        with NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_file_path = temp_file.name

        try:
            args = [sys.executable, "-m", "locust", "-f", temp_file_path, "--web-port", str(port)]

            with PopenContextManager(args) as manager:
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
        finally:
            os.unlink(temp_file_path)

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

            # Perform assertions
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
                0,
                manager.process.returncode,
                msg=f"Locust process exited with return code {manager.process.returncode}",
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
                try:
                    popen_ctx.process.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    print("Process timed out")

                all_output = "\n".join(popen_ctx.output_lines)

                self.assertNotIn("Traceback", all_output)

                # Check for the specific message
                expected_message = 'Spawning additional {"UserSubclass": 1} ({"UserSubclass": 0} already running)...'
                self.assertIn(expected_message, all_output)

                # Check return code
                self.assertEqual(0, popen_ctx.process.returncode)

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
            print(f"Combined Locust Output:\n{combined_output}")

            self.assertIn("All users spawned", combined_output, msg="Expected 'All users spawned' not found in output.")
            self.assertIn(
                "Shutting down (exit code 0)",
                combined_output,
                msg="Expected 'Shutting down (exit code 0)' not found in output.",
            )
            self.assertEqual(
                0,
                manager.process.returncode,
                msg=f"Locust process exited with return code {manager.process.returncode}",
            )
            self.assertNotIn(
                "Locust is running with the UserClass Picker Enabled",
                combined_output,
                msg="Unexpected 'UserClass Picker Enabled' message found in output.",
            )
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

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
                    self.assertEqual(
                        0,
                        manager.process.returncode,
                        msg=f"Locust process exited with return code {manager.process.returncode}.",
                    )
                    self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

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
            self.assertEqual(
                0,
                manager.process.returncode,
                msg=f"Locust process exited with return code {manager.process.returncode}.",
            )
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

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
                    self.assertEqual(
                        0,
                        manager.process.returncode,
                        msg=f"Locust process exited with return code {manager.process.returncode}.",
                    )
                    self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

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
                sys.executable,  # Use the Python interpreter
                "-m",
                "locust",
                "-f",
                mocked.file_path,
                "--web-port",
                str(port),
                "--autostart",
            ]

            with PopenContextManager(args) as manager:
                # Define the messages to check in the output
                start_message = "Starting Locust"
                no_run_time_message = "No run time limit set, use CTRL+C to interrupt"

                messages_to_check = [
                    start_message,
                    no_run_time_message,
                ]

                # Wait for each message sequentially
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

                # Make an HTTP GET request to verify the web interface is accessible
                try:
                    response = self.make_http_request(f"{port}", method="GET", path="/")
                    self.assertEqual(200, response.status_code, "Locust web interface did not return status code 200.")
                except requests.exceptions.RequestException as e:
                    manager.process.terminate()
                    self.fail(f"Failed to connect to Locust web interface: {e}")

                # Send SIGTERM to initiate graceful shutdown
                manager.process.send_signal(signal.SIGTERM)

                # Define the shutdown message to wait for
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

                # Wait for the process to terminate gracefully
                try:
                    manager.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.process.terminate()
                    manager.process.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully after SIGTERM.")

            # Combine all output lines for assertions
            combined_output = "\n".join(manager.output_lines)

            # Assertions
            self.assertIn(start_message, combined_output, msg="Start message not found in output.")
            self.assertIn(no_run_time_message, combined_output, msg="No run time message not found in output.")
            self.assertIn(shutdown_message, combined_output, msg="Shutdown message not found in output.")
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

            # Check response content using PyQuery
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
                sys.executable,  # Use the Python interpreter
                "-m",
                "locust",
                "-f",
                mocked.file_path,
                "--web-port",
                str(port),
                "-t",
                "3",  # Run time of 3 seconds
                "--autostart",
                "--autoquit",
                "1",
            ]

            with PopenContextManager(args) as manager:
                # Define the messages to check in the output
                start_message = "Starting Locust"
                run_time_message = "Run time limit set to 3 seconds"
                shutdown_message = "Shutting down"

                messages_to_check = [
                    start_message,
                    run_time_message,
                ]

                # Wait for each message sequentially
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

                # Make an HTTP GET request to verify the web interface is accessible
                try:
                    response = self.make_http_request(f"{port}", method="GET", path="/")
                    self.assertEqual(200, response.status_code, "Locust web interface did not return status code 200.")
                except requests.exceptions.RequestException as e:
                    manager.process.terminate()
                    self.fail(f"Failed to connect to Locust web interface: {e}")

                # Wait for the shutdown message indicating autoquit
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

                # Wait for the process to terminate gracefully
                try:
                    manager.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.process.terminate()
                    manager.process.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully.")

            # Combine all output lines for assertions
            combined_output = "\n".join(manager.output_lines)

            # Assertions
            self.assertIn(start_message, combined_output, msg="Start message not found in output.")
            self.assertIn(run_time_message, combined_output, msg="Run time message not found in output.")
            self.assertIn(shutdown_message, combined_output, msg="Shutdown message not found in output.")
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

            # Check response content using PyQuery
            d = pq(response.content.decode("utf-8"))
            self.assertIn('"state": "running"', str(d), msg="Expected 'running' state not found in response.")

            # Verify exit code
            self.assertEqual(
                0,
                manager.process.returncode,
                msg=f"Locust process exited with return code {manager.process.returncode}.",
            )

    @unittest.skipIf(os.name == "nt", reason="Signal handling on Windows is hard")
    def test_run_autostart_with_multiple_locustfiles(self):
        """
        Test Locust's autostart functionality with multiple Locustfiles.
        Ensures that Locust starts automatically, spawns users from multiple Locustfiles,
        and shuts down gracefully.
        """
        with TemporaryDirectory() as temp_dir:
            # Create the first mock Locustfile in the temporary directory
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
                # Create the second mock Locustfile in the same directory
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
                        sys.executable,  # Use the Python interpreter
                        "-m",
                        "locust",
                        "-f",
                        f"{mocked1},{mocked2}",  # Pass multiple Locustfile paths separated by comma
                        "--autostart",
                        "-u",
                        "2",
                        "--exit-code-on-error",
                        "0",
                        "--web-port",
                        str(port),
                    ]

                    with PopenContextManager(args) as manager:
                        # Define the messages to check in the output
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

                        # Wait for each message sequentially
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

                        # Send SIGTERM to initiate graceful shutdown
                        manager.process.send_signal(signal.SIGTERM)

                        # Wait for the shutdown message
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

                        # Wait for the process to terminate gracefully
                        try:
                            manager.process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            manager.process.terminate()
                            manager.process.wait(timeout=10)
                            self.fail("Locust process did not terminate gracefully after SIGTERM.")

                    # Combine all output lines for assertions
                    combined_output = "\n".join(manager.output_lines)

                    # Assertions
                    for message in messages_to_check + [shutdown_message]:
                        self.assertIn(
                            message, combined_output, msg=f"Expected message '{message}' not found in output."
                        )

                    self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")
                    self.assertEqual(
                        0,
                        manager.process.returncode,
                        msg=f"Locust process exited with return code {manager.process.returncode}.",
                    )

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
                sys.executable,  # Use the Python interpreter
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
                # Wait for the web interface to start
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Starting web interface at", timeout=30
                ):
                    manager.process.terminate()
                    self.fail("Timeout waiting for Locust web interface to start.")

                # Make an HTTP GET request to verify the web interface is accessible
                try:
                    response = self.make_http_request(f"{port}", method="GET", path="/", timeout=10)
                    self.assertEqual(200, response.status_code, "Locust web interface did not return status code 200.")
                except requests.exceptions.RequestException as e:
                    manager.process.terminate()
                    self.fail(f"Failed to connect to Locust web interface: {e}")

                # Wait for Locust to apply the load shape and autoquit
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Starting Locust", timeout=30
                ):
                    manager.process.terminate()
                    self.fail("Timeout waiting for Locust to start.")

                # Wait for Locust to shutdown after autoquit time
                if not wait_for_output_condition_non_threading(
                    manager.process, manager.output_lines, "Shutting down (exit code 0)", timeout=50
                ):
                    manager.process.terminate()
                    self.fail("Timeout waiting for Locust to shut down after autoquit time.")

                # Wait for the process to terminate gracefully
                try:
                    manager.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Locust did not terminate within the expected time.")
                    manager.process.terminate()
                    manager.process.wait(timeout=10)
                    self.fail("Locust process did not terminate gracefully after autoquit.")

            # Combine all output lines for assertions
            combined_output = "\n".join(manager.output_lines)

            # Assertions
            self.assertIn("Starting Locust", combined_output, msg="Expected 'Starting Locust' not found in output.")
            self.assertIn(
                "Shape test starting", combined_output, msg="Expected 'Shape test starting' not found in output."
            )
            self.assertIn("Shutting down", combined_output, msg="Expected 'Shutting down' not found in output.")
            self.assertIn(
                "autoquit time reached", combined_output, msg="Expected 'autoquit time reached' not found in output."
            )
            self.assertEqual(
                0,
                manager.process.returncode,
                msg=f"Locust process exited with return code {manager.process.returncode}.",
            )
            self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

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
            # Create the first mock Locustfile (TestUser2) in the temporary directory
            with self.create_temp_locustfile(content=content1, dir=temp_dir) as mocked1:
                # Create the second mock Locustfile with LoadTestShape (TestUser and CustomLoadTestShape)
                with self.create_temp_locustfile(content=content2, dir=temp_dir) as mocked2:
                    port = get_free_tcp_port()
                    args = [
                        sys.executable,  # Use the Python interpreter
                        "-m",
                        "locust",
                        "-f",
                        f"{mocked1},{mocked2}",  # Pass multiple Locustfile paths separated by comma
                        "--autostart",
                        "--autoquit",
                        "3",
                        "--web-port",
                        str(port),
                    ]

                    with PopenContextManager(args) as manager:
                        try:
                            # Wait for each expected message sequentially
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
                            # Ensure process is terminated
                            if manager.process.poll() is None:
                                manager.process.terminate()
                                try:
                                    manager.process.wait(timeout=5)
                                except subprocess.TimeoutExpired:
                                    manager.process.kill()

        # Combine all output lines for assertions
        combined_output = "\n".join(manager.output_lines)

        # Assertions
        for output in expected_outputs:
            self.assertIn(output, combined_output, f"Expected output not found: {output}")

        # Verify that both user tasks are present
        self.assertIn("running my_task()", combined_output, msg="TestUser task output not found.")
        self.assertIn("running my_task() again", combined_output, msg="TestUser2 task output not found.")

        # Ensure no tracebacks are present
        self.assertNotIn("Traceback", combined_output, msg="Unexpected traceback found in output.")

        # Verify exit code
        self.assertEqual(
            0,
            manager.process.returncode,
            msg=f"Locust process exited with return code {manager.process.returncode}.",
        )

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

            with run_locust_process(file_content=None, args=args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, output, timeout=30
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
                "--loglevel",
                "INFO",
            ]

            with run_locust_process(file_content=None, args=args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, output, timeout=30
                    ):
                        self.fail(f"Timeout waiting for: {output}")

        combined_output = "\n".join(manager.output_lines)
        print(f"Combined Locust Output:\n{combined_output}")

        for output in expected_outputs:
            self.assertIn(output, combined_output, f"Expected output not found: {output}")

        self.assertRegex(combined_output, r".*Aggregated[\S\s]*Shutting down[\S\s]*Aggregated.*")

        self.assertEqual(0, manager.proc.returncode, f"Process failed with return code {manager.proc.returncode}")

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

        expected_outputs = ["Total fixed_count of User classes (4) is greater than ", "Shutting down (exit code 0)"]

        with mock_locustfile(content=LOCUSTFILE_CONTENT) as mocked:
            args = ["-f", mocked.file_path, "--headless", "--run-time", "1s", "-u", "3"]

            with run_locust_process(file_content=None, args=args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, output, timeout=30
                    ):
                        self.fail(f"Timeout waiting for: {output}")

        combined_output = "\n".join(manager.output_lines)

        for output in expected_outputs:
            self.assertIn(output, combined_output, f"Expected output not found: {output}")

    def test_with_package_as_locustfile(self):
        expected_outputs = ["Starting Locust", "All users spawned:", '"UserSubclass": 1', "Shutting down (exit code 0)"]

        with TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "__init__.py"), mode="w"):
                pass

            with mock_locustfile(dir=temp_dir):
                args = ["-f", temp_dir, "--headless", "--exit-code-on-error", "0", "--run-time", "2"]

                with run_locust_process(file_content=None, args=args) as manager:
                    for output in expected_outputs:
                        if not wait_for_output_condition_non_threading(
                            manager.proc, manager.output_lines, output, timeout=30
                        ):
                            self.fail(f"Timeout waiting for: {output}")

        combined_output = "\n".join(manager.output_lines)

        for output in expected_outputs:
            self.assertIn(output, combined_output, f"Expected output not found: {output}")

        self.assertEqual(0, manager.proc.returncode, f"Process failed with return code {manager.proc.returncode}")

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
            args = ["-f", mocked.file_path, "--headless", "--run-time", "2s", "-u", "5", "-r", "10", "User2", "User3"]

            with run_locust_process(file_content=None, args=args) as manager:
                for output in expected_outputs:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, output, timeout=30
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
                with run_locust_process(args=["-f", f"{file1},{file2}", "--class-picker"], port=port) as manager:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, "Starting Locust", timeout=20
                    ):
                        self.fail("Timeout waiting for Locust to start.")

                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, "Starting web interface at", timeout=20
                    ):
                        self.fail("Timeout waiting for web interface to start.")

                    if not wait_for_output_condition_non_threading(
                        manager.proc,
                        manager.output_lines,
                        "Locust is running with the UserClass Picker Enabled",
                        timeout=20,
                    ):
                        self.fail("Timeout waiting for UserClass Picker message.")

                    manager.proc.send_signal(signal.SIGTERM)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Locust is running with the UserClass Picker Enabled", combined_output)
        self.assertIn("Starting Locust", combined_output)
        self.assertIn("Starting web interface at", combined_output)
        self.assertIn("Shutting down (exit code 0)", combined_output)

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
                with run_locust_process(args=["-f", f"{file1},{file2}"]) as manager:
                    if not wait_for_output_condition_non_threading(
                        manager.proc,
                        manager.output_lines,
                        "Duplicate user class names: TestUser1 is defined",
                        timeout=5,
                    ):
                        self.fail("Timeout waiting for duplicate user class error message.")

                    manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Duplicate user class names: TestUser1 is defined", combined_output)
        self.assertEqual(1, manager.proc.returncode)

    def test_no_error_when_same_userclass_in_two_files(self):
        with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_A) as file1:
            MOCK_LOCUSTFILE_CONTENT_C = textwrap.dedent(
                f"""
                from {os.path.basename(file1)[:-3]} import TestUser1
            """
            )
            print(MOCK_LOCUSTFILE_CONTENT_C)
            with temporary_file(content=MOCK_LOCUSTFILE_CONTENT_C) as file2:
                with run_locust_process(args=["-f", f"{file1},{file2}", "-t", "1", "--headless"]) as manager:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, "running my_task", timeout=50
                    ):
                        self.fail("Timeout waiting for 'running my_task' message.")

                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, "Shutting down (exit code 0)", timeout=10
                    ):
                        self.fail("Timeout waiting for Locust to shut down.")

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("running my_task", combined_output)
        self.assertEqual(0, manager.proc.returncode)

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
                with run_locust_process(args=["-f", f"{file1},{file2}"]) as manager:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, "Duplicate shape classes: TestShape", timeout=5
                    ):
                        self.fail("Timeout waiting for duplicate shape class error message.")

                    manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Duplicate shape classes: TestShape", combined_output)
        self.assertEqual(1, manager.proc.returncode)

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
            with run_locust_process(
                args=["-f", mocked.file_path, "--run-time=1s", "--headless", "--exit-code-on-error", "0"]
            ) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.proc,
                    manager.output_lines,
                    "--run-time, --users or --spawn-rate have no impact on LoadShapes",
                    timeout=5,
                ):
                    self.fail("Timeout waiting for LoadShapes impact message.")

                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "The following option(s) will be ignored: --run-time", timeout=5
                ):
                    self.fail("Timeout waiting for ignored options message.")

                manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("--run-time, --users or --spawn-rate have no impact on LoadShapes", combined_output)
        self.assertIn("The following option(s) will be ignored: --run-time", combined_output)
        self.assertEqual(0, manager.proc.returncode)

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
            with run_locust_process(
                args=["--headless", "-f", mocked.file_path, "--exit-code-on-error=0", "--users=1", "--spawn-rate=1"]
            ) as manager:
                expected_messages = [
                    "Shape test starting.",
                    "--run-time, --users or --spawn-rate have no impact on LoadShapes",
                    "The following option(s) will be ignored: --users, --spawn-rate",
                ]

                for message in expected_messages:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, message, timeout=5
                    ):
                        self.fail(f"Timeout waiting for message: {message}")

                manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        for message in expected_messages:
            self.assertIn(message, combined_output)

        self.assertEqual(0, manager.proc.returncode)

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
            with run_locust_process(
                args=[
                    "-f",
                    mocked.file_path,
                    "--run-time=1s",
                    "--users=1",
                    "--spawn-rate=1",
                    "--headless",
                    "--exit-code-on-error=0",
                ]
            ) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Shape test starting.", timeout=5
                ):
                    self.fail("Timeout waiting for 'Shape test starting.' message.")

                # Wait for the process to finish
                manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn("Shape test starting.", combined_output)
        self.assertNotIn("--run-time, --users or --spawn-rate have no impact on LoadShapes", combined_output)
        self.assertNotIn("The following option(s) will be ignored:", combined_output)
        self.assertEqual(0, manager.proc.returncode)

    def test_error_when_locustfiles_directory_is_empty(self):
        with TemporaryDirectory() as temp_dir:
            with run_locust_process(args=["-f", temp_dir]) as manager:
                expected_error_message = f"Could not find any locustfiles in directory '{temp_dir}'"

                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, expected_error_message, timeout=5
                ):
                    self.fail(f"Timeout waiting for error message: {expected_error_message}")

                manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        self.assertIn(expected_error_message, combined_output)
        self.assertEqual(1, manager.proc.returncode)

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
        content = textwrap.dedent(
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
        with temporary_file(content=content) as mocked:
            with run_locust_process(args=["-f", mocked, "--headless"]) as manager:
                if not wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Shape test starting", timeout=5
                ):
                    self.fail("Timeout waiting for 'Shape test starting' message.")

                manager.proc.send_signal(signal.SIGINT)

                expected_messages = ["Shape test starting", "Exiting due to CTRL+C interruption", "Test Stopped"]

                for message in expected_messages:
                    if not wait_for_output_condition_non_threading(
                        manager.proc, manager.output_lines, message, timeout=5
                    ):
                        self.fail(f"Timeout waiting for message: {message}")

                manager.proc.wait(timeout=5)

        combined_output = "\n".join(manager.output_lines)

        for message in expected_messages:
            self.assertIn(message, combined_output)

        # Check for the stats printer output
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
        port = get_free_tcp_port()
        file_content = textwrap.dedent("""
            from locust import User, task, constant
            class TestUser(User):
                wait_time = constant(1)
                @task
                def my_task(self):
                    print("running my_task()")
        """)

        with run_locust_process(
            file_content=file_content,
            args=["--headless", "--master", "--expect-workers", "2", "--expect-workers-max-wait", "1"],
            port=port,
        ) as manager:
            self.assertTrue(
                wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Waiting for workers to be ready, 0 of 2 connected", timeout=5
                ),
                "Timeout waiting for 'Waiting for workers' message",
            )

            self.assertTrue(
                wait_for_output_condition_non_threading(
                    manager.proc, manager.output_lines, "Gave up waiting for workers to connect", timeout=5
                ),
                "Timeout waiting for 'Gave up waiting' message",
            )

            combined_output = "\n".join(manager.output_lines)
            self.assertNotIn("Traceback", combined_output)

        self.assertIn(
            manager.proc.returncode,
            [1, -15],
            f"Locust process exited with unexpected return code: {manager.proc.returncode}",
        )
        self.assertIsNotNone(manager.proc.returncode, "Locust process did not terminate")

    def test_distributed_events(self):
        # Define the Locustfile content with event listeners
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

        with mock_locustfile(content=content):
            # Start the master process
            with run_locust_process(
                file_content=content,
                args=[
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-t",
                    "1",  # Run test for 1 second
                    "--exit-code-on-error",
                    "0",
                    "-L",
                    "DEBUG",
                ],
                port=get_free_tcp_port(),
            ) as master_manager:
                with run_locust_process(
                    file_content=content,
                    args=["--worker", "-L", "DEBUG"],
                    port=None,
                ) as worker_manager:
                    master_finished = wait_for_output_condition_non_threading(
                        master_manager.proc, master_manager.output_lines, "test_stop on master", timeout=5
                    )
                    self.assertTrue(master_finished, "Master did not finish as expected.")

                    worker_finished = wait_for_output_condition_non_threading(
                        worker_manager.proc, worker_manager.output_lines, "test_stop on worker", timeout=5
                    )
                    self.assertTrue(worker_finished, "Worker did not finish as expected.")

                self.assertIsNotNone(worker_manager.proc.returncode, "Worker process did not terminate")
                self.assertEqual(0, worker_manager.proc.returncode, "Worker process exited with unexpected return code")

            self.assertIsNotNone(master_manager.proc.returncode, "Master process did not terminate")
            self.assertEqual(0, master_manager.proc.returncode, "Master process exited with unexpected return code")

            master_output = "\n".join(master_manager.output_lines)
            worker_output = "\n".join(worker_manager.output_lines)

            self.assertIn("test_start on master", master_output)
            self.assertIn("test_stop on master", master_output)
            self.assertNotIn("Traceback", master_output)

            self.assertIn("test_start on worker", worker_output)
            self.assertIn("test_stop on worker", worker_output)
            self.assertNotIn("Traceback", worker_output)

    def test_distributed_tags(self):
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

        with mock_locustfile(content=content):
            with run_locust_process(
                file_content=content,
                args=[
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
                port=get_free_tcp_port(),
            ) as master_manager:
                with run_locust_process(
                    file_content=content,
                    args=["--worker", "-L", "DEBUG"],
                    port=None,
                ) as worker_manager:
                    master_finished = wait_for_output_condition_non_threading(
                        master_manager.proc, master_manager.output_lines, "Shutting down", timeout=5
                    )
                    self.assertTrue(master_finished, "Master did not shut down as expected.")

                    worker_finished = wait_for_output_condition_non_threading(
                        worker_manager.proc, worker_manager.output_lines, "Shutting down", timeout=5
                    )
                    self.assertTrue(worker_finished, "Worker did not shut down as expected.")

            self.assertIsNotNone(master_manager.proc.returncode, "Master process did not terminate")
            self.assertEqual(0, master_manager.proc.returncode, "Master process exited with unexpected return code")

            self.assertIsNotNone(worker_manager.proc.returncode, "Worker process did not terminate")
            self.assertEqual(0, worker_manager.proc.returncode, "Worker process exited with unexpected return code")

            master_output = "\n".join(master_manager.output_lines)
            worker_output = "\n".join(worker_manager.output_lines)

            self.assertIn("task1", worker_output, "Expected 'task1' not found in worker output")
            self.assertNotIn("task2", worker_output, "Unexpected 'task2' found in worker output")
            self.assertNotIn("Traceback", master_output, "Traceback found in master stderr/output")
            self.assertNotIn("Traceback", worker_output, "Traceback found in worker stderr/output")

            self.assertIn("task1", worker_output, "Master did not filter tasks correctly; 'task1' should be present")
            self.assertNotIn(
                "task2", worker_output, "Master did not filter tasks correctly; 'task2' should not be present"
            )

    def test_distributed(self):
        LOCUSTFILE_CONTENT = textwrap.dedent("""
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    pass
        """)

        with mock_locustfile(content=LOCUSTFILE_CONTENT):
            with run_locust_process(
                file_content=LOCUSTFILE_CONTENT,
                args=[
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-u",
                    "3",
                    "-t",
                    "5s",
                ],
                port=get_free_tcp_port(),
            ) as master_manager:
                with run_locust_process(
                    file_content=LOCUSTFILE_CONTENT,
                    args=["--worker"],
                    port=None,
                ) as worker_manager:
                    master_finished = wait_for_output_condition_non_threading(
                        master_manager.proc, master_manager.output_lines, "Shutting down (exit code 0)", timeout=10
                    )
                    self.assertTrue(master_finished, "Master did not shut down as expected.")

                    worker_finished = wait_for_output_condition_non_threading(
                        worker_manager.proc, worker_manager.output_lines, "Shutting down (exit code 0)", timeout=10
                    )
                    self.assertTrue(worker_finished, "Worker did not shut down as expected.")

        self.assertIsNotNone(master_manager.proc.returncode, "Master process did not terminate")
        self.assertEqual(0, master_manager.proc.returncode, "Master process exited with unexpected return code")

        self.assertIsNotNone(worker_manager.proc.returncode, "Worker process did not terminate")
        self.assertEqual(0, worker_manager.proc.returncode, "Worker process exited with unexpected return code")

        master_output = "\n".join(master_manager.output_lines)
        worker_output = "\n".join(worker_manager.output_lines)

        self.assertIn('All users spawned: {"User1": 3} (3 total users)', master_output)
        self.assertIn("Shutting down (exit code 0)", master_output)

        self.assertNotIn("Traceback", master_output, "Traceback found in master output")
        self.assertNotIn("Traceback", worker_output, "Traceback found in worker output")

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

        # Define the environment variable key and value
        env_var_key = "LOCUST_WAIT_FOR_WORKERS_REPORT_AFTER_RAMP_UP"
        env_var_value = "0.01"  # Very short wait time to trigger timeout

        with (
            mock_locustfile(content=LOCUSTFILE_CONTENT),
            patch_env(env_var_key, env_var_value),
        ):
            # Start the master process
            with run_locust_process(
                file_content=LOCUSTFILE_CONTENT,
                args=[
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "1",
                    "-u",
                    "3",
                    "-t",
                    "5s",
                ],
                port=get_free_tcp_port(),
            ) as master_manager:
                with run_locust_process(
                    file_content=LOCUSTFILE_CONTENT,
                    args=["--worker"],
                    port=None,
                ) as worker_manager:
                    master_finished = wait_for_output_condition_non_threading(
                        master_manager.proc,
                        master_manager.output_lines,
                        'Spawning is complete and report waittime is expired, but not all reports received from workers: {"User1": 2} (2 total users)',
                        timeout=10,
                    )
                    self.assertTrue(master_finished, "Master did not report timeout as expected.")

                    shutting_down = wait_for_output_condition_non_threading(
                        master_manager.proc, master_manager.output_lines, "Shutting down (exit code 0)", timeout=5
                    )
                    self.assertTrue(shutting_down, "Master did not shut down as expected.")

                    worker_finished = wait_for_output_condition_non_threading(
                        worker_manager.proc, worker_manager.output_lines, "Shutting down (exit code 0)", timeout=5
                    )
                    self.assertTrue(worker_finished, "Worker did not shut down as expected.")

        self.assertIsNotNone(master_manager.proc.returncode, "Master process did not terminate")
        self.assertEqual(0, master_manager.proc.returncode, "Master process exited with unexpected return code")

        self.assertIsNotNone(worker_manager.proc.returncode, "Worker process did not terminate")
        self.assertEqual(0, worker_manager.proc.returncode, "Worker process exited with unexpected return code")

        master_output = "\n".join(master_manager.output_lines)
        worker_output = "\n".join(worker_manager.output_lines)

        expected_timeout_message = 'Spawning is complete and report waittime is expired, but not all reports received from workers: {"User1": 2} (2 total users)'
        self.assertIn(expected_timeout_message, master_output, "Expected timeout message not found in master output")
        self.assertIn("Shutting down (exit code 0)", master_output)

        # Assertions for worker process
        self.assertNotIn("Traceback", master_output, "Traceback found in master output")
        self.assertNotIn("Traceback", worker_output, "Traceback found in worker output")

    def test_locustfile_distribution(self):
        """
        Tests that the Locust master and multiple worker processes correctly distribute users
        and handle shutdown as expected.
        """
        LOCUSTFILE_CONTENT = textwrap.dedent("""
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    pass
        """)

        with mock_locustfile(content=LOCUSTFILE_CONTENT):
            with run_locust_process(
                file_content=LOCUSTFILE_CONTENT,
                args=[
                    "--headless",
                    "--master",
                    "--expect-workers",
                    "2",
                    "-t",
                    "5s",
                    "-u",
                    "2",
                ],
                port=get_free_tcp_port(),
            ) as master_manager:
                with run_locust_process(
                    file_content=LOCUSTFILE_CONTENT,
                    args=["--worker"],
                    port=None,
                ) as worker_manager1:
                    with run_locust_process(
                        file_content=LOCUSTFILE_CONTENT,
                        args=["--worker"],
                        port=None,
                    ) as worker_manager2:
                        all_users_spawned = wait_for_output_condition_non_threading(
                            master_manager.proc,
                            master_manager.output_lines,
                            'All users spawned: {"User1": 2} (2 total users)',
                            timeout=30,
                        )
                        self.assertTrue(all_users_spawned, "Timeout waiting for all users to be spawned.")

        master_output = "\n".join(master_manager.output_lines)
        worker_output1 = "\n".join(worker_manager1.output_lines)
        worker_output2 = "\n".join(worker_manager2.output_lines)
        combined_output = f"{master_output}\n{worker_output1}\n{worker_output2}"

        self.assertIn(
            "Shutting down (exit code 0)",
            combined_output,
            f"'Shutting down (exit code 0)' not found in output:\n{combined_output}",
        )

        self.assertIn(
            'All users spawned: {"User1": 2} (2 total users)',
            combined_output,
            "Expected user spawn message not found in output.",
        )

        self.assertNotIn("Traceback", combined_output, "Traceback found in output, indicating an error.")

        self.assertEqual(
            0,
            master_manager.proc.returncode,
            f"Master process exited with unexpected return code: {master_manager.proc.returncode}",
        )
        self.assertEqual(
            0,
            worker_manager1.proc.returncode,
            f"First worker process exited with unexpected return code: {worker_manager1.proc.returncode}",
        )
        self.assertEqual(
            0,
            worker_manager2.proc.returncode,
            f"Second worker process exited with unexpected return code: {worker_manager2.proc.returncode}",
        )

    def test_locustfile_distribution_with_workers_started_first(self):
        LOCUSTFILE_CONTENT = textwrap.dedent("""
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    print("hello")
        """)

        with mock_locustfile(content=LOCUSTFILE_CONTENT):
            with run_locust_process(
                file_content=LOCUSTFILE_CONTENT,
                args=["--worker"],
                port=None,
            ) as worker_manager:
                with run_locust_process(
                    file_content=LOCUSTFILE_CONTENT,
                    args=[
                        "--headless",
                        "--master",
                        "--expect-workers",
                        "1",
                        "-t",
                        "2s",
                        "-u",
                        "2",
                    ],
                    port=get_free_tcp_port(),
                ) as master_manager:
                    all_users_spawned = wait_for_output_condition_non_threading(
                        master_manager.proc,
                        master_manager.output_lines,
                        'All users spawned: {"User1": 2} (2 total users)',
                        timeout=30,
                    )
                    self.assertTrue(all_users_spawned, "Timeout waiting for all users to be spawned.")

                    shutting_down = wait_for_output_condition_non_threading(
                        master_manager.proc, master_manager.output_lines, "Shutting down (exit code 0)", timeout=30
                    )
                    self.assertTrue(shutting_down, "'Shutting down (exit code 0)' not found in master output.")

        master_output = "\n".join(master_manager.output_lines)
        worker_output = "\n".join(worker_manager.output_lines)
        combined_output = f"{master_output}\n{worker_output}"

        self.assertIn(
            'All users spawned: {"User1": 2} (2 total users)',
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

        self.assertEqual(
            0,
            master_manager.proc.returncode,
            f"Master process exited with unexpected return code: {master_manager.proc.returncode}",
        )
        self.assertEqual(
            0,
            worker_manager.proc.returncode,
            f"Worker process exited with unexpected return code: {worker_manager.proc.returncode}",
        )

    def test_distributed_with_locustfile_distribution_not_plain_filename(self):
        LOCUSTFILE_CONTENT = textwrap.dedent("""
            from locust import User, task, constant

            class User1(User):
                wait_time = constant(1)

                @task
                def t(self):
                    print("hello")
        """)

        with mock_locustfile(content=LOCUSTFILE_CONTENT):
            with run_locust_process(
                file_content=LOCUSTFILE_CONTENT,
                args=["--worker"],
                port=None,
            ) as worker_manager:
                print(f"DEBUG: Worker started with PID {worker_manager.proc.pid}")

                with run_locust_process(
                    file_content=LOCUSTFILE_CONTENT,
                    args=[
                        "--headless",
                        "--master",
                        "--expect-workers",
                        "1",
                        "-t",
                        "5s",
                    ],
                    port=get_free_tcp_port(),  # Assign a free port to the master process
                ) as master_manager:
                    # Poll for the worker to connect to the master
                    worker_connected = wait_for_output_condition_non_threading(
                        master_manager.proc, master_manager.output_lines, "1 workers connected", timeout=30
                    )
                    self.assertTrue(worker_connected, "Worker did not connect to master.")

                    all_users_spawned = wait_for_output_condition_non_threading(
                        master_manager.proc,
                        master_manager.output_lines,
                        'All users spawned: {"User1": 1} (1 total users)',
                        timeout=30,
                    )
                    self.assertTrue(all_users_spawned, "Timeout waiting for all users to be spawned.")

                    shutting_down = wait_for_output_condition_non_threading(
                        master_manager.proc, master_manager.output_lines, "Shutting down (exit code 0)", timeout=30
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

            self.assertEqual(
                0,
                master_manager.proc.returncode,
                f"Master process exited with unexpected return code: {master_manager.proc.returncode}",
            )
            self.assertEqual(
                0,
                worker_manager.proc.returncode,
                f"Worker process exited with unexpected return code: {worker_manager.proc.returncode}",
            )

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
        with run_locust_process(
            file_content=LOCUSTFILE_CONTENT,
            args=[
                "--host",
                "http://google.com",
                "--headless",
                "-u",
                "1",
                "-t",
                "2s",
                "--json",
            ],
        ) as manager:
            manager.proc.wait()

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

            self.assertEqual(0, manager.proc.returncode)

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
            with run_locust_process(
                args=master_args,
            ) as master:
                master_ready = wait_for_output_condition_non_threading(
                    master.proc, master.output_lines, "Waiting for workers to be ready", timeout=10
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
                with (
                    run_locust_process(
                        args=worker_args,
                    ) as worker1,
                    run_locust_process(
                        args=worker_args,
                    ) as worker2,
                ):
                    workers_ready = wait_for_output_condition_non_threading(
                        master.proc, master.output_lines, "Sending spawn jobs", timeout=10
                    )

                    self.assertTrue(workers_ready, "Workers did not connect properly")

                    master.proc.wait(timeout=15)
                    self.assertEqual(0, master.proc.poll(), "Master process did not exit cleanly")

                    worker1.proc.wait(timeout=5)
                    worker2.proc.wait(timeout=5)

                    self.assertEqual(0, worker1.proc.poll(), "Worker 1 did not exit cleanly")
                    self.assertEqual(0, worker2.proc.poll(), "Worker 2 did not exit cleanly")

                    master_output = "\n".join(master.output_lines)
                    worker1_output = "\n".join(worker1.output_lines)
                    worker2_output = "\n".join(worker2.output_lines)

                    self.assertNotIn("Traceback", master_output)
                    self.assertNotIn("Traceback", worker1_output)
                    self.assertNotIn("Traceback", worker2_output)

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
            os.unlink(temp_file_path)

    @unittest.skipIf(os.name == "nt", reason="--processes doesn't work on Windows")
    def test_processes(self):
        with mock_locustfile() as mocked:
            args = [
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
            with run_locust_process(args=args) as proc:
                process_finished = wait_for_output_condition_non_threading(
                    proc.proc, proc.output_lines, "Shutting down (exit code 0)", timeout=9
                )
                if not process_finished:
                    proc.proc.kill()
                    print("Process output:\n", "\n".join(proc.output_lines))
                    self.fail(f"Locust process never finished: {' '.join(args)}")
                output = "\n".join(proc.output_lines)
                self.assertNotIn("Traceback", output)
                self.assertIn("(index 3) reported as ready", output)
                self.assertIn("Shutting down (exit code 0)", output)

    @unittest.skipIf(os.name == "nt", reason="--processes doesn't work on Windows")
    def test_processes_autodetect(self):
        with mock_locustfile() as mocked:
            args = [
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
            with run_locust_process(args=args) as proc:
                process_finished = wait_for_output_condition_non_threading(
                    proc.proc, proc.output_lines, "Shutting down (exit code 0)", timeout=9
                )
                if not process_finished:
                    proc.proc.kill()
                    print("Process output:\n", "\n".join(proc.output_lines))
                    self.fail(f"Locust process never finished: {' '.join(args)}")

                proc.proc.wait(timeout=5)
                self.assertEqual(0, proc.proc.poll(), "Locust process did not exit cleanly")

                output = "\n".join(proc.output_lines)

                self.assertNotIn("Traceback", output)
                self.assertIn("(index 0) reported as ready", output)
                self.assertIn("Shutting down (exit code 0)", output)

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
