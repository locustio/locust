import logging


class MockedLoggingHandler(logging.Handler):
    debug = []
    warning = []
    info = []
    error = []
    critical = []

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
