import logging


class MockedLoggingHandler(logging.Handler):
    debug = []
    warning = []
    info = []
    error = []

    def emit(self, record):
        getattr(self.__class__, record.levelname.lower()).append(record.getMessage())

    @classmethod
    def reset(cls):
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), list):
                setattr(cls, attr, [])
