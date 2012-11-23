from gevent import monkey
monkey.patch_all(thread=False)

import unittest

from test_locust_class import TestTaskSet, TestWebLocustClass, TestCatchResponse
from test_stats import TestRequestStats, TestRequestStatsWithWebserver, TestInspectLocust
from test_runners import TestMasterRunner
from test_taskratio import TestTaskRatio
from test_client import TestHttpSession

if __name__ == '__main__':
	unittest.main()
