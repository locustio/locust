import os
from optparse import OptionParser
import locust
from locust import config

from .testcases import LocustTestCase

class TestTaskSet(LocustTestCase):

    def tearDown(self):
        super(TestTaskSet, self).tearDown()
        config.register_config(config.LocustConfig())

    def test_default_config(self):
        self.assertIsInstance(config.locust_config(), config.LocustConfig)

    def test_configure(self):
        with locust.configure() as l_config:
            l_config.http_logging = 'DEBUG'
            l_config.custom_param = 'custom value'

        self.assertEqual(config.locust_config().http_logging, 'DEBUG')
        self.assertEqual(config.locust_config().custom_param, 'custom value')

    def test_composite_host(self):
        with locust.configure() as l_config:
            l_config.host = 'example.com'
            l_config.scheme = 'https'
            l_config.port = '8080'

        self.assertEqual(config.locust_config().host, 'https://example.com:8080')
        self.assertEqual(config.locust_config().socket_io, 'https://example.com:8080')

    def test_load_locusts(self):
        class MockOpts(object):
            locustfile = os.path.dirname(os.path.abspath(__file__)) + '/helpers/basic_locustfile'
        locusts = config.load_locusts(MockOpts, [])
        self.assertEqual(len(locusts), 1)

    def test_config_to_dict(self):
        with locust.configure() as l_config:
            l_config.http_logging = 'DEBUG'
            l_config.custom_param = 'custom value'
        config_dict = config.locust_config().to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertDictContainsSubset(
            {'http_logging': 'DEBUG', 'custom_param':'custom value'},
            config_dict
        )
        config_dict['http_logging'] = 'ERROR'
        self.assertEqual(config.locust_config().http_logging, 'DEBUG')

    def test_update_config_values(self):
        updates = {'host': 'example.com', 'port': None, 'master_host': 'http_new_host'}
        config.locust_config().update_config(updates)
        self.assertEqual(config.locust_config().host, 'http://example.com')
        self.assertEqual(config.locust_config().master_host, '127.0.0.1')
