import unittest
from locust.util.timespan import parse_timespan
from locust.util.rounding import proper_round


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


class TestRounding(unittest.TestCase):
    def test_rounding_down(self):
        self.assertEqual(1, proper_round(1.499999999))
        self.assertEqual(5, proper_round(5.499999999))
        self.assertEqual(2, proper_round(2.05))
        self.assertEqual(3, proper_round(3.05))

    def test_rounding_up(self):
        self.assertEqual(2, proper_round(1.5))
        self.assertEqual(3, proper_round(2.5))
        self.assertEqual(4, proper_round(3.5))
        self.assertEqual(5, proper_round(4.5))
        self.assertEqual(6, proper_round(5.5))
