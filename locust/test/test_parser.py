import unittest
import os
import tempfile
import mock
from io import StringIO

import locust
from locust.argument_parser import parse_options, get_parser, parse_locustfile_option
from .mock_locustfile import mock_locustfile
from .testcases import LocustTestCase


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = get_parser(default_config_files=[])

    def test_default(self):
        opts = self.parser.parse_args([])
        self.assertEqual(opts.reset_stats, False)
        self.assertEqual(opts.skip_log_setup, False)

    def test_reset_stats(self):
        args = ["--reset-stats"]
        opts = self.parser.parse_args(args)
        self.assertEqual(opts.reset_stats, True)

    def test_skip_log_setup(self):
        args = ["--skip-log-setup"]
        opts = self.parser.parse_args(args)
        self.assertEqual(opts.skip_log_setup, True)

    def test_parameter_parsing(self):
        with tempfile.NamedTemporaryFile(mode="w") as file:
            os.environ["LOCUST_LOCUSTFILE"] = "locustfile_from_env"
            file.write("host host_from_config\nweb-host webhost_from_config")
            file.flush()
            parser = get_parser(default_config_files=[file.name])
            options = parser.parse_args(["-H", "host_from_args"])
            del os.environ["LOCUST_LOCUSTFILE"]
        self.assertEqual(options.web_host, "webhost_from_config")
        self.assertEqual(options.locustfile, "locustfile_from_env")
        self.assertEqual(options.host, "host_from_args")  # overridden

    def test_web_auth(self):
        args = ["--web-auth", "hello:bye"]
        opts = self.parser.parse_args(args)
        self.assertEqual(opts.web_auth, "hello:bye")


class TestArgumentParser(LocustTestCase):
    def test_parse_options(self):
        options = parse_options(
            args=[
                "-f",
                "locustfile.py",
                "-u",
                "100",
                "-r",
                "10",
                "-t",
                "5m",
                "--reset-stats",
                "--stop-timeout",
                "5",
                "MyUserClass",
            ]
        )
        self.assertEqual("locustfile.py", options.locustfile)
        self.assertEqual(100, options.num_users)
        self.assertEqual(10, options.spawn_rate)
        self.assertEqual("5m", options.run_time)
        self.assertTrue(options.reset_stats)
        self.assertEqual(5, options.stop_timeout)
        self.assertEqual(["MyUserClass"], options.user_classes)
        # check default arg
        self.assertEqual(8089, options.web_port)

    def test_parse_locustfile(self):
        with mock_locustfile() as mocked:
            locustfile = parse_locustfile_option(
                args=[
                    "-f",
                    mocked.file_path,
                    "-u",
                    "100",
                    "-r",
                    "10",
                    "-t",
                    "5m",
                    "--reset-stats",
                    "--stop-timeout",
                    "5",
                    "MyUserClass",
                ]
            )
            self.assertEqual(mocked.file_path, locustfile)
            locustfile = parse_locustfile_option(
                args=[
                    "-f",
                    mocked.file_path,
                ]
            )
            self.assertEqual(mocked.file_path, locustfile)

    def test_unknown_command_line_arg(self):
        with self.assertRaises(SystemExit):
            with mock.patch("sys.stderr", new=StringIO()):
                parse_options(
                    args=[
                        "-f",
                        "something.py",
                        "-u",
                        "100",
                        "-r",
                        "10",
                        "-t",
                        "5m",
                        "--reset-stats",
                        "--stop-timeout",
                        "5",
                        "--unknown-flag",
                        "MyUserClass",
                    ]
                )

    def test_custom_argument(self):
        @locust.events.init_command_line_parser.add_listener
        def _(parser, **kw):
            parser.add_argument("--custom-bool-arg", action="store_true", help="Custom boolean flag")
            parser.add_argument(
                "--custom-string-arg",
                help="Custom string arg",
            )

        options = parse_options(
            args=[
                "-u",
                "666",
                "--custom-bool-arg",
                "--custom-string-arg",
                "HEJ",
            ]
        )
        self.assertEqual(666, options.num_users)
        self.assertEqual("HEJ", options.custom_string_arg)
        self.assertTrue(options.custom_bool_arg)

    def test_custom_argument_help_message(self):
        @locust.events.init_command_line_parser.add_listener
        def _(parser, **kw):
            parser.add_argument("--custom-bool-arg", action="store_true", help="Custom boolean flag")
            parser.add_argument(
                "--custom-string-arg",
                help="Custom string arg",
            )

        out = StringIO()
        with mock.patch("sys.stdout", new=out):
            with self.assertRaises(SystemExit):
                parse_options(args=["--help"])

        out.seek(0)
        stdout = out.read()
        self.assertIn("Custom boolean flag", stdout)
        self.assertIn("Custom string arg", stdout)

    def test_csv_full_history_requires_csv(self):
        with mock.patch("sys.stderr", new=StringIO()):
            with self.assertRaises(SystemExit):
                parse_options(
                    args=[
                        "-f",
                        "locustfile.py",
                        "--csv-full-history",
                    ]
                )
