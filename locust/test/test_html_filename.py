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

    def test_process_html_filename_fractional_spawn_rate(self):
        mock_options = MagicMock()
        mock_options.num_users = 10
        mock_options.spawn_rate = 0.05
        mock_options.run_time = 60
        mock_options.html_file = "results_{r}.html"

        process_html_filename(mock_options)

        self.assertEqual(mock_options.html_file, "results_0.05.html")

    def test_process_html_filename_fractional_values_not_truncated(self):
        # -r 0.05, -r 0.2 and -r 0.5 must produce distinct file names, not all collapse to 0
        names = []
        for rate in (0.05, 0.2, 0.5):
            mock_options = MagicMock()
            mock_options.num_users = 10
            mock_options.spawn_rate = rate
            mock_options.run_time = 60
            mock_options.html_file = "results_10_{r}.html"
            process_html_filename(mock_options)
            names.append(mock_options.html_file)
        self.assertEqual(names, ["results_10_0.05.html", "results_10_0.2.html", "results_10_0.5.html"])

    def test_process_html_filename_integral_float_stays_integral(self):
        mock_options = MagicMock()
        mock_options.num_users = 10
        mock_options.spawn_rate = 2.0
        mock_options.run_time = 60
        mock_options.html_file = "results_{r}.html"

        process_html_filename(mock_options)

        self.assertEqual(mock_options.html_file, "results_2.html")

    def test_process_html_filename_None_arguments(self):
        mock_options = MagicMock()
        mock_options.num_users = 5
        # mock_options.spawn_rate = None
        mock_options.run_time = None
        mock_options.html_file = "report_u{u}_r{r}_t{t}.html"

        process_html_filename(mock_options)

        expected_filename = "report_u5_r1_t{t}.html"
        self.assertEqual(mock_options.html_file, expected_filename)
