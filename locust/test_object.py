import time
import random
from enum import Enum

class TestSuite(object):
    def __init__(self, **kwargs):
        self._id = 'TSU-%s' % time.time()
        self._name = self.prepare_name(kwargs.get('name', None))
        self._test_cases = kwargs.get('test_cases', dict())
        self._path = kwargs.get('path', None)

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = self.prepare_name(value)

    @property
    def test_cases(self):
        return self._test_cases
    
    @test_cases.setter
    def test_cases(self, value):
        self._test_cases = value

    def set_test_case(self, test_case):
        try:
            test_case.test_suite_id = self._id
            self._test_cases[test_case.id] = test_case
        finally:
            return test_case

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def prepare_name(self, name):
        if name:
            x = []
            y = list(name)
            first_char = True
            for index, char in enumerate(y):
                if first_char:
                    first_char = False
                    x.append(char.upper())
                else:
                    if char.isupper():
                        if (y[index-1].islower() & y[index+2].islower()) or y[index+1].islower() or y[index-1].islower():
                            x.append(' %s' % char)
                        else:
                            x.append(char)
                    else:
                        x.append(char)

            return ''.join(x)

        return None


class TestCase(object):
    def __init__(self, **kwargs):
        self._id = 'TC-%s' % time.time()
        self._test_suite_id = kwargs.get('test_suite_id', None)
        self._name = self.prepare_name(kwargs.get('name', None))
        self._test_steps = kwargs.get('test_steps', [])
        self._status = kwargs.get('status', None)
        self._repetition_index = kwargs.get('repetition_index', None)
        self._time_start = kwargs.get('time_start', None)
        self._time_end = kwargs.get('time_end', None)
        self._group = kwargs.get('group', None)
        self.reason = kwargs.get('reason', None)

    def auto_set_status(self):
        new_status = TestStatus.SUCCESS
        for x in range(0,len(self._test_steps)):
            test_step = self._test_steps[x]
            if test_step.status.value > new_status.value :
                new_status = test_step.status
                self.reason = "%s on step %s [%s]" % (new_status.name,(x+1),test_step.name)
        self._time_start = self.test_steps[0]._time_start
        self._time_end = self.test_steps[len(self.test_steps)-1]._time_end
        self._status = new_status

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
    
    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        self._group = value

    @property
    def test_suite_id(self):
        return self._test_suite_id

    @test_suite_id.setter
    def test_suite_id(self, value):
        self._test_suite_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = self.prepare_name(value)

    @property
    def test_steps(self):
        return self._test_steps

    def append_test_step(self, test_step):
        self._test_steps.append(test_step)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def repetition_index(self):
        return self._repetition_index

    @repetition_index.setter
    def repetition_index(self, value):
        self._repetition_index = value

    @property
    def time_start(self):
        return self._time_start

    @time_start.setter
    def time_start(self, value):
        self._time_start = value

    @property
    def time_end(self):
        return self._time_end

    @time_end.setter
    def time_end(self, value):
        self._time_end = value

    def prepare_name(self, name):
        if name:
            x = []
            y = list(name)
            first_char = True
            for index, char in enumerate(y):
                if first_char:
                    x.append(char.upper())
                    first_char = False
                elif y[index-1] == '_':
                    x.append(' %s' % char.upper())
                elif char == '_':
                    continue
                else:
                    x.append(char)

            return ''.join(x)
            
        return None

class TestStep(object):
    def __init__(self, **kwargs):
        self._id = 'TST-%s' % time.time()
        self._test_case_id = kwargs.get('test_case_id', None)
        self._name = kwargs.get('name', None)
        self._status = kwargs.get('status', None)
        self._time_start = kwargs.get('time_start', None)
        self._time_end = kwargs.get('time_end', None)
        self._request = kwargs.get('request', None)
        self._response = kwargs.get('response', None)
        self.reason = kwargs.get('reason', None)
        if(kwargs.get('dummy', False) is True) :
            self._time_start = time.time()
            time.sleep(0.1)
            self._time_end = time.time()
            class dummyResponse(object):
                def __init__(self):
                    self.content = str(random.randint(1000000,1000000000))
                    self.headers = {
                        'content-type':'application/json/response',
                        'date':'Thu, 16 Jul 2019 04:19:02 GMT'
                    }
                    self.status_code = random.randint(100,600)
                    self.url = 'https:/%s' % (random.randint(0,1000))
                    class dummyRequest(object):
                        def __init__(self, url):
                            self.headers = {
                                'content-type':'application/json/request',
                                'date':'Thu, 12 Jul 2018 04:19:02 GMT'
                            }
                            self.method = 'GET'
                            self.body = None
                            self.url = url
                    self.request = dummyRequest(self.url)
            self._response = dummyResponse()

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def test_case_id(self):
        return self._test_case_id

    @test_case_id.setter
    def test_case_id(self, value):
        self._test_case_id = value
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def time_start(self):
        return self._time_start

    @time_start.setter
    def time_start(self, value):
        self._time_start = value

    @property
    def time_end(self):
        return self._time_end

    @time_end.setter
    def time_end(self, value):
        self._time_end = value

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        self._response = response

class TestStatus(Enum):
    SUCCESS, WARNING, FAIL = 0, 1, 2
