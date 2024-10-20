from datetime import datetime, timezone

import humanfriendly


def format_utc_timestamp(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_safe_timestamp(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp).strftime("%Y-%m-%d %Hh%M")


def format_duration(start_unix_timestamp, end_unix_timestamp):
    return humanfriendly.format_timespan(end_unix_timestamp - start_unix_timestamp)
