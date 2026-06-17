from locust.util.rounding import proper_round
from locust.util.timespan import parse_timespan

import unittest


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

    def test_parse_timespan_rejects_trailing_junk(self):
        # Strings with digits after a valid pattern but missing a unit suffix
        # must raise ValueError; before the fix they were silently accepted.
        self.assertRaises(ValueError, parse_timespan, "1h2m3")   # trailing '3' has no unit
        self.assertRaises(ValueError, parse_timespan, "2h3m5s6")  # trailing '6' has no unit
        self.assertRaises(ValueError, parse_timespan, "1h30")    # '30' has no unit
        self.assertRaises(ValueError, parse_timespan, "30m45")   # '45' has no unit


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
