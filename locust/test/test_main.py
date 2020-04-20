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
from locust.core import HttpLocust, Locust, TaskSet
from .mock_locustfile import mock_locustfile
from .testcases import LocustTestCase
from .util import temporary_file, get_free_tcp_port


class TestLoadLocustfile(LocustTestCase):
    def test_is_locust(self):
        self.assertFalse(main.is_locust(Locust))
        self.assertFalse(main.is_locust(HttpLocust))
        self.assertFalse(main.is_locust({}))
        self.assertFalse(main.is_locust([]))
        
        class MyTaskSet(TaskSet):
            pass
        
        class MyHttpLocust(HttpLocust):
            tasks = [MyTaskSet]
        
        class MyLocust(Locust):
            tasks = [MyTaskSet]
        
        self.assertTrue(main.is_locust(MyHttpLocust))
        self.assertTrue(main.is_locust(MyLocust))
        
        class ThriftLocust(Locust):
            abstract = True
        
        self.assertFalse(main.is_locust(ThriftLocust))
    
    def test_load_locust_file_from_absolute_path(self):
        with mock_locustfile() as mocked:
            docstring, locusts = main.load_locustfile(mocked.file_path)
            self.assertIn('LocustSubclass', locusts)
            self.assertNotIn('NotLocustSubclass', locusts)

    def test_load_locust_file_from_relative_path(self):
        with mock_locustfile() as mocked:
            docstring, locusts = main.load_locustfile(os.path.join('./locust/test/', mocked.filename))

    def test_load_locust_file_with_a_dot_in_filename(self):
        with mock_locustfile(filename_prefix="mocked.locust.file") as mocked:
            docstring, locusts = main.load_locustfile(mocked.file_path)
    
    def test_return_docstring_and_locusts(self):
        with mock_locustfile() as mocked:
            docstring, locusts = main.load_locustfile(mocked.file_path)
            self.assertEqual("This is a mock locust file for unit testing", docstring)
            self.assertIn('LocustSubclass', locusts)
            self.assertNotIn('NotLocustSubclass', locusts)
    
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
        self.assertTrue(output.startswith("Usage: locust [OPTIONS] [LocustClass ...]"))
        self.assertIn("Common options:", output)
        self.assertIn("-f LOCUSTFILE, --locustfile LOCUSTFILE", output)
        self.assertIn("Logging options:", output)
        self.assertIn("--skip-log-setup      Disable Locust's logging setup.", output)
    
    def test_webserver(self):
        with temporary_file(content=textwrap.dedent("""
            from locust import Locust, task, constant, events
            class TestUser(Locust):
                wait_time = constant(3)
                @task
                def my_task():
                    print("running my_task()")
        """)) as file_path:
            proc = subprocess.Popen(["locust", "-f", file_path], stdout=PIPE, stderr=PIPE)
            gevent.sleep(1)
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate()
            self.assertEqual(0, proc.returncode)
            stderr = stderr.decode("utf-8")
            self.assertIn("Starting web monitor at", stderr)
            self.assertIn("Starting Locust", stderr)
            self.assertIn("Shutting down (exit code 0), bye", stderr)

    def test_web_options(self):
        port = get_free_tcp_port()
        if platform.system() == "Darwin":
            # MacOS only sets up the loopback interface for 127.0.0.1 and not for 127.*.*.*
            interface = "127.0.0.1"
        else:
            interface = "127.0.0.2"
        with mock_locustfile() as mocked:
            proc = subprocess.Popen(
                    ["locust",
                        "-f", mocked.file_path,
                        "--web-host", interface,
                        "--web-port", str(port)],
                    stdout=PIPE, stderr=PIPE
                    )
            gevent.sleep(0.5)
            self.assertEqual(200, requests.get("http://%s:%i/" % (interface, port), timeout=1).status_code)
            proc.terminate()
