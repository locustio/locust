import atexit
import csv
import os
import sys
from datetime import datetime

import gevent
import requests

from .exception import CatchResponseError
from .runners import MasterRunner, WorkerRunner

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")


class InfluxExporter:
    def __init__(self, environment):
        if not INFLUXDB_URL or not INFLUXDB_TOKEN or not INFLUXDB_ORG:
            sys.stderr.write(
                "Locust was set to export stats but INFLUXDB_URL, INFLUXDB_URL, or INFLUXDB_ORG were not set as env variables. Please ensure the variables are set or remove the exporter flag.\n"
            )
            sys.exit(1)

        from influxdb_client import BucketsApi, InfluxDBClient
        from influxdb_client.client.write_api import SYNCHRONOUS

        self._client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG,
        )
        self._BucketsApi = BucketsApi
        self.stat_entries = {}
        self._points = []
        self._environment = environment
        self._environment.events.request.add_listener(self.on_request)
        self._environment.events.test_start.add_listener(self.on_test_start)
        self._environment.events.test_stop.add_listener(self.on_test_stop)
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
        self._query_api = self._client.query_api()

        self._greenlets = []

        atexit.register(self.on_exit)

    def _create_bucket(self):
        buckets_api = self._BucketsApi(self._client)
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
        bucket_name = f"locust_test_{current_time}"

        try:
            bucket = buckets_api.create_bucket(bucket_name=bucket_name)
            return bucket.name
        except Exception as e:
            print(e)
            sys.stderr.write(
                "Could not create InfluxDB bucket. Please ensure the INFLUXDB_URL has access to create new buckets.\n"
            )
            sys.exit(1)

    def _queue_point(self, measurement, tags={}, fields={}):
        point = {"measurement": measurement, "tags": tags, "fields": fields, "time": datetime.utcnow().isoformat()}
        self._points.append(point)

    def _write_points(self):
        while True:
            # Copy and clear queue so only new points are sent each cycle
            points = self._points.copy()
            self._points.clear()

            if points:
                self._write_api.write(record=points, bucket=self._bucket)

            gevent.sleep(0.5)

    def _log_user_count(self):
        while True:
            user_count = self._environment.runner.user_count

            self._queue_point(
                "user_count",
                fields={"user_count": user_count},
            )

            gevent.sleep(2)

    def on_exit(self):
        for greenlet in self._greenlets:
            greenlet.kill()

    def register(self, stat_entries):
        self.stat_entries = stat_entries

    def on_test_start(self, environment):
        self._bucket = self._create_bucket()

        if environment.runner and not isinstance(environment.runner, WorkerRunner):
            self._greenlets.append(gevent.spawn(self._log_user_count))

        self._greenlets.append(gevent.spawn(self._write_points))

    def on_test_stop(self, environment):
        self.on_exit()

    def on_request(
        self,
        request_type,
        name,
        response_time,
        response_length,
        exception,
        context,
        start_time=None,
        url=None,
        **kwargs,
    ):
        fields = {
            "response_time": response_time,
            "content_length": response_length,
        }

        if exception:
            if isinstance(exception, CatchResponseError):
                fields["exception"] = str(exception)
            else:
                try:
                    fields["exception"] = repr(exception)
                except AttributeError:
                    fields["exception"] = f"{exception.__class__} (and it has no string representation)"
        else:
            fields["exception"] = None

        self._queue_point(
            "request",
            tags={"name": name, "method": request_type},
            fields=fields,
        )
