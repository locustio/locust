import unittest
from locust.util.time import parse_timespan


class TestParseTimespan(unittest.TestCase):
    def test_parse_timespan_invalid_values(self):
        self.assertRaises(ValueError, parse_timespan, None)
        self.assertRaises(ValueError, parse_timespan, "")
        self.assertRaises(ValueError, parse_timespan, "q")
    
    def test_parse_timespan(self):
        self.assertEqual(7, parse_timespan("7"))
        self.assertEqual(7, parse_timespan("7s"))
        self.assertEqual(60, parse_timespan("1m"))
        self.assertEqual(7200, parse_timespan("2h"))
        self.assertEqual(3787, parse_timespan("1h3m7s"))
