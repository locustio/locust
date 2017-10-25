import unittest
from pytest import raises
from locust.util.time import parse_timespan


class TestParseTimespan(unittest.TestCase):
    def test_parse_timespan_invalid_values(self):
        raises(ValueError, parse_timespan, None)
        raises(ValueError, parse_timespan, "")
        raises(ValueError, parse_timespan, "q")
    
    def test_parse_timespan(self):
        assert 7 == parse_timespan("7")
        assert 7 == parse_timespan("7s")
        assert 60 == parse_timespan("1m")
        assert 7200 == parse_timespan("2h")
        assert 3787 == parse_timespan("1h3m7s")
