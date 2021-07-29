# -*- coding: utf-8 -*-

"""
This is an example of a locustfile to use locust's builtin
web extensions to add custom start and edit fields on a loadtest.
"""

import os
from requests.auth import HTTPDigestAuth
from locust import HttpUser, TaskSet, task, web, between, events
from flask import Blueprint, render_template, jsonify, request

AUTH = None


class MyTaskSet(TaskSet):
    @task(2)
    def index(self):
        self.client.get("/", auth=globals()['AUTH'])

    @task(1)
    def stats(self):
        self.client.get("/stats/requests", auth=globals()['AUTH'])


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    tasks = [MyTaskSet]


#Set up the flask blueprint to extend the locust UI
path = os.path.dirname(os.path.abspath(__file__))
extend = Blueprint(
    "extend",
    "custom_test_start",
    static_folder=f"{path}/static/",
    static_url_path="/extend/static/",
    template_folder=f"{path}/templates/",
)


@events.init.add_listener
def locust_init(environment, **kwargs):
    if environment.web_ui:
        @extend.route("/custom-start")
        def custom_load_start():
            """
            Add a route to see your new changes to the Locust UI
            Navigate to this route to start and monitor a new test
            """
            environment.web_ui.update_template_args()
            return render_template("extend_test_start.html", **environment.web_ui.template_args)

        @extend.route("/customize-load-test", methods=["POST"])
        def customize_load_test():
            """
            Add a route to send your new form changes to so you can update the the load test
            """
            globals()['AUTH'] = HTTPDigestAuth(request.form['username'], request.form['password'])

            return jsonify({"post": "Success setting authentication"})

        #register our new routes and extended UI with the Locust UI
        environment.web_ui.app.register_blueprint(extend)



