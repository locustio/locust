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
        Returns a tuple with 2 elements to control the running load test:

            user_count -- Total user count
            spawn_rate -- Number of users to start/stop per second when changing number of users

        If `None` is returned then the running load test will be stopped.

        """

        return None
