# This locust test script example will simulate a user
# browsing the Locust documentation on https://docs.locust.io/

import random
from locust import HttpUser, SequentialTaskSet, task, between
from pyquery import PyQuery


class BrowseDocumentationSequence(SequentialTaskSet):
    def on_start(self):
        self.urls_on_current_page = self.toc_urls = None

    # assume all users arrive at the index page
    @task
    def index_page(self):
        r = self.client.get("/")
        pq = PyQuery(r.content)
        link_elements = pq(".toctree-wrapper a.internal")
        self.toc_urls = [l.attrib["href"] for l in link_elements]
        # it is fine to do multiple requests in a single task, you dont need SequentialTaskSet for that
        self.client.get("/favicon.ico")

    @task
    def load_page(self, url=None):
        url = random.choice(self.toc_urls)
        r = self.client.get(url)
        pq = PyQuery(r.content)
        link_elements = pq("a.internal")
        self.urls_on_current_page = [l.attrib["href"] for l in link_elements]

    @task
    def load_sub_page(self):
        url = random.choice(self.urls_on_current_page)
        r = self.client.get(url)


class AwesomeUser(HttpUser):
    tasks = [BrowseDocumentationSequence]
    host = "https://docs.locust.io/en/latest/"

    # we assume someone who is browsing the Locust docs,
    # generally has a quite long waiting time (between
    # 20 and 600 seconds), since there's a bunch of text
    # on each page
    wait_time = between(20, 600)
