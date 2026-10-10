"""Tests for the request listener of locust.opentelemetry."""

from locust import events, opentelemetry
from locust import log as locust_log

import pytest

pytest.importorskip("opentelemetry.sdk")

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader


@pytest.fixture
def metric_reader(monkeypatch):
    """Run setup_opentelemetry against an in-memory metric reader and undo its global side effects afterwards."""
    reader = InMemoryMetricReader()
    meter_provider = MeterProvider(metric_readers=[reader])
    monkeypatch.setenv("OTEL_METRICS_EXPORTER", "console")
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "none")
    monkeypatch.setenv("OTEL_LOGS_EXPORTER", "none")
    monkeypatch.setattr(opentelemetry, "_setup_meter_provider", lambda resource, exporters: meter_provider)
    # the OpenTelemetry API only lets the global meter provider be set once per process
    monkeypatch.setattr(metrics, "set_meter_provider", lambda provider: None)
    monkeypatch.setattr(metrics, "get_meter", meter_provider.get_meter)
    # the instrumentations would call the patched get_meter with their own arguments and stay installed afterwards
    monkeypatch.setattr(opentelemetry, "_setup_auto_instrumentation", lambda: None)
    monkeypatch.setattr(opentelemetry, "request_names", set())
    monkeypatch.setattr(locust_log, "unhandled_greenlet_exception", False)
    request_handlers = list(events.request._handlers)
    init_handlers = list(events.init._handlers)

    assert opentelemetry.setup_opentelemetry("locustfile.py", None)
    yield reader

    events.request._handlers[:] = request_handlers
    events.init._handlers[:] = init_handlers
    meter_provider.shutdown()


def _sample_count(reader):
    count = 0
    data = reader.get_metrics_data()
    # the reader has no data at all until something has been recorded
    for resource_metrics in data.resource_metrics if data else []:
        for scope_metrics in resource_metrics.scope_metrics:
            for metric in scope_metrics.metrics:
                if metric.name == "locust.client.duration":
                    count += sum(point.count for point in metric.data.data_points)
    return count


def test_request_with_response_time_records_one_sample(metric_reader):
    events.request.fire(
        request_type="GET", name="/test", response_time=12.0, response_length=0, exception=None, context={}
    )

    assert _sample_count(metric_reader) == 1
    assert not locust_log.unhandled_greenlet_exception


def test_request_without_response_time_records_no_sample_and_does_not_raise(metric_reader):
    events.request.fire(
        request_type="GET", name="/test", response_time=None, response_length=0, exception=None, context={}
    )

    assert _sample_count(metric_reader) == 0
    assert not locust_log.unhandled_greenlet_exception
