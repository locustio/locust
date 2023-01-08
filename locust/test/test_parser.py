import unittest
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory
from random import randint
from unittest import mock
from io import StringIO

import locust
from locust.argument_parser import (
    locustfile_is_directory,
    parse_options,
    get_parser,
    parse_locustfile_option,
    ui_extra_args_dict,
    find_locustfiles,
)
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
        with NamedTemporaryFile(mode="w") as file:
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
    def setUp(self):
        super().setUp()
        self.parent_dir = TemporaryDirectory()
        self.child_dir = TemporaryDirectory(dir=self.parent_dir.name)

    def tearDown(self):
        super().tearDown()
        self.child_dir.cleanup()
        self.parent_dir.cleanup()

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
        self.assertEqual("5", options.stop_timeout)
        self.assertEqual(["MyUserClass"], options.user_classes)
        # check default arg
        self.assertEqual(8089, options.web_port)

    def test_parse_locustfile(self):
        with mock_locustfile() as mocked:
            locustfiles = parse_locustfile_option(
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
            locustfile = locustfiles[0]
            self.assertEqual(mocked.file_path, locustfile)
            assert len(locustfiles) == 1
            locustfiles = parse_locustfile_option(
                args=[
                    "-f",
                    mocked.file_path,
                ]
            )
            locustfile = locustfiles[0]
            self.assertEqual(mocked.file_path, locustfile)
            assert len(locustfiles) == 1

    def test_parse_locustfile_multiple_files(self):
        with mock_locustfile() as mocked1:
            with mock_locustfile(dir=self.parent_dir.name) as mocked2:
                locustfiles = parse_locustfile_option(
                    args=[
                        "-f",
                        f"{mocked1.file_path},{mocked2.file_path}",
                    ]
                )

                self.assertIn(mocked1.file_path, locustfiles)
                self.assertIn(mocked2.file_path, locustfiles)
                assert 2 == len(locustfiles)

    def test_parse_locustfile_with_directory(self):
        with mock_locustfile(dir=self.parent_dir.name) as mocked:
            locustfiles = parse_locustfile_option(
                args=[
                    "-f",
                    self.parent_dir.name,
                ]
            )

            self.assertIn(mocked.file_path, locustfiles)

    def test_parse_locustfile_with_nested_directory(self):
        """
        Mock Directory contents:

        ├── parent_dir/
        │   ├── mock_locustfile1.py
        │   └── child_dir/
        │       ├── mock_locustfile2.py
        │       ├── mock_locustfile3.py
        """
        with mock_locustfile(filename_prefix="mock_locustfile1", dir=self.parent_dir.name) as mock_locustfile1:
            with mock_locustfile(filename_prefix="mock_locustfile2", dir=self.child_dir.name) as mock_locustfile2:
                with mock_locustfile(filename_prefix="mock_locustfile3", dir=self.child_dir.name) as mock_locustfile3:
                    locustfiles = parse_locustfile_option(
                        args=[
                            "-f",
                            self.parent_dir.name,
                        ]
                    )

                    self.assertIn(mock_locustfile1.file_path, locustfiles)
                    self.assertIn(mock_locustfile2.file_path, locustfiles)
                    self.assertIn(mock_locustfile3.file_path, locustfiles)

    def test_parse_locustfile_with_directory_ignores_invalid_filenames(self):
        with NamedTemporaryFile(suffix=".py", prefix="_", dir=self.parent_dir.name) as invalid_file1:
            with NamedTemporaryFile(suffix=".txt", prefix="", dir=self.parent_dir.name) as invalid_file2:
                with mock_locustfile(filename_prefix="mock_locustfile1", dir=self.parent_dir.name) as mock_locustfile1:
                    locustfiles = parse_locustfile_option(
                        args=[
                            "-f",
                            self.parent_dir.name,
                        ]
                    )

                    self.assertIn(mock_locustfile1.file_path, locustfiles)
                    self.assertNotIn(invalid_file1.name, locustfiles)
                    self.assertNotIn(invalid_file2.name, locustfiles)

    def test_parse_locustfile_empty_directory_error(self):
        with mock.patch("sys.stderr", new=StringIO()):
            with self.assertRaises(SystemExit):
                locustfiles = parse_locustfile_option(
                    args=[
                        "-f",
                        self.parent_dir.name,
                    ]
                )

    def test_parse_locustfile_invalid_directory_error(self):
        with mock.patch("sys.stderr", new=StringIO()):
            with self.assertRaises(SystemExit):
                locustfiles = parse_locustfile_option(
                    args=[
                        "-f",
                        "non_existent_dir",
                    ]
                )

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

    def test_custom_argument_included_in_web_ui(self):
        @locust.events.init_command_line_parser.add_listener
        def _(parser, **kw):
            parser.add_argument("--a1", help="a1 help")
            parser.add_argument("--a2", help="a2 help", include_in_web_ui=False)
            parser.add_argument("--a3", help="a3 help", is_secret=True)

        args = ["-u", "666", "--a1", "v1", "--a2", "v2", "--a3", "v3"]
        options = parse_options(args=args)
        self.assertEqual(666, options.num_users)
        self.assertEqual("v1", options.a1)
        self.assertEqual("v2", options.a2)

        extra_args = ui_extra_args_dict(args)
        self.assertIn("a1", extra_args)
        self.assertNotIn("a2", extra_args)
        self.assertIn("a3", extra_args)
        self.assertEqual("v1", extra_args["a1"].default_value)


class TestFindLocustfiles(LocustTestCase):
    def setUp(self):
        super().setUp()
        self.parent_dir1 = TemporaryDirectory()
        self.parent_dir2 = TemporaryDirectory()
        self.child_dir = TemporaryDirectory(dir=self.parent_dir1.name)

    def tearDown(self):
        super().tearDown()
        self.child_dir.cleanup()
        self.parent_dir1.cleanup()
        self.parent_dir2.cleanup()

    def test_find_locustfiles_with_is_directory(self):
        with mock_locustfile(dir=self.parent_dir1.name) as mocked1:
            with mock_locustfile(dir=self.child_dir.name) as mocked2:
                with mock_locustfile(dir=self.child_dir.name) as mocked3:
                    locustfiles = find_locustfiles([self.parent_dir1.name], True)

                    self.assertIn(mocked1.file_path, locustfiles)
                    self.assertIn(mocked2.file_path, locustfiles)
                    self.assertIn(mocked3.file_path, locustfiles)
                    assert 3 == len(locustfiles)

    def test_find_locustfiles_error_if_directory_doesnt_exist(self):
        with mock.patch("sys.stderr", new=StringIO()):
            with self.assertRaises(SystemExit):
                find_locustfiles(["some_directory"], True)

    def test_find_locustfiles_ignores_invalid_files_in_directory(self):
        with NamedTemporaryFile(suffix=".py", prefix="_", dir=self.parent_dir1.name) as invalid_file1:
            with NamedTemporaryFile(suffix=".txt", prefix="", dir=self.parent_dir1.name) as invalid_file2:
                with mock_locustfile(filename_prefix="mock_locustfile1", dir=self.parent_dir1.name) as mock_locustfile1:
                    locustfiles = find_locustfiles([self.parent_dir1.name], True)

                    self.assertIn(mock_locustfile1.file_path, locustfiles)
                    self.assertNotIn(invalid_file1.name, locustfiles)
                    self.assertNotIn(invalid_file2.name, locustfiles)
                    assert 1 == len(locustfiles)

    def test_find_locustfiles_with_multiple_locustfiles(self):
        with mock_locustfile() as mocked1:
            with mock_locustfile() as mocked2:
                with mock_locustfile() as mocked3:
                    locustfiles = find_locustfiles([mocked1.file_path, mocked2.file_path], False)

                    self.assertIn(mocked1.file_path, locustfiles)
                    self.assertIn(mocked2.file_path, locustfiles)

                    assert 2 == len(locustfiles)

    def test_find_locustfiles_error_for_invalid_file_extension(self):
        with mock.patch("sys.stderr", new=StringIO()):
            with mock_locustfile() as valid_file:
                with self.assertRaises(SystemExit):
                    invalid_file = NamedTemporaryFile(suffix=".txt")
                    find_locustfiles([valid_file.file_path, invalid_file.name], False)

    def test_find_locustfiles_error_if_invalid_directory(self):
        with mock.patch("sys.stderr", new=StringIO()):
            with mock_locustfile() as valid_file:
                with self.assertRaises(SystemExit):
                    find_locustfiles([valid_file.file_path], True)

    def test_find_locustfiles_error_if_multiple_values_for_directory(self):
        with mock.patch("sys.stderr", new=StringIO()):
            with self.assertRaises(SystemExit):
                find_locustfiles([self.parent_dir1.name, self.parent_dir2.name], True)


class TestLocustfileIsDirectory(LocustTestCase):
    def setUp(self):
        super().setUp()
        self.random_prefix = "locust/test/foobar_" + str(randint(1000, 9999))
        self.mock_filename = self.random_prefix + ".py"

        self.mock_locustfile = open(self.mock_filename, "w")
        self.mock_locustfile.close()
        self.mock_dir = os.mkdir(self.random_prefix)

    def tearDown(self):
        super().tearDown()
        os.remove(self.mock_filename)
        os.rmdir(self.random_prefix)

    def test_locustfile_is_directory_single_locustfile(self):
        with mock_locustfile() as mocked:
            is_dir = locustfile_is_directory([mocked.file_path])
            assert not is_dir

    def test_locustfile_is_directory_single_locustfile_without_file_extension(self):
        prefix_name = "foobar"
        with NamedTemporaryFile(prefix=prefix_name, suffix=".py") as mocked:
            is_dir = locustfile_is_directory([prefix_name])
            assert not is_dir

    def test_locustfile_is_directory_multiple_locustfiles(self):
        with mock_locustfile() as mocked1:
            with mock_locustfile() as mocked2:
                is_dir = locustfile_is_directory([mocked1.file_path, mocked2.file_path])
                assert not is_dir

    def test_locustfile_is_directory_true_if_directory(self):
        with TemporaryDirectory() as mocked_dir:
            is_dir = locustfile_is_directory([mocked_dir])
            assert is_dir

    def test_locustfile_is_directory_false_if_file_and_directory_share_the_same_name(self):
        """See locustfile_is_directory docstring of an example of this usecase"""
        is_dir = locustfile_is_directory([self.random_prefix, self.mock_filename])
        assert not is_dir
