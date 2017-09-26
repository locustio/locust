import os
from optparse import OptionParser
import locust
from locust import config

from .testcases import LocustTestCase

class TestTaskSet(LocustTestCase):

    def test_default_config(self):
        self.assertTrue(isinstance(config.locust_config, config.LocustConfig))

    def test_configure(self):
        with locust.configure() as l_config:
            l_config.http_logging = 'DEBUG'
            l_config.custom_param = 'custom value'

        self.assertTrue(config.locust_config.http_logging == 'DEBUG')
        self.assertTrue(config.locust_config.custom_param == 'custom value')

    def test_composite_host(self):
        with locust.configure() as l_config:
            l_config.host = 'example.com'
            l_config.scheme = 'https'
            l_config.port = '8080'

        self.assertTrue(config.locust_config.host == 'https://example.com:8080')
        self.assertTrue(config.locust_config.web_socket == 'https://example.com:8080')

    def test_load_locusts(self):
        class MockOpts(object):
            locustfile = os.path.dirname(os.path.abspath(__file__)) + '/helpers/basic_locustfile'
        locusts = config.load_locusts(MockOpts, [])
        self.assertTrue(len(locusts) == 1)

