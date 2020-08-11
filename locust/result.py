# -*- coding: utf-8 -*-

from collections import OrderedDict
import logging


logger = logging.getLogger(__name__)


_STD_RESULTS = ["pass", "warning", "fail"]
RESULT_PASS, RESULT_WARN, RESULT_FAIL = _STD_RESULTS


class _Result(OrderedDict):
    """Hold a pass/warn/fail result for a test-run."""

    def __init__(self, value, reason):
        super().__init__(value=value, reason=reason)

    @property
    def value(self):
        return self['value']

    @property
    def reason(self):
        return self['reason']


def set_result(runner, value, reason):
    """Set a pass/warn/fail result for a test-run.

    Check that result does not go from worse to better.

    Arguments:
    runner: Locust master runner.
    value: One of RESULT_PASS, RESULT_WARN, RESULT_FAIL or any another value which you want to set as the result of the test.
        Using non standard values may adversely change Web UI look. If using non-standard results you may want to override the new_result
    reason: A description of what caused this value to be set.
    """

    # Check that ww don't forgat a bad result
    old_result = runner.result
    if old_result:
        try:
            old_index = _STD_RESULTS.index(old_result.value)
            new_index = _STD_RESULTS.index(value)
        except ValueError:
            logger.info("Non standard result values in use: '%s', '%s'. No check, we don't know the order.", old_result.value, value)
        else:
            if old_index >= new_index:
                logger.warning("NOT changing result from '%s' to '%s': '%s', we will not go from worse to better!", old_result.value, value, reason)
                return

        logger.info("Changing result from '%s' to '%s': '%s'.", old_result.value, value, reason)
    else:
        logger.info("Setting result to '%s': '%s'.", value, reason)

    runner.result = _Result(value, reason)
