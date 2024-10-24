import decimal
import numbers
import re
from datetime import datetime, timedelta, timezone


def format_utc_timestamp(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_safe_timestamp(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp).strftime("%Y-%m-%d-%Hh%M")


def format_duration(start_unix_timestamp, end_unix_timestamp):
    """
    Format a timespan between two timestamps as a human readable string.
    Taken from xolox/python-humanfriendly

    :param start_unix_timestamp: Start timestamp.
    :param end_unix_timestamp: End timestamp.

    """
    # Common time units, used for formatting of time spans.
    time_units = (
        dict(divider=1e-9, singular="nanosecond", plural="nanoseconds", abbreviations=["ns"]),
        dict(divider=1e-6, singular="microsecond", plural="microseconds", abbreviations=["us"]),
        dict(divider=1e-3, singular="millisecond", plural="milliseconds", abbreviations=["ms"]),
        dict(divider=1, singular="second", plural="seconds", abbreviations=["s", "sec", "secs"]),
        dict(divider=60, singular="minute", plural="minutes", abbreviations=["m", "min", "mins"]),
        dict(divider=60 * 60, singular="hour", plural="hours", abbreviations=["h"]),
        dict(divider=60 * 60 * 24, singular="day", plural="days", abbreviations=["d"]),
        dict(divider=60 * 60 * 24 * 7, singular="week", plural="weeks", abbreviations=["w"]),
        dict(divider=60 * 60 * 24 * 7 * 52, singular="year", plural="years", abbreviations=["y"]),
    )

    num_seconds = coerce_seconds(
        end_unix_timestamp - start_unix_timestamp,
    )
    if num_seconds < 60:
        # Fast path.
        return pluralize(round_number(num_seconds), "second")
    else:
        # Slow path.
        result = []
        num_seconds = decimal.Decimal(str(num_seconds))
        relevant_units = list(reversed(time_units[3:]))
        for unit in relevant_units:
            # Extract the unit count from the remaining time.
            divider = decimal.Decimal(str(unit["divider"]))
            count = num_seconds / divider
            num_seconds %= divider
            # Round the unit count appropriately.
            if unit != relevant_units[-1]:
                # Integer rounding for all but the smallest unit.
                count = int(count)
            else:
                # Floating point rounding for the smallest unit.
                count = round_number(count)
            # Only include relevant units in the result.
            if count not in (0, "0"):
                result.append(pluralize(count, unit["singular"], unit["plural"]))
        if len(result) == 1:
            # A single count/unit combination.
            return result[0]
        else:
            # Format the timespan in a readable way.
            return concatenate(result[:3])


def coerce_seconds(value):
    """
    Coerce a value to the number of seconds.

    :param value: An :class:`int`, :class:`float` or
                  :class:`datetime.timedelta` object.
    :returns: An :class:`int` or :class:`float` value.

    When `value` is a :class:`datetime.timedelta` object the
    :meth:`~datetime.timedelta.total_seconds()` method is called.
    """
    if isinstance(value, timedelta):
        return value.total_seconds()
    if not isinstance(value, numbers.Number):
        msg = "Failed to coerce value to number of seconds! (%r)"
        raise ValueError(format(msg, value))
    return value


def round_number(count, keep_width=False):
    """
    Round a floating point number to two decimal places in a human friendly format.

    :param count: The number to format.
    :param keep_width: :data:`True` if trailing zeros should not be stripped,
                       :data:`False` if they can be stripped.
    :returns: The formatted number as a string. If no decimal places are
              required to represent the number, they will be omitted.

    The main purpose of this function is to be used by functions like
    :func:`format_length()`, :func:`format_size()` and
    :func:`format_timespan()`.

    Here are some examples:

    >>> from humanfriendly import round_number
    >>> round_number(1)
    '1'
    >>> round_number(math.pi)
    '3.14'
    >>> round_number(5.001)
    '5'
    """
    text = "%.2f" % float(count)
    if not keep_width:
        text = re.sub("0+$", "", text)
        text = re.sub(r"\.$", "", text)
    return text


def concatenate(items, conjunction="and", serial_comma=False):
    """
    Concatenate a list of items in a human friendly way.

    :param items:

        A sequence of strings.

    :param conjunction:

        The word to use before the last item (a string, defaults to "and").

    :param serial_comma:

        :data:`True` to use a `serial comma`_, :data:`False` otherwise
        (defaults to :data:`False`).

    :returns:

        A single string.

    >>> from humanfriendly.text import concatenate
    >>> concatenate(["eggs", "milk", "bread"])
    'eggs, milk and bread'

    .. _serial comma: https://en.wikipedia.org/wiki/Serial_comma
    """
    items = list(items)
    if len(items) > 1:
        final_item = items.pop()
        formatted = ", ".join(items)
        if serial_comma:
            formatted += ","
        return " ".join([formatted, conjunction, final_item])
    elif items:
        return items[0]
    else:
        return ""


def pluralize(count, singular, plural=None):
    """
    Combine a count with the singular or plural form of a word.

    :param count: The count (a number).
    :param singular: The singular form of the word (a string).
    :param plural: The plural form of the word (a string or :data:`None`).
    :returns: The count and singular or plural word concatenated (a string).

    See :func:`pluralize_raw()` for the logic underneath :func:`pluralize()`.
    """
    return "%s %s" % (count, pluralize_raw(count, singular, plural))


def pluralize_raw(count, singular, plural=None):
    """
    Select the singular or plural form of a word based on a count.

    :param count: The count (a number).
    :param singular: The singular form of the word (a string).
    :param plural: The plural form of the word (a string or :data:`None`).
    :returns: The singular or plural form of the word (a string).

    When the given count is exactly 1.0 the singular form of the word is
    selected, in all other cases the plural form of the word is selected.

    If the plural form of the word is not provided it is obtained by
    concatenating the singular form of the word with the letter "s". Of course
    this will not always be correct, which is why you have the option to
    specify both forms.
    """
    if not plural:
        plural = singular + "s"
    return singular if float(count) == 1.0 else plural
