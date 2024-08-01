from __future__ import annotations

import csv
import hashlib
import json
import logging
import os
import signal
import time
from abc import abstractmethod
from collections import OrderedDict, defaultdict, namedtuple
from collections.abc import Iterable
from copy import copy
from html import escape
from itertools import chain
from types import FrameType
from typing import TYPE_CHECKING, Any, Callable, NoReturn, Protocol, TypedDict, TypeVar, cast

import gevent

from .event import Events
from .exception import CatchResponseError
from .util.date import format_utc_timestamp
from .util.rounding import proper_round

if TYPE_CHECKING:
    from .env import Environment
    from .runners import Runner

console_logger = logging.getLogger("locust.stats_logger")

"""Space in table for request name. Auto shrink it if terminal is small (<160 characters)"""
try:
    STATS_NAME_WIDTH = max(min(os.get_terminal_size()[0] - 80, 80), 0)
except OSError:  # not a real terminal
    STATS_NAME_WIDTH = 80

STATS_AUTORESIZE = True  # overwrite this if you dont want auto resize while running


class CSVWriter(Protocol):
    @abstractmethod
    def writerow(self, columns: Iterable[str | int | float]) -> None: ...


class StatsBaseDict(TypedDict):
    name: str
    method: str


class StatsEntryDict(StatsBaseDict):
    last_request_timestamp: float | None
    start_time: float
    num_requests: int
    num_none_requests: int
    num_failures: int
    total_response_time: int
    max_response_time: int
    min_response_time: int | None
    total_content_length: int
    response_times: dict[int, int]
    num_reqs_per_sec: dict[int, int]
    num_fail_per_sec: dict[int, int]


class StatsErrorDict(StatsBaseDict):
    error: str
    occurrences: int


class StatsHolder(Protocol):
    name: str
    method: str


S = TypeVar("S", bound=StatsHolder)


def resize_handler(signum: int, frame: FrameType | None):
    global STATS_NAME_WIDTH
    if STATS_AUTORESIZE:
        try:
            STATS_NAME_WIDTH = max(min(os.get_terminal_size()[0] - 80, 80), 0)
        except OSError:  # not a real terminal
            pass


try:
    signal.signal(signal.SIGWINCH, resize_handler)
except AttributeError:
    pass  # Windows doesn't have SIGWINCH

STATS_TYPE_WIDTH = 8

"""Default interval for how frequently results are written to console."""
CONSOLE_STATS_INTERVAL_SEC = 2

"""Default interval for how frequently results are written to history."""
HISTORY_STATS_INTERVAL_SEC = 5

"""Default interval for how frequently CSV files are written if this option is configured."""
CSV_STATS_INTERVAL_SEC = 1
CSV_STATS_FLUSH_INTERVAL_SEC = 5

"""
Default window size/resolution - in seconds - when calculating the current
response time percentile
"""
CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW = 10

CachedResponseTimes = namedtuple("CachedResponseTimes", ["response_times", "num_requests"])

PERCENTILES_TO_REPORT = [0.50, 0.66, 0.75, 0.80, 0.90, 0.95, 0.98, 0.99, 0.999, 0.9999, 1.0]

PERCENTILES_TO_STATISTICS = [0.95, 0.99]
PERCENTILES_TO_CHART = [0.5, 0.95]


class RequestStatsAdditionError(Exception):
    pass


def get_readable_percentiles(percentile_list: list[float]) -> list[str]:
    """
    Converts a list of percentiles from 0-1 fraction to 0%-100% view for using in console & csv reporting
    :param percentile_list: The list of percentiles in range 0-1
    :return: The list of string representation for each percentile in 0%-100% view
    """
    return [
        f"{int(percentile * 100) if (percentile * 100).is_integer() else round(100 * percentile, 6)}%"
        for percentile in percentile_list
    ]


def calculate_response_time_percentile(response_times: dict[int, int], num_requests: int, percent: float) -> int:
    """
    Get the response time that a certain number of percent of the requests
    finished within. Arguments:

    response_times: A StatsEntry.response_times dict
    num_requests: Number of request made (could be derived from response_times,
                  but we save some CPU cycles by using the value which we already store)
    percent: The percentile we want to calculate. Specified in range: 0.0 - 1.0
    """
    num_of_request = int(num_requests * percent)

    processed_count = 0
    for response_time in sorted(response_times.keys(), reverse=True):
        processed_count += response_times[response_time]
        if num_requests - processed_count <= num_of_request:
            return response_time
    # if all response times were None
    return 0


def diff_response_time_dicts(latest: dict[int, int], old: dict[int, int]) -> dict[int, int]:
    """
    Returns the delta between two {response_times:request_count} dicts.

    Used together with the response_times cache to get the response times for the
    last X seconds, which in turn is used to calculate the current response time
    percentiles.
    """
    new = {}
    for t in latest:
        if diff := latest[t] - old.get(t, 0):
            new[t] = diff
    return new


class EntriesDict(dict):
    def __init__(self, request_stats):
        self.request_stats = request_stats

    def __missing__(self, key):
        self[key] = StatsEntry(
            self.request_stats, key[0], key[1], use_response_times_cache=self.request_stats.use_response_times_cache
        )
        return self[key]


class RequestStats:
    """
    Class that holds the request statistics. Accessible in a User from self.environment.stats
    """

    def __init__(self, use_response_times_cache=True):
        """
        :param use_response_times_cache: The value of use_response_times_cache will be set for each StatsEntry()
                                         when they are created. Settings it to False saves some memory and CPU
                                         cycles which we can do on Worker nodes where the response_times_cache
                                         is not needed.
        """
        self.use_response_times_cache = use_response_times_cache
        self.entries: dict[tuple[str, str], StatsEntry] = EntriesDict(self)
        self.errors: dict[str, StatsError] = {}
        self.total = StatsEntry(self, "Aggregated", None, use_response_times_cache=self.use_response_times_cache)
        self.history = []

    @property
    def num_requests(self):
        return self.total.num_requests

    @property
    def num_none_requests(self):
        return self.total.num_none_requests

    @property
    def num_failures(self):
        return self.total.num_failures

    @property
    def last_request_timestamp(self):
        return self.total.last_request_timestamp

    @property
    def start_time(self):
        return self.total.start_time

    def log_request(self, method: str, name: str, response_time: int, content_length: int) -> None:
        self.total.log(response_time, content_length)
        self.entries[(name, method)].log(response_time, content_length)

    def log_error(self, method: str, name: str, error: Exception | str | None) -> None:
        self.total.log_error(error)
        self.entries[(name, method)].log_error(error)

        # store error in errors dict
        key = StatsError.create_key(method, name, error)
        entry = self.errors.get(key)
        if not entry:
            entry = StatsError(method, name, error)
            self.errors[key] = entry
        entry.occurred()

    def get(self, name: str, method: str) -> StatsEntry:
        """
        Retrieve a StatsEntry instance by name and method
        """
        return self.entries[(name, method)]

    def reset_all(self) -> None:
        """
        Go through all stats entries and reset them to zero
        """
        self.total.reset()
        self.errors = {}
        for r in self.entries.values():
            r.reset()
        self.history = []

    def clear_all(self) -> None:
        """
        Remove all stats entries and errors
        """
        self.total = StatsEntry(self, "Aggregated", "", use_response_times_cache=self.use_response_times_cache)
        self.entries = EntriesDict(self)
        self.errors = {}
        self.history = []

    def serialize_stats(self) -> list[StatsEntryDict]:
        return [
            e.get_stripped_report() for e in self.entries.values() if not (e.num_requests == 0 and e.num_failures == 0)
        ]

    def serialize_errors(self) -> dict[str, StatsErrorDict]:
        return {k: e.serialize() for k, e in self.errors.items()}


class StatsEntry:
    """
    Represents a single stats entry (name and method)
    """

    def __init__(self, stats: RequestStats | None, name: str, method: str, use_response_times_cache: bool = False):
        self.stats = stats
        self.name = name
        """ Name (URL) of this stats entry """
        self.method = method
        """ Method (GET, POST, PUT, etc.) """
        self.use_response_times_cache = use_response_times_cache
        """
        If set to True, the copy of the response_time dict will be stored in response_times_cache
        every second, and kept for 20 seconds (by default, will be CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW + 10).
        We can use this dict to calculate the *current*  median response time, as well as other response
        time percentiles.
        """
        self.num_requests: int = 0
        """ The number of requests made """
        self.num_none_requests: int = 0
        """ The number of requests made with a None response time (typically async requests) """
        self.num_failures: int = 0
        """ Number of failed request """
        self.total_response_time: int = 0
        """ Total sum of the response times """
        self.min_response_time: int | None = None
        """ Minimum response time """
        self.max_response_time: int = 0
        """ Maximum response time """
        self.num_reqs_per_sec: dict[int, int] = defaultdict(int)
        """ A {second => request_count} dict that holds the number of requests made per second """
        self.num_fail_per_sec: dict[int, int] = defaultdict(int)
        """ A (second => failure_count) dict that hold the number of failures per second """
        self.response_times: dict[int, int] = defaultdict(int)
        """
        A {response_time => count} dict that holds the response time distribution of all
        the requests.

        The keys (the response time in ms) are rounded to store 1, 2, ... 98, 99, 100, 110, 120, ... 980, 990, 1000,
        1100, 1200, ... 9800, 9900, 10_000, 11_000, 12_000 ... in order to save memory.

        This dict is used to calculate the median and percentile response times.
        """
        self.response_times_cache: OrderedDict[int, CachedResponseTimes] | None = None
        """
        If use_response_times_cache is set to True, this will be a {timestamp => CachedResponseTimes()}
        OrderedDict that holds a copy of the response_times dict for each of the last 20 seconds.
        """
        self.total_content_length: int = 0
        """ The sum of the content length of all the responses for this entry """
        self.start_time: float = 0.0
        """ Time of the first request for this entry """
        self.last_request_timestamp: float | None = None
        """ Time of the last request for this entry """
        self.reset()

    def reset(self):
        self.start_time = time.time()
        self.num_requests = 0
        self.num_none_requests = 0
        self.num_failures = 0
        self.total_response_time = 0
        self.response_times = defaultdict(int)
        self.min_response_time = None
        self.max_response_time = 0
        self.last_request_timestamp = None
        self.num_reqs_per_sec = defaultdict(int)
        self.num_fail_per_sec = defaultdict(int)
        self.total_content_length = 0
        if self.use_response_times_cache:
            self.response_times_cache = OrderedDict()
            self._cache_response_times(int(time.time()))

    def log(self, response_time: int, content_length: int) -> None:
        # get the time
        current_time = time.time()
        t = int(current_time)

        if self.use_response_times_cache and self.last_request_timestamp and t > int(self.last_request_timestamp):
            # see if we shall make a copy of the response_times dict and store in the cache
            self._cache_response_times(t - 1)

        self.num_requests += 1
        self._log_time_of_request(current_time)
        self._log_response_time(response_time)

        # increase total content-length
        self.total_content_length += content_length

    def _log_time_of_request(self, current_time: float) -> None:
        t = int(current_time)
        self.num_reqs_per_sec[t] += 1
        self.last_request_timestamp = current_time

    def _log_response_time(self, response_time: int) -> None:
        if response_time is None:
            self.num_none_requests += 1
            return

        self.total_response_time += response_time

        if self.min_response_time is None:
            self.min_response_time = response_time
        else:
            self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)

        # to avoid to much data that has to be transferred to the master node when
        # running in distributed mode, we save the response time rounded in a dict
        # so that 147 becomes 150, 3432 becomes 3400 and 58760 becomes 59000
        if response_time < 100:
            rounded_response_time = round(response_time)
        elif response_time < 1000:
            rounded_response_time = round(response_time, -1)
        elif response_time < 10000:
            rounded_response_time = round(response_time, -2)
        else:
            rounded_response_time = round(response_time, -3)

        # increase request count for the rounded key in response time dict
        self.response_times[rounded_response_time] += 1

    def log_error(self, error: Exception | str | None) -> None:
        self.num_failures += 1
        t = int(time.time())
        self.num_fail_per_sec[t] += 1

    @property
    def fail_ratio(self) -> float:
        try:
            return float(self.num_failures) / self.num_requests
        except ZeroDivisionError:
            if self.num_failures > 0:
                return 1.0
            else:
                return 0.0

    @property
    def avg_response_time(self) -> float:
        try:
            return float(self.total_response_time) / (self.num_requests - self.num_none_requests)
        except ZeroDivisionError:
            return 0.0

    @property
    def median_response_time(self) -> int:
        if not self.response_times:
            return 0
        median = median_from_dict(self.num_requests - self.num_none_requests, self.response_times) or 0

        # Since we only use two digits of precision when calculating the median response time
        # while still using the exact values for min and max response times, the following checks
        # makes sure that we don't report a median > max or median < min when a StatsEntry only
        # have one (or very few) really slow requests
        if median > self.max_response_time:
            median = self.max_response_time
        elif self.min_response_time is not None and median < self.min_response_time:
            median = self.min_response_time

        return median

    @property
    def current_rps(self) -> float:
        if self.stats is None or self.stats.last_request_timestamp is None:
            return 0
        slice_start_time = max(int(self.stats.last_request_timestamp) - 12, int(self.stats.start_time or 0))

        reqs: list[int | float] = [
            self.num_reqs_per_sec.get(t, 0) for t in range(slice_start_time, int(self.stats.last_request_timestamp) - 2)
        ]
        return avg(reqs)

    @property
    def current_fail_per_sec(self):
        if self.stats.last_request_timestamp is None:
            return 0
        slice_start_time = max(int(self.stats.last_request_timestamp) - 12, int(self.stats.start_time or 0))

        reqs = [
            self.num_fail_per_sec.get(t, 0) for t in range(slice_start_time, int(self.stats.last_request_timestamp) - 2)
        ]
        return avg(reqs)

    @property
    def total_rps(self):
        if not self.stats.last_request_timestamp or not self.stats.start_time:
            return 0.0
        try:
            return self.num_requests / (self.stats.last_request_timestamp - self.stats.start_time)
        except ZeroDivisionError:
            return 0.0

    @property
    def total_fail_per_sec(self):
        if not self.stats.last_request_timestamp or not self.stats.start_time:
            return 0.0
        try:
            return self.num_failures / (self.stats.last_request_timestamp - self.stats.start_time)
        except ZeroDivisionError:
            return 0.0

    @property
    def avg_content_length(self):
        try:
            return self.total_content_length / self.num_requests
        except ZeroDivisionError:
            return 0

    def extend(self, other: StatsEntry) -> None:
        """
        Extend the data from the current StatsEntry with the stats from another
        StatsEntry instance.
        """
        # save the old last_request_timestamp, to see if we should store a new copy
        # of the response times in the response times cache
        old_last_request_timestamp = self.last_request_timestamp

        if self.last_request_timestamp is not None and other.last_request_timestamp is not None:
            self.last_request_timestamp = max(self.last_request_timestamp, other.last_request_timestamp)
        elif other.last_request_timestamp is not None:
            self.last_request_timestamp = other.last_request_timestamp
        self.start_time = min(self.start_time, other.start_time)
        self.num_requests += other.num_requests
        self.num_none_requests += other.num_none_requests
        self.num_failures += other.num_failures
        self.total_response_time += other.total_response_time
        self.max_response_time = max(self.max_response_time, other.max_response_time)
        if self.min_response_time is not None and other.min_response_time is not None:
            self.min_response_time = min(self.min_response_time, other.min_response_time)
        elif other.min_response_time is not None:
            # this means self.min_response_time is None, so we can safely replace it
            self.min_response_time = other.min_response_time
        self.total_content_length += other.total_content_length

        for key in other.response_times:
            self.response_times[key] = self.response_times.get(key, 0) + other.response_times[key]
        for key in other.num_reqs_per_sec:
            self.num_reqs_per_sec[key] = self.num_reqs_per_sec.get(key, 0) + other.num_reqs_per_sec[key]
        for key in other.num_fail_per_sec:
            self.num_fail_per_sec[key] = self.num_fail_per_sec.get(key, 0) + other.num_fail_per_sec[key]

        if self.use_response_times_cache:
            # If we've entered a new second, we'll cache the response times. Note that there
            # might still be reports from other worker nodes - that contains requests for the same
            # time periods - that hasn't been received/accounted for yet. This will cause the cache to
            # lag behind a second or two, but since StatsEntry.current_response_time_percentile()
            # (which is what the response times cache is used for) uses an approximation of the
            # last 10 seconds anyway, it should be fine to ignore this.
            last_time = int(self.last_request_timestamp) if self.last_request_timestamp else None
            if last_time and last_time > (old_last_request_timestamp and int(old_last_request_timestamp) or 0):
                self._cache_response_times(last_time)

    def serialize(self) -> StatsEntryDict:
        return cast(StatsEntryDict, {key: getattr(self, key, None) for key in StatsEntryDict.__annotations__.keys()})

    @classmethod
    def unserialize(cls, data: StatsEntryDict) -> StatsEntry:
        """Return the unserialzed version of the specified dict"""
        obj = cls(None, data["name"], data["method"])
        valid_keys = StatsEntryDict.__annotations__.keys()

        for key, value in data.items():
            if key in ["name", "method"] or key not in valid_keys:
                continue

            setattr(obj, key, value)
        return obj

    def get_stripped_report(self) -> StatsEntryDict:
        """
        Return the serialized version of this StatsEntry, and then clear the current stats.
        """
        report = self.serialize()
        self.reset()
        return report

    def to_string(self, current=True) -> str:
        """
        Return the stats as a string suitable for console output. If current is True, it'll show
        the RPS and failure rate for the last 10 seconds. If it's false, it'll show the total stats
        for the whole run.
        """
        if current:
            rps = self.current_rps
            fail_per_sec = self.current_fail_per_sec
        else:
            rps = self.total_rps
            fail_per_sec = self.total_fail_per_sec
        return (
            "%-"
            + str(STATS_TYPE_WIDTH)
            + "s %-"
            + str((STATS_NAME_WIDTH - STATS_TYPE_WIDTH) + 4)
            + "s %7d %12s |%7d %7d %7d%7d | %7.2f %11.2f"
        ) % (
            (self.method and self.method + " " or ""),
            self.name,
            self.num_requests,
            "%d(%.2f%%)" % (self.num_failures, self.fail_ratio * 100),
            self.avg_response_time,
            self.min_response_time or 0,
            self.max_response_time,
            self.median_response_time or 0,
            rps or 0,
            fail_per_sec or 0,
        )

    def __str__(self) -> str:
        return self.to_string(current=True)

    def get_response_time_percentile(self, percent: float) -> int:
        """
        Get the response time that a certain number of percent of the requests
        finished within.

        Percent specified in range: 0.0 - 1.0
        """
        return calculate_response_time_percentile(self.response_times, self.num_requests, percent)

    def get_current_response_time_percentile(self, percent: float) -> int | None:
        """
        Calculate the *current* response time for a certain percentile. We use a sliding
        window of (approximately) the last 10 seconds (specified by CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW)
        when calculating this.
        """
        if not self.use_response_times_cache:
            raise ValueError(
                "StatsEntry.use_response_times_cache must be set to True if we should be able to calculate the _current_ response time percentile"
            )
        # First, we want to determine which of the cached response_times dicts we should
        # use to get response_times for approximately 10 seconds ago.
        t = int(time.time())
        # Since we can't be sure that the cache contains an entry for every second.
        # We'll construct a list of timestamps which we consider acceptable keys to be used
        # when trying to fetch the cached response_times. We construct this list in such a way
        # that it's ordered by preference by starting to add t-10, then t-11, t-9, t-12, t-8,
        # and so on
        acceptable_timestamps: list[int] = []
        acceptable_timestamps.append(t - CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW)
        for i in range(1, 9):
            acceptable_timestamps.append(t - CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW - i)
            acceptable_timestamps.append(t - CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW + i)

        cached: CachedResponseTimes | None = None
        if self.response_times_cache is not None:
            for ts in acceptable_timestamps:
                if ts in self.response_times_cache:
                    cached = self.response_times_cache[ts]
                    break

        if cached:
            # If we found an acceptable cached response times, we'll calculate a new response
            # times dict of the last 10 seconds (approximately) by diffing it with the current
            # total response times. Then we'll use that to calculate a response time percentile
            # for that timeframe
            return calculate_response_time_percentile(
                diff_response_time_dicts(self.response_times, cached.response_times),
                self.num_requests - cached.num_requests,
                percent,
            )
        # if time was not in response times cache window
        return None

    def percentile(self) -> str:
        if not self.num_requests:
            raise ValueError("Can't calculate percentile on url with no successful requests")

        tpl = f"%-{str(STATS_TYPE_WIDTH)}s %-{str(STATS_NAME_WIDTH)}s %8d {' '.join(['%6d'] * len(PERCENTILES_TO_REPORT))}"

        return tpl % (
            (self.method or "", self.name)
            + tuple(self.get_response_time_percentile(p) for p in PERCENTILES_TO_REPORT)
            + (self.num_requests,)
        )

    def _cache_response_times(self, t: int) -> None:
        if self.response_times_cache is None:
            self.response_times_cache = OrderedDict()

        self.response_times_cache[t] = CachedResponseTimes(
            response_times=copy(self.response_times),
            num_requests=self.num_requests,
        )

        # We'll use a cache size of CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW + 10 since - in the extreme case -
        # we might still use response times (from the cache) for t-CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW-10
        # to calculate the current response time percentile, if we're missing cached values for the subsequent
        # 20 seconds
        cache_size = CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW + 10

        if len(self.response_times_cache) > cache_size:
            # only keep the latest 20 response_times dicts
            for _ in range(len(self.response_times_cache) - cache_size):
                self.response_times_cache.popitem(last=False)

    def to_dict(self, escape_string_values=False):
        response_time_percentiles = {
            f"response_time_percentile_{percentile}": self.get_response_time_percentile(percentile)
            for percentile in PERCENTILES_TO_STATISTICS
        }

        return {
            "method": escape(self.method or "") if escape_string_values else self.method,
            "name": escape(self.name) if escape_string_values else self.name,
            "safe_name": escape(self.name, quote=False),
            "num_requests": self.num_requests,
            "num_failures": self.num_failures,
            "min_response_time": 0 if self.min_response_time is None else proper_round(self.min_response_time),
            "max_response_time": proper_round(self.max_response_time),
            "current_rps": self.current_rps,
            "current_fail_per_sec": self.current_fail_per_sec,
            "avg_response_time": self.avg_response_time,
            "median_response_time": self.median_response_time,
            "total_rps": self.total_rps,
            "total_fail_per_sec": self.total_fail_per_sec,
            **response_time_percentiles,
            "avg_content_length": self.avg_content_length,
        }


class StatsError:
    def __init__(self, method: str, name: str, error: Exception | str | None, occurrences: int = 0):
        self.method = method
        self.name = name
        self.error = error
        self.occurrences = occurrences

    @classmethod
    def parse_error(cls, error: Exception | str | None) -> str:
        if isinstance(error, str):
            string_error = error
        else:
            string_error = repr(error)
        target = "object at 0x"
        target_index = string_error.find(target)
        if target_index < 0:
            return string_error
        start = target_index + len(target) - 2
        end = string_error.find(">", start)
        if end < 0:
            return string_error
        hex_address = string_error[start:end]
        return string_error.replace(hex_address, "0x....")

    @classmethod
    def create_key(cls, method: str, name: str, error: Exception | str | None) -> str:
        key = f"{method}.{name}.{StatsError.parse_error(error)!r}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def occurred(self) -> None:
        self.occurrences += 1

    def to_name(self) -> str:
        error = self.error
        if isinstance(error, str):  # in distributed mode, all errors have been converted to strings
            if error.startswith("CatchResponseError("):
                # unwrap CatchResponseErrors
                length = len("CatchResponseError(")
                unwrapped_error = error[length:-1]
            else:
                unwrapped_error = error
        else:  # in standalone mode, errors are still objects
            if isinstance(error, CatchResponseError):
                # unwrap CatchResponseErrors
                unwrapped_error = error.args[0]
            else:
                unwrapped_error = repr(error)

        return f"{self.method} {self.name}: {unwrapped_error}"

    def serialize(self) -> StatsErrorDict:
        def _getattr(obj: StatsError, key: str, default: Any | None) -> Any | None:
            value = getattr(obj, key, default)

            if key in ["error"]:
                value = StatsError.parse_error(value)

            return value

        return cast(StatsErrorDict, {key: _getattr(self, key, None) for key in StatsErrorDict.__annotations__.keys()})

    @classmethod
    def unserialize(cls, data: StatsErrorDict) -> StatsError:
        return cls(data["method"], data["name"], data["error"], data["occurrences"])

    def to_dict(self, escape_string_values=False):
        return {
            "method": escape(self.method),
            "name": escape(self.name),
            "error": escape(self.parse_error(self.error)),
            "occurrences": self.occurrences,
        }


def avg(values: list[float | int]) -> float:
    return sum(values, 0.0) / max(len(values), 1)


def median_from_dict(total: int, count: dict[int, int]) -> int:
    """
    total is the number of requests made
    count is a dict {response_time: count}
    """
    pos = (total - 1) / 2
    for k in sorted(count.keys()):
        if pos < count[k]:
            return k
        pos -= count[k]

    return k


def setup_distributed_stats_event_listeners(events: Events, stats: RequestStats) -> None:
    def on_report_to_master(client_id: str, data: dict[str, Any]) -> None:
        data["stats"] = stats.serialize_stats()
        data["stats_total"] = stats.total.get_stripped_report()
        data["errors"] = stats.serialize_errors()
        stats.errors = {}

    def on_worker_report(client_id: str, data: dict[str, Any]) -> None:
        for stats_data in data["stats"]:
            entry = StatsEntry.unserialize(stats_data)
            request_key = (entry.name, entry.method)
            if request_key not in stats.entries:
                stats.entries[request_key] = StatsEntry(stats, entry.name, entry.method, use_response_times_cache=True)
            stats.entries[request_key].extend(entry)

        for error_key, error in data["errors"].items():
            if error_key not in stats.errors:
                stats.errors[error_key] = StatsError.unserialize(error)
            else:
                stats.errors[error_key].occurrences += error["occurrences"]

        stats.total.extend(StatsEntry.unserialize(data["stats_total"]))

    events.report_to_master.add_listener(on_report_to_master)
    events.worker_report.add_listener(on_worker_report)


def print_stats(stats: RequestStats, current=True) -> None:
    for line in get_stats_summary(stats, current):
        console_logger.info(line)
    console_logger.info("")


def print_stats_json(stats: RequestStats) -> None:
    print(json.dumps(stats.serialize_stats(), indent=4))


def get_stats_summary(stats: RequestStats, current=True) -> list[str]:
    """
    stats summary will be returned as list of string
    """
    name_column_width = (STATS_NAME_WIDTH - STATS_TYPE_WIDTH) + 4  # saved characters by compacting other columns
    summary = []
    summary.append(
        ("%-" + str(STATS_TYPE_WIDTH) + "s %-" + str(name_column_width) + "s %7s %12s |%7s %7s %7s%7s | %7s %11s")
        % ("Type", "Name", "# reqs", "# fails", "Avg", "Min", "Max", "Med", "req/s", "failures/s")
    )
    separator = f'{"-" * STATS_TYPE_WIDTH}|{"-" * (name_column_width)}|{"-" * 7}|{"-" * 13}|{"-" * 7}|{"-" * 7}|{"-" * 7}|{"-" * 7}|{"-" * 8}|{"-" * 11}'
    summary.append(separator)
    for key in sorted(stats.entries.keys()):
        r = stats.entries[key]
        summary.append(r.to_string(current=current))
    summary.append(separator)
    summary.append(stats.total.to_string(current=current))
    return summary


def print_percentile_stats(stats: RequestStats) -> None:
    for line in get_percentile_stats_summary(stats):
        console_logger.info(line)
    console_logger.info("")


def get_percentile_stats_summary(stats: RequestStats) -> list[str]:
    """
    Percentile stats summary will be returned as list of string
    """
    summary = ["Response time percentiles (approximated)"]
    headers = ("Type", "Name") + tuple(get_readable_percentiles(PERCENTILES_TO_REPORT)) + ("# reqs",)
    summary.append(
        (
            f"%-{str(STATS_TYPE_WIDTH)}s %-{str(STATS_NAME_WIDTH)}s %8s "
            f"{' '.join(['%6s'] * len(PERCENTILES_TO_REPORT))}"
        )
        % headers
    )
    separator = (
        f'{"-" * STATS_TYPE_WIDTH}|{"-" * STATS_NAME_WIDTH}|{"-" * 8}|{("-" * 6 + "|") * len(PERCENTILES_TO_REPORT)}'
    )[:-1]
    summary.append(separator)
    for key in sorted(stats.entries.keys()):
        r = stats.entries[key]
        if r.response_times:
            summary.append(r.percentile())
    summary.append(separator)

    if stats.total.response_times:
        summary.append(stats.total.percentile())
    return summary


def print_error_report(stats: RequestStats) -> None:
    if stats.errors:
        for line in get_error_report_summary(stats):
            console_logger.info(line)


def get_error_report_summary(stats) -> list[str]:
    summary = ["Error report"]
    summary.append("%-18s %-100s" % ("# occurrences", "Error"))
    separator = f'{"-" * 18}|{"-" * ((80 + STATS_NAME_WIDTH) - 19)}'
    summary.append(separator)
    for error in stats.errors.values():
        summary.append("%-18i %-100s" % (error.occurrences, error.to_name()))
    summary.append(separator)
    summary.append("")
    return summary


def stats_printer(stats: RequestStats) -> Callable[[], None]:
    def stats_printer_func() -> None:
        while True:
            print_stats(stats)
            gevent.sleep(CONSOLE_STATS_INTERVAL_SEC)

    return stats_printer_func


def sort_stats(stats: dict[Any, S]) -> list[S]:
    return [stats[key] for key in sorted(stats.keys())]


def update_stats_history(runner: Runner) -> None:
    stats = runner.stats
    current_response_time_percentiles = {
        f"response_time_percentile_{percentile}": stats.total.get_current_response_time_percentile(percentile) or 0
        for percentile in PERCENTILES_TO_CHART
    }

    r = {
        **current_response_time_percentiles,
        "time": format_utc_timestamp(time.time()),
        "current_rps": stats.total.current_rps or 0,
        "current_fail_per_sec": stats.total.current_fail_per_sec or 0,
        "total_avg_response_time": proper_round(stats.total.avg_response_time, digits=2),
        "user_count": runner.user_count or 0,
    }
    stats.history.append(r)


def stats_history(runner: Runner) -> None:
    """Save current stats info to history for charts of report."""
    while True:
        if not runner.stats.total.use_response_times_cache:
            break
        if runner.state != "stopped":
            update_stats_history(runner)

        gevent.sleep(HISTORY_STATS_INTERVAL_SEC)


class StatsCSV:
    """Write statistics to csv_writer stream."""

    def __init__(self, environment: Environment, percentiles_to_report: list[float]) -> None:
        self.environment = environment
        self.percentiles_to_report = percentiles_to_report

        self.percentiles_na = ["N/A"] * len(self.percentiles_to_report)

        self.requests_csv_columns = [
            "Type",
            "Name",
            "Request Count",
            "Failure Count",
            "Median Response Time",
            "Average Response Time",
            "Min Response Time",
            "Max Response Time",
            "Average Content Size",
            "Requests/s",
            "Failures/s",
        ] + get_readable_percentiles(self.percentiles_to_report)

        self.failures_columns = [
            "Method",
            "Name",
            "Error",
            "Occurrences",
        ]

        self.exceptions_columns = [
            "Count",
            "Message",
            "Traceback",
            "Nodes",
        ]

    def _percentile_fields(self, stats_entry: StatsEntry, use_current: bool = False) -> list[str] | list[int]:
        if not stats_entry.num_requests:
            return self.percentiles_na
        elif use_current:
            return [int(stats_entry.get_current_response_time_percentile(x) or 0) for x in self.percentiles_to_report]
        else:
            return [int(stats_entry.get_response_time_percentile(x) or 0) for x in self.percentiles_to_report]

    def requests_csv(self, csv_writer: CSVWriter) -> None:
        """Write requests csv with header and data rows."""
        csv_writer.writerow(self.requests_csv_columns)
        self._requests_data_rows(csv_writer)

    def _requests_data_rows(self, csv_writer: CSVWriter) -> None:
        """Write requests csv data row, excluding header."""
        stats = self.environment.stats
        for stats_entry in chain(sort_stats(stats.entries), [stats.total]):
            csv_writer.writerow(
                chain(
                    [
                        stats_entry.method,
                        stats_entry.name,
                        stats_entry.num_requests,
                        stats_entry.num_failures,
                        stats_entry.median_response_time,
                        stats_entry.avg_response_time,
                        stats_entry.min_response_time or 0,
                        stats_entry.max_response_time,
                        stats_entry.avg_content_length,
                        stats_entry.total_rps,
                        stats_entry.total_fail_per_sec,
                    ],
                    self._percentile_fields(stats_entry),
                )
            )

    def failures_csv(self, csv_writer: CSVWriter) -> None:
        csv_writer.writerow(self.failures_columns)
        self._failures_data_rows(csv_writer)

    def _failures_data_rows(self, csv_writer: CSVWriter) -> None:
        for stats_error in sort_stats(self.environment.stats.errors):
            csv_writer.writerow(
                [
                    stats_error.method,
                    stats_error.name,
                    StatsError.parse_error(stats_error.error),
                    stats_error.occurrences,
                ]
            )

    def exceptions_csv(self, csv_writer: CSVWriter) -> None:
        csv_writer.writerow(self.exceptions_columns)
        self._exceptions_data_rows(csv_writer)

    def _exceptions_data_rows(self, csv_writer: CSVWriter) -> None:
        if self.environment.runner is None:
            return

        for exc in self.environment.runner.exceptions.values():
            csv_writer.writerow([exc["count"], exc["msg"], exc["traceback"], ", ".join(exc["nodes"])])


class StatsCSVFileWriter(StatsCSV):
    """Write statistics to CSV files"""

    def __init__(
        self,
        environment: Environment,
        percentiles_to_report: list[float],
        base_filepath: str,
        full_history: bool = False,
    ):
        super().__init__(environment, percentiles_to_report)
        self.base_filepath = base_filepath
        self.full_history = full_history

        self.requests_csv_filehandle = open(self.base_filepath + "_stats.csv", "w")
        self.requests_csv_writer = csv.writer(self.requests_csv_filehandle)

        self.stats_history_csv_filehandle = open(self.stats_history_file_name(), "w")
        self.stats_history_csv_writer = csv.writer(self.stats_history_csv_filehandle)

        self.failures_csv_filehandle = open(self.base_filepath + "_failures.csv", "w")
        self.failures_csv_writer = csv.writer(self.failures_csv_filehandle)
        self.failures_csv_data_start: int = 0

        self.exceptions_csv_filehandle = open(self.base_filepath + "_exceptions.csv", "w")
        self.exceptions_csv_writer = csv.writer(self.exceptions_csv_filehandle)
        self.exceptions_csv_data_start: int = 0

        self.stats_history_csv_columns = [
            "Timestamp",
            "User Count",
            "Type",
            "Name",
            "Requests/s",
            "Failures/s",
            *get_readable_percentiles(self.percentiles_to_report),
            "Total Request Count",
            "Total Failure Count",
            "Total Median Response Time",
            "Total Average Response Time",
            "Total Min Response Time",
            "Total Max Response Time",
            "Total Average Content Size",
        ]

    def __call__(self) -> None:
        self.stats_writer()

    def stats_writer(self) -> NoReturn:
        """Writes all the csv files for the locust run."""

        # Write header row for all files and save position for non-append files
        self.requests_csv_writer.writerow(self.requests_csv_columns)
        requests_csv_data_start = self.requests_csv_filehandle.tell()

        self.stats_history_csv_writer.writerow(self.stats_history_csv_columns)

        self.failures_csv_writer.writerow(self.failures_columns)
        self.failures_csv_data_start = self.failures_csv_filehandle.tell()

        self.exceptions_csv_writer.writerow(self.exceptions_columns)
        self.exceptions_csv_data_start = self.exceptions_csv_filehandle.tell()

        # Continuously write date rows for all files
        last_flush_time: float = 0.0
        while True:
            now = time.time()

            self.requests_csv_filehandle.seek(requests_csv_data_start)
            self._requests_data_rows(self.requests_csv_writer)
            self.requests_csv_filehandle.truncate()

            self._stats_history_data_rows(self.stats_history_csv_writer, now)

            self.failures_csv_filehandle.seek(self.failures_csv_data_start)
            self._failures_data_rows(self.failures_csv_writer)
            self.failures_csv_filehandle.truncate()

            self.exceptions_csv_filehandle.seek(self.exceptions_csv_data_start)
            self._exceptions_data_rows(self.exceptions_csv_writer)
            self.exceptions_csv_filehandle.truncate()

            if now - last_flush_time > CSV_STATS_FLUSH_INTERVAL_SEC:
                self.requests_flush()
                self.stats_history_flush()
                self.failures_flush()
                self.exceptions_flush()
                last_flush_time = now

            gevent.sleep(CSV_STATS_INTERVAL_SEC)

    def _stats_history_data_rows(self, csv_writer: CSVWriter, now: float) -> None:
        """
        Write CSV rows with the *current* stats. By default only includes the
        Aggregated stats entry, but if self.full_history is set to True, a row for each entry will
        will be included.

        Note that this method differs from the other methods as it appends time-stamped data to the file, whereas the other methods overwrites the data.
        """

        stats = self.environment.stats
        timestamp = int(now)
        stats_entries: list[StatsEntry] = []
        if self.full_history:
            stats_entries = sort_stats(stats.entries)

        for stats_entry in chain(stats_entries, [stats.total]):
            csv_writer.writerow(
                chain(
                    (
                        timestamp,
                        self.environment.runner.user_count if self.environment.runner is not None else 0,
                        stats_entry.method or "",
                        stats_entry.name,
                        f"{stats_entry.current_rps:2f}",
                        f"{stats_entry.current_fail_per_sec:2f}",
                    ),
                    self._percentile_fields(stats_entry, use_current=self.full_history),
                    (
                        stats_entry.num_requests,
                        stats_entry.num_failures,
                        stats_entry.median_response_time,
                        stats_entry.avg_response_time,
                        stats_entry.min_response_time or 0,
                        stats_entry.max_response_time,
                        stats_entry.avg_content_length,
                    ),
                )
            )

    def requests_flush(self) -> None:
        self.requests_csv_filehandle.flush()

    def stats_history_flush(self) -> None:
        self.stats_history_csv_filehandle.flush()

    def failures_flush(self) -> None:
        self.failures_csv_filehandle.flush()

    def exceptions_flush(self) -> None:
        self.exceptions_csv_filehandle.flush()

    def close_files(self) -> None:
        self.requests_csv_filehandle.close()
        self.stats_history_csv_filehandle.close()
        self.failures_csv_filehandle.close()
        self.exceptions_csv_filehandle.close()

    def stats_history_file_name(self) -> str:
        return self.base_filepath + "_stats_history.csv"
