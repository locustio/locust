from unittest import mock
import socket
import subprocess
import textwrap
from logging import getLogger

import gevent

from locust import log
from locust.log import greenlet_exception_logger
from .testcases import LocustTestCase
from .util import temporary_file
from . import changed_rlimit


class TestGreenletExceptionLogger(LocustTestCase):
    # Gevent outputs all unhandled exceptions to stderr, so we'll suppress that in this test
    @mock.patch("sys.stderr.write")
    def test_greenlet_exception_logger(self, mocked_stderr):
        self.assertFalse(log.unhandled_greenlet_exception)

        def thread():
            raise ValueError("Boom!?")

        logger = getLogger("greenlet_test_logger")
        g = gevent.spawn(thread)
        g.link_exception(greenlet_exception_logger(logger))
        g.join()
        self.assertEqual(1, len(self.mocked_log.critical))
        msg = self.mocked_log.critical[0]
        self.assertIn("Unhandled exception in greenlet: ", msg["message"])
        self.assertTrue(isinstance(msg["exc_info"][1], ValueError))
        self.assertIn("Boom!?", str(msg["exc_info"][1]))
        self.assertTrue(log.unhandled_greenlet_exception)


class TestLoggingOptions(LocustTestCase):
    def test_logging_output(self):
        with temporary_file(
            textwrap.dedent(
                """
            import logging
            from locust import User, task, constant

            custom_logger = logging.getLogger("custom_logger")

            class MyUser(User):
                wait_time = constant(2)
                @task
                def my_task(self):
                    print("running my_task")
                    logging.info("custom log message")
                    custom_logger.info("test")
        """
            )
        ) as file_path:
            output = subprocess.check_output(
                [
                    "locust",
                    "-f",
                    file_path,
                    "-u",
                    "1",
                    "-r",
                    "1",
                    "-t",
                    "1",
                    "--headless",
                ],
                stderr=subprocess.STDOUT,
                timeout=10,
                text=True,
            )

        self.assertIn(
            f"{socket.gethostname()}/INFO/locust.main: Run time limit set to 1 seconds",
            output,
        )
        self.assertIn(
            f"{socket.gethostname()}/INFO/locust.main: --run-time limit reached, shutting down",
            output,
        )
        self.assertIn(
            f"{socket.gethostname()}/INFO/locust.main: Shutting down (exit code 0)",
            output,
        )
        self.assertIn(
            "\nrunning my_task\n",
            output,
        )
        # check that custom message of root logger is also printed
        self.assertIn(
            f"{socket.gethostname()}/INFO/root: custom log message",
            output,
        )
        # check that custom message of custom_logger is also printed
        self.assertIn(
            f"{socket.gethostname()}/INFO/custom_logger: test",
            output,
        )

    def test_skip_logging(self):
        with temporary_file(
            textwrap.dedent(
                """
            from locust import User, task, constant

            class MyUser(User):
                wait_time = constant(2)
                @task
                def my_task(self):
                    print("running my_task")
        """
            )
        ) as file_path:
            output = subprocess.check_output(
                [
                    "locust",
                    "-f",
                    file_path,
                    "-u",
                    "1",
                    "-r",
                    "1",
                    "-t",
                    "1",
                    "--headless",
                    "--skip-log-setup",
                ],
                stderr=subprocess.STDOUT,
                timeout=10,
                text=True,
            )
        if not changed_rlimit:
            self.assertTrue(output.strip().endswith("running my_task"))
        else:
            self.assertEqual("running my_task", output.strip())

    def test_log_to_file(self):
        with temporary_file(
            textwrap.dedent(
                """
            import logging
            from locust import User, task, constant

            class MyUser(User):
                wait_time = constant(2)
                @task
                def my_task(self):
                    print("running my_task")
                    logging.info("custom log message")
        """
            )
        ) as file_path:
            with temporary_file("", suffix=".log") as log_file_path:
                try:
                    output = subprocess.check_output(
                        [
                            "locust",
                            "-f",
                            file_path,
                            "-u",
                            "1",
                            "-r",
                            "1",
                            "-t",
                            "1",
                            "--headless",
                            "--logfile",
                            log_file_path,
                        ],
                        stderr=subprocess.STDOUT,
                        timeout=10,
                        text=True,
                    )
                except subprocess.CalledProcessError as e:
                    raise AssertionError(f"Running locust command failed. Output was:\n\n{e.stdout}") from e

                with open(log_file_path, encoding="utf-8") as f:
                    log_content = f.read()

        # make sure print still appears in output
        self.assertIn("running my_task", output)

        # check that log messages don't go into output
        self.assertNotIn("Starting Locust", output)
        self.assertNotIn("Run time limit set to 1 seconds", output)

        # check that log messages goes into file
        self.assertIn(
            f"{socket.gethostname()}/INFO/locust.main: Run time limit set to 1 seconds",
            log_content,
        )
        self.assertIn(
            f"{socket.gethostname()}/INFO/locust.main: --run-time limit reached, shutting down",
            log_content,
        )
        self.assertIn(
            f"{socket.gethostname()}/INFO/locust.main: Shutting down (exit code 0)",
            log_content,
        )
        # check that message of custom logger also went into log file
        self.assertIn(
            f"{socket.gethostname()}/INFO/root: custom log message",
            log_content,
        )
