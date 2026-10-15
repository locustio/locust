from locust.html import process_html_filename

import unittest
from unittest.mock import MagicMock


class TestProcessHtmlFilename(unittest.TestCase):
    def test_process_html_filename(self):
        mock_options = MagicMock()
        mock_options.num_users = 100
        mock_options.spawn_rate = 10
        mock_options.run_time = 60
        mock_options.html_file = "report_u{u}_r{r}_t{t}.html"

        process_html_filename(mock_options)

        expected_filename = "report_u100_r10_t60.html"
        self.assertEqual(mock_options.html_file, expected_filename)

    def test_process_html_filename_partial_replacement(self):
        mock_options = MagicMock()
        mock_options.num_users = 50
        mock_options.spawn_rate = 5
        mock_options.run_time = 30
        mock_options.html_file = "loadtest_{u}_{r}.html"

        process_html_filename(mock_options)

        expected_filename = "loadtest_50_5.html"
        self.assertEqual(mock_options.html_file, expected_filename)

    def test_process_html_filename_no_replacement(self):
        mock_options = MagicMock()
        mock_options.num_users = 50
        mock_options.spawn_rate = 5
        mock_options.run_time = 30
        mock_options.html_file = "static_report.html"

        process_html_filename(mock_options)

        expected_filename = "static_report.html"
        self.assertEqual(mock_options.html_file, expected_filename)

    def test_process_html_filename_None_arguments(self):
        mock_options = MagicMock()
        mock_options.num_users = 5
        # mock_options.spawn_rate = None
        mock_options.run_time = None
        mock_options.html_file = "report_u{u}_r{r}_t{t}.html"

        process_html_filename(mock_options)

        expected_filename = "report_u5_r1_t{t}.html"
        self.assertEqual(mock_options.html_file, expected_filename)

    def test_process_html_filename_fractional_spawn_rate(self):
        """--spawn-rate is a float option, so {r} must not be truncated to 0."""
        for spawn_rate, expected in (
            (0.5, "report_10_0.5.html"),
            (1.5, "report_10_1.5.html"),
            (2.0, "report_10_2.html"),
        ):
            mock_options = MagicMock()
            mock_options.num_users = 10
            mock_options.spawn_rate = spawn_rate
            mock_options.run_time = None
            mock_options.html_file = "report_{u}_{r}.html"

            process_html_filename(mock_options)

            self.assertEqual(mock_options.html_file, expected)

    def test_process_html_filename_keeps_distinct_spawn_rates_apart(self):
        """Rates a user can actually pass must not collide on one report file name."""
        names = set()
        for spawn_rate in (0.05, 0.2, 0.5):
            mock_options = MagicMock()
            mock_options.num_users = 10
            mock_options.spawn_rate = spawn_rate
            mock_options.run_time = None
            mock_options.html_file = "report_{u}_{r}.html"

            process_html_filename(mock_options)
            names.add(mock_options.html_file)

        self.assertEqual(len(names), 3)
