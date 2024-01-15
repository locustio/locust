def proper_round(val, digits=0):
    return round(val + 10 ** (-len(str(val)) - 1), digits)


def normalize_decimal(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    else:
        return value
