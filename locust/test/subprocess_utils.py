import os
import pty
import re
import shlex
import signal
import subprocess
import time
from collections.abc import Callable


class TestPTYProcess:
    """
    Wraps a subprocess attached to a pseudo-terminal (PTY).
    """

    def __init__(self, command: str, on_fail: Callable[[str], None], *, return_code: int = 0):
        self.stdin_m: int
        self.stdin_s: int
        self.proc: subprocess.Popen[str]

        self.on_fail = on_fail
        self.return_code = return_code
        self.expect_timeout: int = 5

        # Create PTY pair
        self.stdin_m, self.stdin_s = pty.openpty()

        self.proc = subprocess.Popen(
            shlex.split(command),
            env={"PYTHONUNBUFFERED": "1", **os.environ},
            stdin=self.stdin_s,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            close_fds=True,
            text=True,
        )

    def __enter__(self) -> "TestPTYProcess":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def close(self) -> None:
        """
        Clean up the PTY file descriptors and wait for process to exit.
        """
        error_message = "Process exited with return code %i. Expected %i (%i != %i)"

        os.close(self.stdin_m)
        os.close(self.stdin_s)

        self.send_signal(signal.SIGINT)

        proc_return_code = self.proc.wait()
        if proc_return_code != self.return_code:
            self.on_fail(error_message % (proc_return_code, self.return_code, proc_return_code, self.return_code))

    def expect_output(self, output: str):
        assert self.proc.stdout

        error_message = "Did not see expected message: '%s' within %s seconds. Got %s"
        buffer = []

        start_time = time.time()

        while line := self.proc.stdout.readline():
            buffer.append(line)
            # Do not check agains timestamps
            if output in line:
                return

            if time.time() - start_time > self.expect_timeout:
                break

            time.sleep(0.05)

        self.on_fail(error_message % (output, self.expect_timeout, buffer))

    def expect_regex(
        self,
        pattern: str | re.Pattern[str],
    ):
        assert self.proc.stdout

        error_message = "Did not find pattern: '%s' within %s seconds. Got %s"
        buffer = []

        if isinstance(pattern, str):
            regex = re.compile(pattern)
        else:
            regex = pattern

        start_time = time.time()

        while line := self.proc.stdout.readline():
            buffer.append(line)
            if regex.search(line):
                return

            if time.time() - start_time > self.expect_timeout:
                break

            time.sleep(0.05)

        self.on_fail(error_message % (pattern, self.expect_timeout, buffer))

    def send_input(self, content: str):
        os.write(self.stdin_m, content.encode())

    def send_signal(self, sig: int):
        self.proc.send_signal(sig)
