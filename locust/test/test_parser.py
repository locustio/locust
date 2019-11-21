import unittest
import os
import tempfile

from locust.main import parse_options


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser, _ = parse_options(default_config_files=[])

    def test_default(self):
        opts = self.parser.parse_args([])
        self.assertEqual(opts.reset_stats, False)
        self.assertEqual(opts.skip_log_setup, False)

    def test_reset_stats(self):
        args = [
            "--reset-stats"
        ]
        opts = self.parser.parse_args(args)
        self.assertEqual(opts.reset_stats, True)

    def test_should_accept_legacy_no_reset_stats(self):
        args = [
            "--no-reset-stats"
        ]
        opts = self.parser.parse_args(args)
        self.assertEqual(opts.reset_stats, False)

    def test_skip_log_setup(self):
        args = [
            "--skip-log-setup"
        ]
        opts = self.parser.parse_args(args)
        self.assertEqual(opts.skip_log_setup, True)

    def test_parameter_parsing(self):
        with tempfile.NamedTemporaryFile(mode='w') as file:
            os.environ['LOCUST_LOCUSTFILE'] = "locustfile_from_env"
            file.write("host host_from_config\nweb-host webhost_from_config")
            file.flush()
            parser, _ = parse_options(default_config_files=[file.name])
            options = parser.parse_args(['-H','host_from_args'])
            del os.environ['LOCUST_LOCUSTFILE']
        self.assertEqual(options.web_host, 'webhost_from_config')
        self.assertEqual(options.locustfile, 'locustfile_from_env')
        self.assertEqual(options.host, 'host_from_args') # overridden
