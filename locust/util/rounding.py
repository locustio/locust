def proper_round(val, digits=0):
    val = float(val)
    return round(val + 10 ** (-len(str(val)) - 1), digits)
