def proper_round(val, digits=0) -> int | float:
    float_val = float(val)
    return round(float_val + 10 ** (-len(str(float_val)) - 1), digits)
