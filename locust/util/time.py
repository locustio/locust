import re
from datetime import timedelta

def parse_timespan(time_str):
    """
    Parse a string representing a time span and return the number of seconds.
    Valid formats are: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.
    """
    if not time_str:
        raise ValueError("Invalid time span format")
    
    if re.match(r'^\d+$', time_str):
        # if an int is specified we assume they want seconds
        return int(time_str)
    
    timespan_regex = re.compile(r'((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    parts = timespan_regex.match(time_str)
    if not parts:
        raise ValueError("Invalid time span format. Valid formats: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.")
    parts = parts.groupdict()
    time_params = {name:int(value) for name, value in parts.items() if value}
    if not time_params:
        raise ValueError("Invalid time span format. Valid formats: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.")
    return int(timedelta(**time_params).total_seconds())
            
