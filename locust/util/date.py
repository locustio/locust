from datetime import datetime, timezone


def format_utc_timestamp(unix_timestamp):
    return datetime.fromtimestamp(int(unix_timestamp), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_safe_timestamp(unix_timestamp):
    return datetime.fromtimestamp(int(unix_timestamp)).strftime("%Y-%m-%d-%Hh%M")


def format_duration(start_time, end_time):
    seconds = int(end_time) - int(start_time)
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    time_parts = [(days, "day"), (hours, "hour"), (minutes, "minute"), (seconds, "second")]

    parts = [f"{value} {label}{'s' if value != 1 else ''}" for value, label in time_parts if value > 0]

    return " and ".join(filter(None, [", ".join(parts[:-1])] + parts[-1:])) if parts else "0 seconds"
