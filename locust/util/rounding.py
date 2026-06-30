def proper_round(val, digits=0):
    # Convert to float first so that integer inputs like 0 produce '0.0'
    # (length 3) rather than '0' (length 1).  Using the shorter string gives
    # an epsilon of 10**(-2)=0.01 which is large enough to corrupt the result
    # when digits >= 2 (e.g. proper_round(0, 2) would return 0.01 instead of
    # 0.0 without this conversion).
    float_val = float(val)
    return round(float_val + 10 ** (-len(str(float_val)) - 1), digits)
