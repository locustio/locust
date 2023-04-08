"""
This is an example of a locustfile that uses Locust's built in event hooks to
track the sum of the content-length header in all successful HTTP responses
"""

from locust import HttpUser, TaskSet, task, web, between
from locust import events


class MyTaskSet(TaskSet):
    @task(2)
    def index(l):
        l.client.get("/")

    @task(1)
    def stats(l):
        l.client.get("/stats/requests")


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    tasks = [MyTaskSet]


stats = {"content-length": 0}


@events.init.add_listener
def locust_init(environment, **kwargs):
    """
    We need somewhere to store the stats.

    On the master node stats will contain the aggregated sum of all content-lengths,
    while on the worker nodes this will be the sum of the content-lengths since the
    last stats report was sent to the master
    """
    if environment.web_ui:
        # this code is only run on the master node (the web_ui instance doesn't exist on workers)
        @environment.web_ui.app.route("/content-length")
        def total_content_length():
            """
            Add a route to the Locust web app, where we can see the total content-length
            """
            return "Total content-length received: %i" % stats["content-length"]


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """
    Event handler that get triggered on every request.
    """
    stats["content-length"] += response_length


@events.report_to_master.add_listener
def on_report_to_master(client_id, data):
    """
    This event is triggered on the worker instances every time a stats report is
    to be sent to the locust master. It will allow us to add our extra content-length
    data to the dict that is being sent, and then we clear the local stats in the worker.
    """
    data["content-length"] = stats["content-length"]
    stats["content-length"] = 0


@events.worker_report.add_listener
def on_worker_report(client_id, data):
    """
    This event is triggered on the master instance when a new stats report arrives
    from a worker. Here we just add the content-length to the master's aggregated
    stats dict.
    """
    stats["content-length"] += data["content-length"]
