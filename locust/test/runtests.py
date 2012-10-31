from gevent import monkey
monkey.patch_all(thread=False)

import unittest
from test_locust_class import TestLocustClass, TestSubLocust, TestWebLocustClass, TestCatchResponse
from test_stats import TestRequestStats, TestRequestStatsWithWebserver, TestInspectLocust
from test_runners import TestMasterRunner

if __name__ == '__main__':
	unittest.main()
