from __future__ import annotations

import json
import os
import platform
import signal
import socket
import subprocess
import sys
import textwrap
import unittest
from subprocess import DEVNULL, PIPE, STDOUT
from tempfile import TemporaryDirectory
from unittest import TestCase

import gevent
import psutil
import requests
from pyquery import PyQuery as pq

from .mock_locustfile import MOCK_LOCUSTFILE_CONTENT, mock_locustfile
from .util import get_free_tcp_port, patch_env, temporary_file

SHORT_SLEEP = 2 if sys.platform == "darwin" else 1  # macOS is slow on GH, give it some extra time


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def use_shell(override: bool = False) -> bool:
    if override:
        return override
    return os.name == "nt"


def shell_str(args_list: list[str], override: bool = False) -> list[str] | str:
    if use_shell(override=override):
        return " ".join(args_list)
    return args_list


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

    def assert_run(self, cmd: list[str], timeout: int = 5) -> subprocess.CompletedProcess[str]:
        out = subprocess.run(shell_str(cmd), capture_output=True, text=True, timeout=timeout, shell=use_shell())
        self.assertEqual(0, out.returncode, f"locust run failed with exit code {out.returncode}:\n{out.stderr}")
        return out


class StandaloneIntegrationTests(ProcessIntegrationTest):
    def windows(self):
        env = os.environ.copy()
        print(env)
        env["PATH"] = r"D:\a\locust\locust\.tox\fail_fast_test_main\Scripts"
        output = subprocess.check_output(
            ["locust", "--help"], stderr=subprocess.STDOUT, timeout=5, text=True, env=env
        ).strip()
        self.assertTrue(output.startswith("Usage: locust [options] [UserClass"))
