# This locust test script example will simulate a user
# browsing the Locust documentation on https://docs.locust.io/

import random
from locust import HttpLocust, TaskSquence, seq_task, task
from pyquery import PyQuery


class BrowseDocumentationSequence(TaskSquence):
    def on_start(self):
        self.urls_on_current_page = self.toc_urls

    # assume all users arrive at the index page
    @seq_task(1)
    def index_page(self):
        r = self.client.get("/")
        pq = PyQuery(r.content)
        link_elements = pq(".toctree-wrapper a.internal")
        self.toc_urls = [
            l.attrib["href"] for l in link_elements
        ]

    @seq_task(2)
    @task(50)
    def load_page(self, url=None):
        url = random.choice(self.toc_urls)
        r = self.client.get(url)
        pq = PyQuery(r.content)
        link_elements = pq("a.internal")
        self.urls_on_current_page = [
            l.attrib["href"] for l in link_elements
        ]

    @seq_task(3)
    @task(30)
    def load_sub_page(self):
        url = random.choice(self.urls_on_current_page)
        r = self.client.get(url)


class AwesomeUser(HttpLocust):
    task_set = BrowseDocumentationSequence
    host = "https://docs.locust.io/en/latest/"

    # we assume someone who is browsing the Locust docs,
    # generally has a quite long waiting time (between
    # 20 and 600 seconds), since there's a bunch of text
    # on each page
    min_wait = 20 * 1000
    max_wait = 600 * 1000
