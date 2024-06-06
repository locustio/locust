from datetime import datetime, timezone


def format_utc_timestamp(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
