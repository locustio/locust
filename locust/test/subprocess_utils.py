import os
import shlex
import signal
import subprocess
import time
from typing import IO

import gevent
import pytest

from .util import IS_WINDOWS


class TestProcess:
    """
    Wraps a subprocess for testing purposes.
    """

    __test__ = False

    def __init__(
        self,
        command: str,
        *,
        extra_env: dict[str, str] = {},
        expect_return_code: int | None = 0,
        sigint_on_exit: bool = True,
        expect_timeout: int = 5,
        use_pty: bool = False,
        join_timeout: int = 1,
    ):
        self.proc: subprocess.Popen[str]
        self._terminated = False
        self._failed = False

        self.expect_return_code = expect_return_code
        self.expect_timeout = expect_timeout
        self.sigint_on_exit = sigint_on_exit
        self.join_timeout = join_timeout

        self.stderr_output: list[str] = []
        self.stdout_output: list[str] = []
        self._stderr_cursor: int = 0  # Used for stateful log matching
        self._stdout_cursor: int = 0

        self.use_pty: bool = use_pty
        # Create PTY pair
        if self.use_pty:
            if IS_WINDOWS:
                raise Exception("termios doesn't exist on windows, and thus we cannot import pty")

            import pty

            self.stdin_m, self.stdin_s = pty.openpty()

        self.proc = subprocess.Popen(
            shlex.split(command) if not IS_WINDOWS else command.split(" "),
            env={"PYTHONUNBUFFERED": "1", **os.environ, **extra_env},
            stdin=self.stdin_s if self.use_pty else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        def _consume_output(source: IO[str], to: list[str]):
            for line in iter(source.readline, ""):
                line = line.rstrip("\n")
                to.append(line)

        self.stdout_reader = gevent.spawn(_consume_output, self.proc.stdout, self.stdout_output)
        self.stderr_reader = gevent.spawn(_consume_output, self.proc.stderr, self.stderr_output)

    def on_fail(self, reason: str = ""):
        __tracebackhide__ = True
        if self._failed:
            return
        self._failed = True
        for line in self.stderr_output:
            print(line)
        pytest.fail(reason)

    def __enter__(self) -> "TestProcess":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def close(self) -> None:
        if self.use_pty:
            os.close(self.stdin_m)
            os.close(self.stdin_s)

        try:
            if self.sigint_on_exit and not self._terminated:
                self.terminate()
            proc_return_code = self.proc.wait(timeout=self.join_timeout)

            # Locust does not perform a graceful shutdown on Windows since we send SIGTERM
            if not IS_WINDOWS and self.expect_return_code is not None and proc_return_code != self.expect_return_code:
                self.on_fail(
                    f"Process exited with return code {proc_return_code}. Expected {self.expect_return_code} ({proc_return_code} != {self.expect_return_code})"
                )
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
            self.on_fail(f"Process took more than {self.join_timeout} seconds to terminate.")

        self.stdout_reader.join(timeout=self.join_timeout)
        self.stderr_reader.join(timeout=self.join_timeout)

    # Check output logs from last found (stateful)
    def expect(self, to_expect, *, stream="stderr"):
        __tracebackhide__ = True

        if stream == "stdout":
            buffer = self.stdout_output
            cursor = self._stdout_cursor
        else:
            buffer = self.stderr_output
            cursor = self._stderr_cursor

        start_time = time.time()
        while time.time() - start_time < self.expect_timeout:
            new_lines = buffer[cursor:]
            for idx, line in enumerate(new_lines):
                if to_expect in line:
                    cursor += idx + 1
                    return
            time.sleep(0.05)

        output = "\n".join(buffer[-5:])
        self.on_fail(f"Timed out waiting for '{to_expect}' after {self.expect_timeout} seconds. Got\n{output}")

    # Check all output logs (stateless)
    def expect_any(self, to_expect, *, stream="stderr"):
        __tracebackhide__ = True

        if stream == "stdout":
            buffer = self.stdout_output
        else:
            buffer = self.stderr_output

        if any(to_expect in line for line in buffer):
            return

        output = "\n".join(buffer[-5:])
        self.on_fail(f"Did not see expected message: '{to_expect}'. Got\n{output}")

    def not_expect_any(self, to_not_expect, *, stream="stderr"):
        __tracebackhide__ = True

        if stream == "stdout":
            buffer = self.stdout_output
        else:
            buffer = self.stderr_output

        if any(to_not_expect in line for line in buffer):
            self.on_fail(f"Found unexpected message: '{to_not_expect}'.")

    def send_input(self, content: str):
        if self.use_pty:
            os.write(self.stdin_m, content.encode())
        else:
            raise Exception("Cannot send input to proccess without pty.")

    def terminate(self):
        if IS_WINDOWS:
            # Signals are hard on Windows
            sig = signal.SIGTERM
        else:
            sig = signal.SIGINT

        self.proc.send_signal(sig)
        self._terminated = True
