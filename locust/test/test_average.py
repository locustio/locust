import unittest
from locust.core import Locust, TaskSet
from testcases import WebserverTestCase


class MovingAverageTest(WebserverTestCase):
    """ This is not a unit test per se because it may fail ocassionally, which is perfectly ok since it deals with randomness.
        It is more for testing the expected behavior if using self.avg_wait in a taskset class and for feedback on the algorithm used.
    """

    def get_task_set(self, min_wait, avg_wait, max_wait):
        class MyLocust(Locust):
            host = 'http://127.0.0.1:%s' % self.port
            min_wait = 1
            max_wait = 1

        taskset = TaskSet(MyLocust())
        taskset._sleep = lambda seconds: None
        taskset.min_wait = min_wait
        taskset.avg_wait = avg_wait
        taskset.max_wait = max_wait
        return taskset

    def _wait(self, taskset, count):
        for x in xrange(count):
            taskset.wait()

    def _get_deviation(self, taskset):
        return abs(taskset._avg_wait - taskset.avg_wait)

    def _get_max_deviation(self, taskset, percent):
        return taskset.avg_wait * (percent / 100.0)

    def _deviation(self, taskset, percentage):
        deviation = self._get_deviation(taskset)
        max_deviation = self._get_max_deviation(taskset, percentage)
        print "Deviation: %.3f ms (%1.3f%%), max: %s ms (%s%%)" % (deviation, deviation / taskset.avg_wait * 100.0, max_deviation, percentage)
        return deviation, max_deviation, percentage

    def _dump_stats(self, taskset):
        print "Num waits: %d Wanted Average: %s Actual Average: %s" % (taskset._avg_wait_ctr, taskset.avg_wait, taskset._avg_wait)

    def _assertion(self, taskset, deviation, max_deviation, percentage):
        self._dump_stats(taskset)
        self.assertTrue(deviation < max_deviation, msg="Deviation not within %s%% of wanted average" % percentage)

    def test_moving_average_100000(self):
        taskset = self.get_task_set(3000, 140000, 20 * 60 * 1000)  # 3 seconds, 140 seconds, 20 minutes
        self._wait(taskset, 100000)
        (deviation, max_deviation, percentage) = self._deviation(taskset, 1.0)
        self._assertion(taskset, deviation, max_deviation, percentage)

    def test_moving_average_100(self):
        # This test is actually expected to fail sometimes
        taskset = self.get_task_set(3000, 140000, 20 * 60 * 1000)  # 3 seconds, 140 seconds, 20 minutes
        self._wait(taskset, 100)
        (deviation, max_deviation, percentage) = self._deviation(taskset, 5.0)
        self._assertion(taskset, deviation, max_deviation, percentage)

    def test_omit_average(self):
        taskset = self.get_task_set(3000, None, 20 * 60 * 1000)  # 3 seconds, None, 20 minutes
        self.assertEquals(None, taskset.avg_wait)
        self.assertEquals(0, taskset._avg_wait)
        self.assertEquals(0, taskset._avg_wait_ctr)
        self._wait(taskset, 100000)
        self.assertEquals(None, taskset.avg_wait)
        self.assertEquals(0, taskset._avg_wait)
        self.assertEquals(0, taskset._avg_wait_ctr)


if __name__ == '__main__':
    unittest.main()