import os
import re
import shlex
import signal
import subprocess
import time
from collections.abc import Callable
from typing import IO, Any

import gevent

from .util import IS_WINDOWS


class TestProcess:
    """
    Wraps a subprocess for testing purposes.
    """

    __test__ = False

    def __init__(
        self,
        command: str,
        on_fail: Callable[[str], None],
        *,
        expect_return_code: int | None = None,
        should_send_sigint: bool = True,
        use_pty: bool = False,
    ):
        self.proc: subprocess.Popen[str]
        self._exitted = False

        self.on_fail = on_fail
        self.expect_return_code = expect_return_code
        self.expect_timeout: int = 5
        self.should_send_sigint = should_send_sigint

        self.output_lines: list[str] = []
        self._cursor: int = 0  # Used for stateful log matching

        self.use_pty: bool = use_pty
        # Create PTY pair
        if self.use_pty:
            if IS_WINDOWS:
                raise Exception("termios doesn't exist on windows, and thus we cannot import pty")

            import pty

            self.stdin_m, self.stdin_s = pty.openpty()

        self.proc = subprocess.Popen(
            shlex.split(command) if not IS_WINDOWS else command.split(" "),
            env={"PYTHONUNBUFFERED": "1", **os.environ},
            stdin=self.stdin_s if self.use_pty else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        def _consume_output(source: IO[str]):
            for line in iter(source.readline, ""):
                line = line.rstrip("\n")
                self.output_lines.append(line)

        self.stdout_reader = gevent.spawn(_consume_output, self.proc.stdout)

    def __enter__(self) -> "TestProcess":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def close(self, timeout: int = 1) -> None:
        if self.use_pty:
            os.close(self.stdin_m)
            os.close(self.stdin_s)

        try:
            if self.should_send_sigint and not self._exitted:
                self.terminate()
            proc_return_code = self.proc.wait(timeout=timeout)

            # Locust does not perform a graceful shutdown on Windows since we send SIGTERM
            if not IS_WINDOWS and self.expect_return_code is not None and proc_return_code != self.expect_return_code:
                self.on_fail(
                    f"Process exited with return code {proc_return_code}. Expected {self.expect_return_code} ({proc_return_code} != {self.expect_return_code})"
                )
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
            self.on_fail(f"Process took more than {timeout} seconds to terminate.")

        self.stdout_reader.join(timeout=timeout)

    # Check output logs from last found (stateful)
    def _expect(self, to_expect, is_match: Callable[[Any, str], bool]):
        start_time = time.time()
        while time.time() - start_time < self.expect_timeout:
            new_lines = self.output_lines[self._cursor :]
            for idx, line in enumerate(new_lines):
                if is_match(to_expect, line):
                    self._cursor += idx + 1
                    return
            time.sleep(0.05)

        self.on_fail(
            f"Did not see expected message: '{to_expect}' within {self.expect_timeout} seconds. Got {self.output_lines[-5:]}"
        )

    # Check all output logs (stateless)
    def _expect_any(self, to_expect, is_match: Callable[[Any, str], bool]):
        if any(is_match(to_expect, line) for line in self.output_lines):
            return

        self.on_fail(f"Did not see expected message: '{to_expect}'. Got {self.output_lines[-5:]}")

    def _not_expect_any(self, to_not_expect, is_match: Callable[[Any, str], bool]):
        if any(is_match(to_not_expect, line) for line in self.output_lines):
            self.on_fail(f"Found unexpected message: '{to_not_expect}'.")

    def expect(self, output: str):
        is_match: Callable[[str, str], bool] = lambda out, line: out in line
        return self._expect(output, is_match)

    def expect_any(self, output: str):
        is_match: Callable[[str, str], bool] = lambda out, line: out in line
        return self._expect_any(output, is_match)

    def not_expect_any(self, output: str):
        is_match: Callable[[str, str], bool] = lambda out, line: out in line
        return self._not_expect_any(output, is_match)

    def expect_regex(self, pattern: str | re.Pattern[str]):
        if isinstance(pattern, str):
            regex = re.compile(pattern)
        else:
            regex = pattern

        is_match: Callable[[re.Pattern, str], bool] = lambda pattern, line: pattern.search(line) is not None
        return self._expect(regex, is_match)

    def expect_regex_any(self, pattern: str | re.Pattern[str]):
        if isinstance(pattern, str):
            regex = re.compile(pattern)
        else:
            regex = pattern

        is_match: Callable[[re.Pattern, str], bool] = lambda pattern, line: pattern.search(line) is not None
        return self._expect(regex, is_match)

    def send_input(self, content: str):
        if self.use_pty:
            os.write(self.stdin_m, content.encode())

    def terminate(self):
        if not IS_WINDOWS:
            sig = signal.SIGINT
        else:
            # Signals are hard on Windows
            sig = signal.SIGTERM

        self.proc.send_signal(sig)
        self._exitted = True
