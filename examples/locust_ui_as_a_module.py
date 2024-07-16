"""
If you have decided to use the LocustUI as a module and expose your own React frontend, the
following example Locust file shows how you can configure Locust to point to your React build
output.
"""

from locust import HttpUser, between, events, task

import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
BUILD_PATH = os.path.join(ROOT_PATH, "dist")
STATIC_PATH = os.path.join(BUILD_PATH, "assets")


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)

    @task
    def index(self):
        self.client.get("/")


@events.init.add_listener
def locust_init(environment, **kwargs):
    webui = environment.web_ui
    if webui:
        webui.app.template_folder = BUILD_PATH
        webui.app.static_folder = STATIC_PATH
        webui.app.root_path = ROOT_PATH
        webui.webui_build_path = BUILD_PATH
