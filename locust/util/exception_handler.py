import time
import logging

logger = logging.getLogger(__name__)

def retry(delays=(1, 3, 5),
          exception=Exception):
    def decorator(function):
        def wrapper(*args, **kwargs):
            cnt = 0
            for delay in delays + (None,):
                try:
                    return function(*args, **kwargs)
                except exception:
                    if delay is None:
                        logger.info("Retry failed after %d times." % ( cnt ) )
                        raise
                    else:
                        cnt += 1
                        logger.info("Exception found on retry %d: -- retry after %ds" % ( cnt, delay ) )
                        time.sleep(delay)
        return wrapper
    return decorator