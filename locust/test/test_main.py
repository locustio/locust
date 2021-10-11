import os
import platform
import pty
import signal
import subprocess
import textwrap
from unittest import TestCase
from subprocess import PIPE, STDOUT

import gevent
import requests

from locust import main
from locust.argument_parser import parse_options
from locust.main import create_environment
from locust.user import HttpUser, User, TaskSet
from .mock_locustfile import mock_locustfile, MOCK_LOCUSTFILE_CONTENT
from .testcases import LocustTestCase
from .util import temporary_file, get_free_tcp_port


class TestLoadLocustfile(LocustTestCase):
    def test_is_user_class(self):
        self.assertFalse(main.is_user_class(User))
        self.assertFalse(main.is_user_class(HttpUser))
        self.assertFalse(main.is_user_class({}))
        self.assertFalse(main.is_user_class([]))

        class MyTaskSet(TaskSet):
            pass

        class MyHttpUser(HttpUser):
            tasks = [MyTaskSet]

        class MyUser(User):
            tasks = [MyTaskSet]

        self.assertTrue(main.is_user_class(MyHttpUser))
        self.assertTrue(main.is_user_class(MyUser))

        class ThriftLocust(User):
            abstract = True

        self.assertFalse(main.is_user_class(ThriftLocust))

    def test_load_locust_file_from_absolute_path(self):
        with mock_locustfile() as mocked:
            docstring, user_classes, shape_class = main.load_locustfile(mocked.file_path)
            self.assertIn("UserSubclass", user_classes)
            self.assertNotIn("NotUserSubclass", user_classes)
            self.assertNotIn("LoadTestShape", user_classes)
            self.assertIsNone(shape_class)

    def test_load_locust_file_from_relative_path(self):
        with mock_locustfile() as mocked:
            docstring, user_classes, shape_class = main.load_locustfile(
                os.path.join(os.path.relpath(mocked.directory, os.getcwd()), mocked.filename)
            )

    def test_load_locust_file_with_a_dot_in_filename(self):
        with mock_locustfile(filename_prefix="mocked.locust.file") as mocked:
            docstring, user_classes, shape_class = main.load_locustfile(mocked.file_path)

    def test_return_docstring_and_user_classes(self):
        with mock_locustfile() as mocked:
            docstring, user_classes, shape_class = main.load_locustfile(mocked.file_path)
            self.assertEqual("This is a mock locust file for unit testing", docstring)
            self.assertIn("UserSubclass", user_classes)
            self.assertNotIn("NotUserSubclass", user_classes)
            self.assertNotIn("LoadTestShape", user_classes)

    def test_with_shape_class(self):
        content = (
            MOCK_LOCUSTFILE_CONTENT
            + """class LoadTestShape(LoadTestShape):
    pass
        """
        )
        with mock_locustfile(content=content) as mocked:
            docstring, user_classes, shape_class = main.load_locustfile(mocked.file_path)
            self.assertEqual("This is a mock locust file for unit testing", docstring)
            self.assertIn("UserSubclass", user_classes)
            self.assertNotIn("NotUserSubclass", user_classes)
            self.assertEqual(shape_class.__class__.__name__, "LoadTestShape")

    def test_create_environment(self):
        options = parse_options(
            args=[
                "--host",
                "https://custom-host",
                "--reset-stats",
            ]
        )
        env = create_environment([], options)
        self.assertEqual("https://custom-host", env.host)
        self.assertTrue(env.reset_stats)

        options = parse_options(args=[])
        env = create_environment([], options)
        self.assertEqual(None, env.host)
        self.assertFalse(env.reset_stats)

    def test_specify_config_file(self):
        with temporary_file(
            textwrap.dedent(
                """
            host = localhost  # With "="
            u 100             # Short form
            spawn-rate 5      # long form
                              # boolean
            headless
            # (for some reason an inline comment makes boolean values fail in configargparse nowadays)
        """
            ),
            suffix=".conf",
        ) as conf_file_path:
            options = parse_options(
                args=[
                    "--config",
                    conf_file_path,
                ]
            )
            self.assertEqual(conf_file_path, options.config)
            self.assertEqual("localhost", options.host)
            self.assertEqual(100, options.num_users)
            self.assertEqual(5, options.spawn_rate)
            self.assertTrue(options.headless)

    def test_command_line_arguments_override_config_file(self):
        with temporary_file("host=from_file", suffix=".conf") as conf_file_path:
            options = parse_options(
                args=[
                    "--config",
                    conf_file_path,
                    "--host",
                    "from_args",
                ]
            )
            self.assertEqual("from_args", options.host)

    def test_locustfile_can_be_set_in_config_file(self):
        with temporary_file(
            "locustfile my_locust_file.py",
            suffix=".conf",
        ) as conf_file_path:
            options = parse_options(
                args=[
                    "--config",
                    conf_file_path,
                ]
            )
            self.assertEqual("my_locust_file.py", options.locustfile)


class LocustProcessIntegrationTest(TestCase):
    def setUp(self):
        super().setUp()
        self.timeout = gevent.Timeout(10)
        self.timeout.start()

    def tearDown(self):
        self.timeout.cancel()
        super().tearDown()

    def test_help_arg(self):
        output = (
            subprocess.check_output(
                ["locust", "--help"],
                stderr=subprocess.STDOUT,
                timeout=5,
            )
            .decode("utf-8")
            .strip()
        )
        self.assertTrue(output.startswith("Usage: locust [OPTIONS] [UserClass ...]"))
        self.assertIn("Common options:", output)
        self.assertIn("-f LOCUSTFILE, --locustfile LOCUSTFILE", output)
        self.assertIn("Logging options:", output)
        self.assertIn("--skip-log-setup      Disable Locust's logging setup.", output)

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
            proc = subprocess.Popen(
                ["locust", "-f", file_path, "--custom-string-arg", "command_line_value", "--web-port", str(port)],
                stdout=PIPE,
                stderr=PIPE,
            )
            gevent.sleep(1)

        requests.post(
            "http://127.0.0.1:%i/swarm" % port,
            data={"user_count": 1, "spawn_rate": 1, "host": "https://localhost", "custom_string_arg": "web_form_value"},
        )
        gevent.sleep(1)

        proc.send_signal(signal.SIGTERM)
        stdout, stderr = proc.communicate(timeout=2)
        stderr = stderr.decode("utf-8")
        stdout = stdout.decode("utf-8")
        self.assertIn("Starting Locust", stderr)
        self.assertNotIn("command_line_value", stdout)
        self.assertIn("web_form_value", stdout)

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
                proc = subprocess.Popen(
                    ["locust", "-f", file_path, "--autostart"],
                    stdout=PIPE,
                    stderr=PIPE,
                )
                gevent.sleep(1)
            finally:
                os.remove("locust.conf")

        proc.send_signal(signal.SIGTERM)
        stdout, stderr = proc.communicate(timeout=2)
        stderr = stderr.decode("utf-8")
        stdout = stdout.decode("utf-8")
        self.assertIn("Starting Locust", stderr)
        self.assertIn("config_file_value", stdout)

    def test_custom_exit_code(self):
        with temporary_file(
            content=textwrap.dedent(
                """
            from locust import User, task, constant, events
            @events.quitting.add_listener
            def _(environment, **kw):
                environment.process_exit_code = 42
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """
            )
        ) as file_path:
            proc = subprocess.Popen(["locust", "-f", file_path], stdout=PIPE, stderr=PIPE)
            gevent.sleep(1)
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate()
            stderr = stderr.decode("utf-8")
            self.assertIn("Starting web interface at", stderr)
            self.assertIn("Starting Locust", stderr)
            self.assertIn("Shutting down (exit code 42), bye", stderr)
            self.assertEqual(42, proc.returncode)

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
            proc = subprocess.Popen(["locust", "-f", file_path], stdout=PIPE, stderr=PIPE)
            gevent.sleep(1)
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate()
            stderr = stderr.decode("utf-8")
            self.assertIn("Starting web interface at", stderr)
            self.assertIn("Starting Locust", stderr)
            self.assertIn("Shutting down (exit code 0), bye", stderr)
            self.assertEqual(0, proc.returncode)

    def test_default_headless_spawn_options(self):
        with mock_locustfile() as mocked:
            output = (
                subprocess.check_output(
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
                    ],
                    stderr=subprocess.STDOUT,
                    timeout=2,
                )
                .decode("utf-8")
                .strip()
            )
            self.assertIn('Spawning additional {"UserSubclass": 1} ({"UserSubclass": 0} already running)...', output)

    def test_headless_spawn_options_wo_run_time(self):
        with mock_locustfile() as mocked:
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--host",
                    "https://test.com/",
                    "--headless",
                    "--exit-code-on-error",
                    "0",
                ],
                stdout=PIPE,
                stderr=PIPE,
            )
            gevent.sleep(1)
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate()
            stderr = stderr.decode("utf-8")
            self.assertIn("Starting Locust", stderr)
            self.assertIn("No run time limit set, use CTRL+C to interrupt", stderr)
            self.assertIn("Shutting down (exit code 0), bye", stderr)
            self.assertEqual(0, proc.returncode)

    def test_default_headless_spawn_options_with_shape(self):
        content = MOCK_LOCUSTFILE_CONTENT + textwrap.dedent(
            """
            class LoadTestShape(LoadTestShape):
                def tick(self):
                    run_time = self.get_run_time()
                    if run_time < 2:
                        return (10, 1)

                    return None
            """
        )
        with mock_locustfile(content=content) as mocked:
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--host",
                    "https://test.com/",
                    "--headless",
                    "--exit-code-on-error",
                    "0",
                ],
                stdout=PIPE,
                stderr=PIPE,
            )

            try:
                success = True
                _, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                success = False
                proc.send_signal(signal.SIGTERM)
                _, stderr = proc.communicate()

            proc.send_signal(signal.SIGTERM)
            _, stderr = proc.communicate()
            stderr = stderr.decode("utf-8")
            self.assertIn("Shape test updating to 10 users at 1.00 spawn rate", stderr)
            self.assertIn("Cleaning up runner...", stderr)
            self.assertEqual(0, proc.returncode)
            self.assertTrue(success, "got timeout and had to kill the process")

    def test_autostart_wo_run_time(self):
        port = get_free_tcp_port()
        with mock_locustfile() as mocked:
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--web-port",
                    str(port),
                    "--autostart",
                ],
                stdout=PIPE,
                stderr=PIPE,
            )
            gevent.sleep(1.9)
            try:
                response = requests.get(f"http://0.0.0.0:{port}/")
            except Exception:
                pass
            self.assertEqual(200, response.status_code)
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate()
            stderr = stderr.decode("utf-8")
            self.assertIn("Starting Locust", stderr)
            self.assertIn("No run time limit set, use CTRL+C to interrupt", stderr)
            self.assertIn("Shutting down ", stderr)
            self.assertNotIn("Traceback", stderr)
            # check response afterwards, because it really isnt as informative as stderr
            self.assertEqual(200, response.status_code)
            self.assertIn('<body class="running">', response.text)

    def test_autostart_w_run_time(self):
        port = get_free_tcp_port()
        with mock_locustfile() as mocked:
            proc = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    mocked.file_path,
                    "--web-port",
                    str(port),
                    "-t",
                    "2",
                    "--autostart",
                    "--autoquit",
                    "1",
                ],
                stdout=PIPE,
                stderr=PIPE,
            )
            gevent.sleep(1.9)
            try:
                response = requests.get(f"http://0.0.0.0:{port}/")
            except Exception:
                pass
            _, stderr = proc.communicate(timeout=2)
            stderr = stderr.decode("utf-8")
            self.assertIn("Starting Locust", stderr)
            self.assertIn("Run time limit set to 2 seconds", stderr)
            self.assertIn("Shutting down ", stderr)
            self.assertNotIn("Traceback", stderr)
            # check response afterwards, because it really isnt as informative as stderr
            self.assertEqual(200, response.status_code)
            self.assertIn('<body class="running">', response.text)

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
                    "2",
                ],
                stdout=PIPE,
                stderr=PIPE,
            )
            gevent.sleep(1.9)
            response = requests.get(f"http://0.0.0.0:{port}/")
            try:
                success = True
                _, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                success = False
                proc.send_signal(signal.SIGTERM)
                _, stderr = proc.communicate()

            stderr = stderr.decode("utf-8")
            self.assertIn("Starting Locust", stderr)
            self.assertIn("Shape test starting", stderr)
            self.assertIn("Shutting down ", stderr)
            self.assertIn("autoquit time reached", stderr)
            # check response afterwards, because it really isnt as informative as stderr
            self.assertEqual(200, response.status_code)
            self.assertIn('<body class="spawning">', response.text)
            self.assertTrue(success, "got timeout and had to kill the process")

    def test_web_options(self):
        port = get_free_tcp_port()
        if platform.system() == "Darwin":
            # MacOS only sets up the loopback interface for 127.0.0.1 and not for 127.*.*.*
            interface = "127.0.0.1"
        else:
            interface = "127.0.0.2"
        with mock_locustfile() as mocked:
            proc = subprocess.Popen(
                ["locust", "-f", mocked.file_path, "--web-host", interface, "--web-port", str(port)],
                stdout=PIPE,
                stderr=PIPE,
            )
            gevent.sleep(1)
            self.assertEqual(200, requests.get("http://%s:%i/" % (interface, port), timeout=1).status_code)
            proc.terminate()

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
            )
            gevent.sleep(1)
            self.assertEqual(200, requests.get("http://127.0.0.1:%i/" % port, timeout=1).status_code)
            proc.terminate()

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

            output = proc.communicate()[0].decode("utf-8")
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
            self.assertIn("Shutting down (exit code 0), bye.", output)
            self.assertEqual(0, proc.returncode)

    def test_html_report_option(self):
        with mock_locustfile() as mocked:
            with temporary_file("", suffix=".html") as html_report_file_path:
                try:
                    output = (
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
                        )
                        .decode("utf-8")
                        .strip()
                    )
                except subprocess.CalledProcessError as e:
                    raise AssertionError(
                        "Running locust command failed. Output was:\n\n%s" % e.stdout.decode("utf-8")
                    ) from e

                with open(html_report_file_path, encoding="utf-8") as f:
                    html_report_content = f.read()

        # make sure title appears in the report
        _, locustfile = os.path.split(mocked.file_path)
        self.assertIn(f"<title>Test Report for {locustfile}</title>", html_report_content)
        self.assertIn(f"<p>Script: <span>{locustfile}</span></p>", html_report_content)

        # make sure host appears in the report
        self.assertIn("https://test.com/", html_report_content)

        # make sure the charts container appears in the report
        self.assertIn("charts-container", html_report_content)

        self.assertNotIn("Download the Report", html_report_content, "Download report link found in HTML content")
