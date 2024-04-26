"""
This is an example of a locustfile that uses Locust's built in event and web
UI extension hooks to track the sum of Varnish cache hit/miss headers
and display them in the web UI.
"""

from locust import HttpUser, TaskSet, between, events, task, web

import json
import os
from html import escape
from time import time

from flask import Blueprint, jsonify, make_response, render_template, request


class MyTaskSet(TaskSet):
    @task(1)
    def miss(l):
        """MISS X-Cache header"""
        l.client.get("/response-headers?X-Cache=MISS")

    @task(2)
    def hit(l):
        """HIT X-Cache header"""
        l.client.get("/response-headers?X-Cache=HIT")

    @task(1)
    def noinfo(l):
        """No X-Cache header (noinfo counter)"""
        l.client.get("/")


class WebsiteUser(HttpUser):
    host = "http://httpbin.org"
    wait_time = between(2, 5)
    tasks = [MyTaskSet]


# This example is based on the Varnish hit/miss headers (https://docs.varnish-software.com/tutorials/hit-miss-logging/).
# It could easily be customised for matching other caching systems, CDN or custom headers.
CACHE_HEADER = "X-Cache"

cache_stats = {}

page_stats = {"hit": 0, "miss": 0, "noinfo": 0}

path = os.path.dirname(os.path.abspath(__file__))
extend = Blueprint(
    "extend",
    "extend_web_ui",
    static_folder=f"{path}/static/",
    static_url_path="/extend/static/",
    template_folder=f"{path}/templates/",
)


@events.init.add_listener
def locust_init(environment, **kwargs):
    """
    Load data on locust init.
    :param environment:
    :param kwargs:
    :return:
    """

    if environment.web_ui:
        # this code is only run on the master node (the web_ui instance doesn't exist on workers)

        def get_cache_stats():
            """
            This is used by the Cache tab in the
            extended web UI to show the stats.
            """
            if cache_stats:
                stats_tmp = []

                for name, inner_stats in cache_stats.items():
                    stats_tmp.append(
                        {
                            "name": name,
                            "safe_name": escape(name, quote=False),
                            "hit": inner_stats["hit"],
                            "miss": inner_stats["miss"],
                            "noinfo": inner_stats["noinfo"],
                        }
                    )

                # Truncate the total number of stats and errors displayed since a large number
                # of rows will cause the app to render extremely slowly.
                return stats_tmp[:500]
            return cache_stats

        @environment.web_ui.app.after_request
        def extend_stats_response(response):
            if request.path != "/stats/requests":
                return response

            # extended_stats contains the data where extended_tables looks for its data: "cache-statistics"
            response.set_data(
                json.dumps(
                    {**response.json, "extended_stats": [{"key": "cache-statistics", "data": get_cache_stats()}]}
                )
            )

            return response

        @extend.route("/extend")
        def extend_web_ui():
            """
            Add route to access the extended web UI with our new tab.
            """
            # ensure the template_args are up to date before using them
            environment.web_ui.update_template_args()
            # set the static paths to use the modern ui
            environment.web_ui.set_static_modern_ui()

            return render_template(
                "index.html",
                template_args={
                    **environment.web_ui.template_args,
                    # extended_tabs and extended_tables keys must match.
                    "extended_tabs": [{"title": "Cache statistics", "key": "cache-statistics"}],
                    "extended_tables": [
                        {
                            "key": "cache-statistics",
                            "structure": [
                                {"key": "name", "title": "Name"},
                                {"key": "hit", "title": "Hit"},
                                {"key": "miss", "title": "Miss"},
                                {"key": "noinfo", "title": "No Info"},
                            ],
                        }
                    ],
                    "extended_csv_files": [{"href": "/cache/csv", "title": "Download Cache statistics CSV"}],
                },
            )

        @extend.route("/cache/csv")
        def request_cache_csv():
            """
            Add route to enable downloading of cache stats as CSV
            """
            response = make_response(cache_csv())
            file_name = f"cache-{time()}.csv"
            disposition = f"attachment;filename={file_name}"
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response

        def cache_csv():
            """Returns the cache stats as CSV."""
            rows = [",".join(['"Name"', '"hit"', '"miss"', '"noinfo"'])]

            if cache_stats:
                for name, stats in cache_stats.items():
                    rows.append(f'"{name}",' + ",".join(str(v) for v in stats.values()))
            return "\n".join(rows)

        # register our new routes and extended UI with the Locust web UI
        environment.web_ui.app.register_blueprint(extend)


@events.request.add_listener
def on_request(name, response, exception, **kwargs):
    """
    Event handler that get triggered on every request
    """

    cache_stats.setdefault(name, page_stats.copy())

    if CACHE_HEADER not in response.headers:
        cache_stats[name]["noinfo"] += 1
    elif response.headers[CACHE_HEADER] == "HIT":
        cache_stats[name]["hit"] += 1
    elif response.headers[CACHE_HEADER] == "MISS":
        cache_stats[name]["miss"] += 1


@events.report_to_master.add_listener
def on_report_to_master(client_id, data):
    """
    This event is triggered on the worker instances every time a stats report is
    to be sent to the locust master. It will allow us to add our extra cache
    data to the dict that is being sent, and then we clear the local stats in the worker.
    """
    global cache_stats
    data["cache_stats"] = cache_stats
    cache_stats = {}


@events.worker_report.add_listener
def on_worker_report(client_id, data):
    """
    This event is triggered on the master instance when a new stats report arrives
    from a worker. Here we just add the cache to the master's aggregated stats dict.
    """
    for name in data["cache_stats"]:
        cache_stats.setdefault(name, page_stats.copy())
        for stat_name, value in data["cache_stats"][name].items():
            cache_stats[name][stat_name] += value


@events.reset_stats.add_listener
def on_reset_stats():
    """
    Event handler that get triggered on click of web UI Reset Stats button
    """
    global cache_stats
    cache_stats = {}
