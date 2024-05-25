from datetime import datetime


def format_utc_timestamp(unix_timestamp):
    return datetime.utcfromtimestamp(unix_timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")
