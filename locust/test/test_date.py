from locust.util.date import format_duration, format_safe_timestamp, format_utc_timestamp

from datetime import datetime

import pytest

dates_checks = [
    {
        "datetime": datetime(2023, 10, 1, 12, 0, 0),
        "utc_timestamp": "2023-10-01T10:00:00Z",
        "safe_timestamp": "2023-10-01-12h00",
        "duration": "0 seconds",
    },
    {
        "datetime": datetime(2023, 10, 1, 12, 0, 30),
        "utc_timestamp": "2023-10-01T10:00:30Z",
        "safe_timestamp": "2023-10-01-12h00",
        "duration": "30 seconds",
    },
    {
        "datetime": datetime(2023, 10, 1, 12, 45, 0),
        "utc_timestamp": "2023-10-01T10:45:00Z",
        "safe_timestamp": "2023-10-01-12h45",
        "duration": "45 minutes",
    },
    {
        "datetime": datetime(2023, 10, 1, 15, 0, 0),
        "utc_timestamp": "2023-10-01T13:00:00Z",
        "safe_timestamp": "2023-10-01-15h00",
        "duration": "3 hours",
    },
    {
        "datetime": datetime(2023, 10, 4, 12, 0, 0),
        "utc_timestamp": "2023-10-04T10:00:00Z",
        "safe_timestamp": "2023-10-04-12h00",
        "duration": "3 days",
    },
    {
        "datetime": datetime(2023, 10, 3, 15, 45, 30),
        "utc_timestamp": "2023-10-03T13:45:30Z",
        "safe_timestamp": "2023-10-03-15h45",
        "duration": "2 days, 3 hours, 45 minutes and 30 seconds",
    },
    {
        "datetime": datetime(2023, 10, 2, 13, 1, 1),
        "utc_timestamp": "2023-10-02T11:01:01Z",
        "safe_timestamp": "2023-10-02-13h01",
        "duration": "1 day, 1 hour, 1 minute and 1 second",
    },
    {
        "datetime": datetime(2023, 10, 1, 15, 30, 45),
        "utc_timestamp": "2023-10-01T13:30:45Z",
        "safe_timestamp": "2023-10-01-15h30",
        "duration": "3 hours, 30 minutes and 45 seconds",
    },
    {
        "datetime": datetime(2023, 10, 2, 12, 30, 45),
        "utc_timestamp": "2023-10-02T10:30:45Z",
        "safe_timestamp": "2023-10-02-12h30",
        "duration": "1 day, 30 minutes and 45 seconds",
    },
    {
        "datetime": datetime(2023, 10, 2, 12, 0, 45),
        "utc_timestamp": "2023-10-02T10:00:45Z",
        "safe_timestamp": "2023-10-02-12h00",
        "duration": "1 day and 45 seconds",
    },
]


@pytest.mark.parametrize("check", dates_checks)
@pytest.mark.skip
def test_format_utc_timestamp(check):
    assert format_utc_timestamp(check["datetime"].timestamp()) == check["utc_timestamp"]


@pytest.mark.parametrize("check", dates_checks)
@pytest.mark.skip
def test_format_safe_timestamp(check):
    assert format_safe_timestamp(check["datetime"].timestamp()) == check["safe_timestamp"]


@pytest.mark.parametrize("check", dates_checks)
@pytest.mark.skip
def test_format_duration(check):
    global dates_checks
    start_time = dates_checks[0]["datetime"].timestamp()
    end_time = check["datetime"].timestamp()
    assert format_duration(start_time, end_time) == check["duration"]
