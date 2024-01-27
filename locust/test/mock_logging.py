from __future__ import annotations

import logging

from typing import List, Union, Dict
from types import TracebackType

LogMessage = List[Union[str, Dict[str, TracebackType]]]


class MockedLoggingHandler(logging.Handler):
    debug: list[LogMessage] = []
    warning: list[LogMessage] = []
    info: list[LogMessage] = []
    error: list[LogMessage] = []
    critical: list[LogMessage] = []

    def emit(self, record):
        if record.exc_info:
            value = {"message": record.getMessage(), "exc_info": record.exc_info}
        else:
            value = record.getMessage()
        getattr(self.__class__, record.levelname.lower()).append(value)

    @classmethod
    def reset(cls):
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), list):
                setattr(cls, attr, [])
