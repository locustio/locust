import time
import math


class LoadTestShaper(object):
    '''
    A simple load test shaper class used to control the shape of load generated
    during a load test.
    '''

    start_time = time.monotonic()

    def tick(self):
        '''
        Returns a tuple with 3 elements to control the running load test.

            user_count: Total user count
            hatch_rate: Hatch rate to use when changing total user count
            stop_test: A boolean to stop the test

        '''
        return (0, 0, True)


class StagesShaper(LoadTestShaper):
    '''
    A simply load test shaper class that can be passed a list of dicts that
    represent stages. Each stage has these keys:

        duration - When this many seconds pass the test is advanced to the next stage
        users - Total user count
        hatch_rate - Hatch rate
        stop - A boolean that can stop that test at a specific stage

    Arguments:

        stop_at_end - can be set to stop once all stages have run.
    '''
    def __init__(self, stages, stop_at_end=False):
        self.stages = sorted(stages, key=lambda k: k['duration'])
        self.stop_at_end = stop_at_end

    def tick(self):
        run_time = round(time.monotonic() - self.start_time)

        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['hatch_rate'], stage['stop'])
                self.last_stage = tick_data
                return tick_data

        if self.stop_at_end:
            print('Stopping test')
            return (0, 0, True)
        else:
            print('Continuing test')
            return self.last_stage



class StepLoadShaper(LoadTestShaper):
    '''
    A step load shaper.

    Arguments:

        step_time - Time between steps
        step_load - User increase amount at each step
        hatch_rate - Hatch rate to use at every step
        time_limit - Time limit in seconds
    '''
    def __init__(self, step_time, step_load, time_limit):
        self.step_time = step_time
        self.step_load = step_load
        self.hatch_rate = hatch_rate
        self.time_limit = time_limit

    def tick(self):
        run_time = round(time.monotonic() - self.start_time)
        current_step = math.floor(run_time / step_time) + 1
        return (current_step * self.step_load, self.hatch_rate, run_time > self.time_limit)
