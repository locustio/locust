def proper_round(val, digits=0):
    return round(val + 10 ** (-len(str(val)) - 1), digits)
