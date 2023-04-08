from locust import HttpUser, task, events
import logging
import requests
from bs4 import BeautifulSoup
import pytest_check as check

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        page = self.client.get("/")
        soup = BeautifulSoup(page.content, 'html.parser')
        class_name = 'mw-page-title-main'
        element_type = 'span'
        web_element = soup.find(element_type, {"class": class_name})
        actual_text = web_element.get_text()
        expected_text = 'Wiki'
        assert(actual_text, expected_text)
        assert actual_text == expected_text


@events.quitting.add_listener
def _(environment, **kw):
    if environment.stats.total.fail_ratio > 0.01:
        logging.error("Test failed due to failure ratio > 1%")
        environment.process_exit_code = 1
    elif environment.stats.total.avg_response_time > 200:
        logging.error("Test failed due to average response time ratio > 200 ms")
        environment.process_exit_code = 1
    elif environment.stats.total.get_response_time_percentile(0.95) > 800:
        logging.error("Test failed due to 95th percentile response time > 800 ms")
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0


'''
comments

cd locust-load-testing/library/test_group/

locus
 
https://storefront:FERfol2021@sfcc-qa.ferguson.com


'''
