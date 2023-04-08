import os
import textwrap

from locust import main
from locust.argument_parser import parse_options
from locust.main import create_environment
from locust.user import HttpUser, User, TaskSet
from locust.util.load_locustfile import is_user_class
from .mock_locustfile import mock_locustfile, MOCK_LOCUSTFILE_CONTENT
from .testcases import LocustTestCase
from .util import temporary_file


class TestLoadLocustfile(LocustTestCase):
    def test_is_user_class(self):
        self.assertFalse(is_user_class(User))
        self.assertFalse(is_user_class(HttpUser))
        self.assertFalse(is_user_class({}))
        self.assertFalse(is_user_class([]))

        class MyTaskSet(TaskSet):
            pass

        class MyHttpUser(HttpUser):
            tasks = [MyTaskSet]

        class MyUser(User):
            tasks = [MyTaskSet]

        self.assertTrue(is_user_class(MyHttpUser))
        self.assertTrue(is_user_class(MyUser))

        class ThriftLocust(User):
            abstract = True

        self.assertFalse(is_user_class(ThriftLocust))

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
                def tick(self):
                    return None
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
