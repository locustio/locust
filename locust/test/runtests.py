from gevent import monkey
monkey.patch_all(thread=False)

import unittest

from test_locust_class import TestTaskSet, TestWebLocustClass, TestCatchResponse
from test_stats import TestRequestStats, TestRequestStatsWithWebserver, TestInspectLocust
from test_runners import TestMasterRunner, TestMessageSerializing
from test_taskratio import TestTaskRatio
from test_client import TestHttpSession
from test_web import TestWebUI
from test_average import MovingAverageTest

if __name__ == '__main__':
    unittest.main()
