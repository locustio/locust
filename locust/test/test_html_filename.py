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
