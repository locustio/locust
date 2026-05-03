"""
Per-request CSV logger for Locust.

Hooks into the ``request`` event and appends one row per completed request to a
CSV file.  Useful for post-run analysis that requires individual data-points
rather than the aggregated statistics provided by the built-in
``--csv`` flag.

Usage::

    from locust import HttpUser, task, events
    from locust.contrib.csv_request_logger import CsvRequestLogger

    logger = CsvRequestLogger("results/requests.csv")

    @events.init.add_listener
    def on_locust_init(environment, **kwargs):
        logger.register(environment)

    class MyUser(HttpUser):
        @task
        def index(self):
            self.client.get("/")

The CSV file is created (or truncated) when :meth:`CsvRequestLogger.register`
is called and closed when the ``quitting`` event fires.

CSV columns
-----------
``timestamp``
    Unix timestamp (seconds, float) at which the request was sent.
``request_type``
    HTTP method or custom protocol name (e.g. ``GET``, ``POST``, ``WS``).
``name``
    URL path / request name as reported to Locust stats.
``response_time_ms``
    Response time in **milliseconds** (float, rounded to 2 dp).
``response_length``
    Response body size in bytes (int).
``status_code``
    HTTP status code (int).  ``0`` when the request failed before a response
    was received (e.g. connection error or custom failure).
``exception``
    String representation of the exception if the request failed, else empty.
"""

import csv
import io
import logging
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from locust.env import Environment
    from locust.stats import CSVWriter

logger = logging.getLogger(__name__)

#: Column headers written to the CSV file.
CSV_COLUMNS = (
    "timestamp",
    "request_type",
    "name",
    "response_time_ms",
    "response_length",
    "status_code",
    "exception",
)


def _status_code(response: Any, exception: Any) -> int:
    """Extract the HTTP status code from a response object.

    Returns ``0`` when no response is available (connection errors, custom
    ``ResponseContextManager`` failures, non-HTTP protocols, etc.).
    """
    if exception is not None and response is None:
        return 0
    try:
        code = int(response.status_code)
        return code
    except (AttributeError, TypeError, ValueError):
        return 0


class CsvRequestLogger:
    """Listens to Locust's ``request`` event and writes one CSV row per request.

    Parameters
    ----------
    filepath:
        Path to the output CSV file.  Parent directories must already exist.
        If the file exists it will be **overwritten** at the start of each run.
    flush_interval:
        Number of rows to buffer before flushing to disk.  Use ``1`` for
        immediate write-through (safest for crash recovery), or a larger value
        for better performance on high-RPS tests.  Defaults to ``1``.
    """

    def __init__(self, filepath: str, *, flush_interval: int = 1) -> None:
        self.filepath = filepath
        self.flush_interval = max(1, flush_interval)

        self._filehandle: io.TextIOWrapper | None = None
        self._writer: CSVWriter | None = None
        self._pending: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, environment: "Environment") -> None:
        """Attach this logger to *environment*'s event hooks.

        Must be called once, typically inside an ``@events.init`` listener.
        """
        environment.events.request.add_listener(self._on_request)
        environment.events.quitting.add_listener(self._on_quitting)
        self._open()
        logger.debug("CsvRequestLogger: writing per-request log to %s", self.filepath)

    def close(self) -> None:
        """Flush and close the underlying file handle.

        Safe to call multiple times.
        """
        if self._filehandle is not None and not self._filehandle.closed:
            self._filehandle.flush()
            self._filehandle.close()
            logger.debug("CsvRequestLogger: closed %s", self.filepath)
        self._filehandle = None
        self._writer = None
        self._pending = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _open(self) -> None:
        """Open (or re-open) the CSV file and write the header row."""
        self.close()
        self._filehandle = open(self.filepath, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._filehandle)
        self._writer.writerow(CSV_COLUMNS)
        self._filehandle.flush()

    def _on_request(
        self,
        *,
        request_type: str,
        name: str,
        response_time: float,
        response_length: int,
        exception: Any = None,
        response: Any = None,
        start_time: float | None = None,
        context: Any = None,
        **kwargs: Any,
    ) -> None:
        """Event handler — called by Locust for every completed request."""
        if self._writer is None:
            return

        ts = start_time if start_time is not None else time.time()
        status_code = _status_code(response, exception)
        exc_str = str(exception) if exception is not None else ""

        self._writer.writerow(
            [
                round(ts, 6),
                request_type,
                name,
                round(response_time, 2),
                response_length,
                status_code,
                exc_str,
            ]
        )

        self._pending += 1
        if self._pending >= self.flush_interval:
            self._filehandle.flush()  # type: ignore[union-attr]
            self._pending = 0

    def _on_quitting(self, **kwargs: Any) -> None:
        """Flush and close when Locust shuts down."""
        self.close()
