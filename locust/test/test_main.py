import os
import platform
import signal
import subprocess
import textwrap
from unittest import TestCase
from subprocess import PIPE

import gevent
import requests

from locust import main
from locust.argument_parser import parse_options
from locust.main import create_environment
from locust.user import HttpUser, User, TaskSet
from .mock_locustfile import mock_locustfile
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
            self.assertIn('UserSubclass', user_classes)
            self.assertNotIn('NotUserSubclass', user_classes)
            self.assertNotIn('LoadTestShape', user_classes)

    def test_load_locust_file_from_relative_path(self):
        with mock_locustfile() as mocked:
            docstring, user_classes, shape_class = main.load_locustfile(os.path.join('./locust/test/', mocked.filename))

    def test_load_locust_file_with_a_dot_in_filename(self):
        with mock_locustfile(filename_prefix="mocked.locust.file") as mocked:
            docstring, user_classes, shape_class = main.load_locustfile(mocked.file_path)
    
    def test_return_docstring_and_user_classes(self):
        with mock_locustfile() as mocked:
            docstring, user_classes, shape_class = main.load_locustfile(mocked.file_path)
            self.assertEqual("This is a mock locust file for unit testing", docstring)
            self.assertIn('UserSubclass', user_classes)
            self.assertNotIn('NotUserSubclass', user_classes)
            self.assertNotIn('LoadTestShape', user_classes)
    
    def test_create_environment(self):
        options = parse_options(args=[
            "--host", "https://custom-host",
            "--reset-stats",
        ])
        env = create_environment([], options)
        self.assertEqual("https://custom-host", env.host)
        self.assertTrue(env.reset_stats)
        
        options = parse_options(args=[])
        env = create_environment([], options)
        self.assertEqual(None, env.host)
        self.assertFalse(env.reset_stats)

    def test_specify_config_file(self):
        with temporary_file(textwrap.dedent("""
            host = localhost  # With "="
            u 100             # Short form
            spawn-rate 5      # long form
            headless          # boolean
        """), suffix=".conf") as conf_file_path:
            options = parse_options(args=[
                "--config", conf_file_path,
            ])
            self.assertEqual(conf_file_path, options.config)
            self.assertEqual("localhost", options.host)
            self.assertEqual(100, options.num_users)
            self.assertEqual(5, options.spawn_rate)
            self.assertTrue(options.headless)

    def test_command_line_arguments_override_config_file(self):
        with temporary_file("host=from_file", suffix=".conf") as conf_file_path:
            options = parse_options(args=[
                "--config", conf_file_path,
                "--host", "from_args",
            ])
            self.assertEqual("from_args", options.host)

    def test_locustfile_can_be_set_in_config_file(self):
        with temporary_file(
            "locustfile my_locust_file.py",
            suffix=".conf",
        ) as conf_file_path:
            options = parse_options(args=[
                "--config", conf_file_path,
            ])
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
        output = subprocess.check_output(
            ["locust", "--help"],
            stderr=subprocess.STDOUT,
            timeout=5,
        ).decode("utf-8").strip()
        self.assertTrue(output.startswith("Usage: locust [OPTIONS] [UserClass ...]"))
        self.assertIn("Common options:", output)
        self.assertIn("-f LOCUSTFILE, --locustfile LOCUSTFILE", output)
        self.assertIn("Logging options:", output)
        self.assertIn("--skip-log-setup      Disable Locust's logging setup.", output)
    
    def test_custom_exit_code(self):
        with temporary_file(content=textwrap.dedent("""
            from locust import User, task, constant, events
            @events.quitting.add_listener
            def _(environment, **kw):
                environment.process_exit_code = 42
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """)) as file_path:
            proc = subprocess.Popen(["locust", "-f", file_path], stdout=PIPE, stderr=PIPE)
            gevent.sleep(1)
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate()
            self.assertEqual(42, proc.returncode)
            stderr = stderr.decode("utf-8")
            self.assertIn("Starting web interface at", stderr)
            self.assertIn("Starting Locust", stderr)
            self.assertIn("Shutting down (exit code 42), bye", stderr)

    def test_webserver(self):
        with temporary_file(content=textwrap.dedent("""
            from locust import User, task, constant, events
            class TestUser(User):
                wait_time = constant(3)
                @task
                def my_task(self):
                    print("running my_task()")
        """)) as file_path:
            proc = subprocess.Popen(["locust", "-f", file_path], stdout=PIPE, stderr=PIPE)
            gevent.sleep(1)
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate()
            self.assertEqual(0, proc.returncode)
            stderr = stderr.decode("utf-8")
            self.assertIn("Starting web interface at", stderr)
            self.assertIn("Starting Locust", stderr)
            self.assertIn("Shutting down (exit code 0), bye", stderr)

    def test_default_headless_spawn_options(self):
        with mock_locustfile() as mocked:
            output = subprocess.check_output(
                    ["locust",
                        "-f", mocked.file_path,
                        "--host", "https://test.com/",
                        "--run-time", "1s",
                        "--headless"],
                    stderr=subprocess.STDOUT,
                    timeout=2,
                    ).decode("utf-8").strip()
            self.assertIn("Spawning 1 users at the rate 1 users/s", output)

    def test_web_options(self):
        port = get_free_tcp_port()
        if platform.system() == "Darwin":
            # MacOS only sets up the loopback interface for 127.0.0.1 and not for 127.*.*.*
            interface = "127.0.0.1"
        else:
            interface = "127.0.0.2"
        with mock_locustfile() as mocked:
            proc = subprocess.Popen([
                "locust",
                "-f", mocked.file_path,
                "--web-host", interface,
                "--web-port", str(port)
            ], stdout=PIPE, stderr=PIPE)
            gevent.sleep(1)
            self.assertEqual(200, requests.get("http://%s:%i/" % (interface, port), timeout=1).status_code)
            proc.terminate()
            
        with mock_locustfile() as mocked:
            proc = subprocess.Popen([
                "locust",
                "-f", mocked.file_path,
                "--web-host", "*",
                "--web-port", str(port),
            ], stdout=PIPE, stderr=PIPE)
            gevent.sleep(1)
            self.assertEqual(200, requests.get("http://127.0.0.1:%i/" % port, timeout=1).status_code)
            proc.terminate()
