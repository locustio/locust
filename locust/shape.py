import time


class LoadTestShape(object):
    """
    A simple load test shape class used to control the shape of load generated
    during a load test.
    """

    start_time = time.monotonic()

    def reset_time(self):
        """
        Resets start time back to 0
        """
        self.start_time = time.monotonic()

    def get_run_time(self):
        """
        Calculates run time in seconds of the load test
        """
        return time.monotonic() - self.start_time

    def tick(self):
        """
        Returns a tuple with 3 elements to control the running load test.

            user_count -- Total user count
            hatch_rate -- Hatch rate to use when changing total user count
            stop_test -- A boolean to stop the test

        """
        run_time = self.get_run_time()

        return (0, 0, True)
