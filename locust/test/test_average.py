import unittest
from core import Locust

class MyLocust(Locust):
    def _sleep(self, seconds):
        """ Bypass actual sleeping
        """
        pass

class MovingAverageTest(unittest.TestCase):
    """ This is not a unit test per se because it may fail ocassionally, which is perfectly ok since it deals with randomness.
        It is more for testing the expected behavior if using self.avg_wait in a Locust class and for feedback on the algorithm used.
    """

    def _setupLocust(self, min_wait, avg_wait, max_wait):
        locust = MyLocust()
        locust.min_wait = min_wait
        locust.avg_wait = avg_wait
        locust.max_wait = max_wait
        return locust

    def _wait(self, locust, count):
        for x in xrange(count):
            locust.wait()

    def _get_deviation(self, locust):
        return abs(locust._avg_wait - locust.avg_wait)

    def _get_max_deviation(self, locust, percent):
        return locust.avg_wait * (percent / 100.0)

    def _deviation(self, locust, percentage):
        deviation = self._get_deviation(locust)
        max_deviation = self._get_max_deviation(locust, percentage)
        print "Deviation: %.3f ms (%1.3f%%), max: %s ms (%s%%)" % (deviation, deviation / locust.avg_wait * 100.0, max_deviation, percentage)
        return deviation, max_deviation, percentage

    def _dump_stats(self, locust):
        print "Num waits: %d Wanted Average: %s Actual Average: %s" % (locust._avg_wait_ctr, locust.avg_wait, locust._avg_wait)

    def _assertion(self, locust, deviation, max_deviation, percentage):
        self._dump_stats(locust)
        self.assertTrue(deviation < max_deviation, msg="Deviation not within %s%% of wanted average" % percentage)

    def test_moving_average_100000(self):
        locust = self._setupLocust(3000, 140000, 20 * 60 * 1000) # 3 seconds, 140 seconds, 20 minutes
        print "Large"
        self._wait(locust, 100000)
        (deviation, max_deviation, percentage) = self._deviation(locust, 1.0)
        self._assertion(locust, deviation, max_deviation, percentage)

    def test_moving_average_100(self):
        # This test is actually expected to fail sometimes
        locust = self._setupLocust(3000, 140000, 20 * 60 * 1000) # 3 seconds, 140 seconds, 20 minutes
        print "Small"
        self._wait(locust, 100)
        (deviation, max_deviation, percentage) = self._deviation(locust, 5.0)
        self._assertion(locust, deviation, max_deviation, percentage)

    def test_omit_average(self):
        locust = self._setupLocust(3000, None, 20 * 60 * 1000) # 3 seconds, None, 20 minutes
        print "Omitted"
        self.assertEquals(None, locust.avg_wait)
        self.assertEquals(0, locust._avg_wait)
        self.assertEquals(0, locust._avg_wait_ctr)
        self._wait(locust, 100000)
        self.assertEquals(None, locust.avg_wait)
        self.assertEquals(0, locust._avg_wait)
        self.assertEquals(0, locust._avg_wait_ctr)


if __name__ == '__main__':
    unittest.main()