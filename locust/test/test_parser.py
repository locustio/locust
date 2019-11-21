import unittest
import os

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
        conf_file = '/tmp/locust.conf'
        os.environ['LOCUST_LOCUSTFILE'] = "locustfile_from_env"
        with open(conf_file, 'w') as file:
            file.write("host host_from_config\nweb-host webhost_from_config\n")
        parser, _ = parse_options(default_config_files=['/tmp/locust.conf'])
        options = parser.parse_args(['-H','host_from_args'])
        del os.environ['LOCUST_LOCUSTFILE'] # remove this so it doesnt impact later tests
        os.remove(conf_file)
        self.assertEqual(options.web_host, 'webhost_from_config')
        self.assertEqual(options.locustfile, 'locustfile_from_env')
        self.assertEqual(options.host, 'host_from_args') # overridden
