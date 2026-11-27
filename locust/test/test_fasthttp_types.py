"""Type-checker coverage for FastHttpSession keyword arguments (issue #3611)."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Requests-only names that must not be on FastHttpSession's TypedDicts.
_REQUESTS_ONLY_KWARGS = ("timeout", "verify", "cert", "proxies", "cookies", "hooks")

_SNIPPET = """\
from locust.contrib.fasthttp import FastHttpSession

def valid(s: FastHttpSession) -> None:
    s.get("/x", params={"arg": "hello"}, headers={"X": "y"}, name="n")
    s.request("GET", "/x", params={"arg": "hello"})
    s.post("/x", data="body", json=None)
    s.iter_lines("/x", method="GET", params={"arg": "hello"})

def invalid(s: FastHttpSession) -> None:
    s.get("/x", timeout=5)
    s.get("/x", verify=False)
    s.get("/x", cert="client.pem")
    s.get("/x", proxies={"http": "http://127.0.0.1:1"})
    s.get("/x", cookies={"session": "abc"})
    s.get("/x", hooks={})
    s.request("GET", "/x", timeout=5)
    s.post("/x", timeout=5)
"""


class TestFastHttpSessionTypes(unittest.TestCase):
    def test_requests_only_kwargs_are_rejected_by_mypy(self):
        try:
            import mypy  # noqa: F401
        except ImportError:
            self.skipTest("mypy is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            snippet = Path(tmp) / "check_fasthttp_kwargs.py"
            snippet.write_text(_SNIPPET)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mypy",
                    "--python-version",
                    "3.11",
                    "--ignore-missing-imports",
                    "--show-error-codes",
                    str(snippet),
                ],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                env={**os.environ, "MYPYPATH": str(REPO_ROOT)},
            )

        output = result.stdout + result.stderr
        self.assertNotIn("valid(", output, msg=output)
        for name in _REQUESTS_ONLY_KWARGS:
            with self.subTest(kwarg=name):
                self.assertIn(f'Unexpected keyword argument "{name}"', output, msg=output)
        self.assertIn('Unexpected keyword argument "timeout" for "request"', output, msg=output)
        self.assertIn('Unexpected keyword argument "timeout" for "post"', output, msg=output)
        self.assertNotEqual(result.returncode, 0, msg=output)
