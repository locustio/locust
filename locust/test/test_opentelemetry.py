"""Tests for locust.opentelemetry."""

from locust import events, opentelemetry

import pytest

pytest.importorskip("opentelemetry.sdk")

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

OVERFLOW_NAME = "Too many unique request names"


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
    request_handlers = list(events.request._handlers)
    init_handlers = list(events.init._handlers)

    assert opentelemetry.setup_opentelemetry("locustfile.py", None)
    yield reader

    events.request._handlers[:] = request_handlers
    events.init._handlers[:] = init_handlers
    meter_provider.shutdown()


def _fire(name):
    events.request.fire(
        request_type="GET", name=name, response_time=12.0, response_length=0, exception=None, context={}
    )


def _counts_by_name(reader):
    counts = {}
    for resource_metrics in reader.get_metrics_data().resource_metrics:
        for scope_metrics in resource_metrics.scope_metrics:
            for metric in scope_metrics.metrics:
                if metric.name != "locust.client.duration":
                    continue
                for point in metric.data.data_points:
                    name = point.attributes["name"]
                    counts[name] = counts.get(name, 0) + point.count
    return counts


def test_known_names_keep_their_label_after_the_cap_is_reached(metric_reader):
    names = [f"/endpoint_{i:02d}" for i in range(opentelemetry.MAX_REQUEST_NAMES + 5)]
    for _ in range(4):
        for name in names:
            _fire(name)

    expected = {name: 4 for name in names[: opentelemetry.MAX_REQUEST_NAMES]}
    expected[OVERFLOW_NAME] = 5 * 4
    assert _counts_by_name(metric_reader) == expected


def test_new_name_after_the_cap_goes_to_overflow_and_known_names_are_unaffected(metric_reader):
    known = [f"/endpoint_{i:02d}" for i in range(opentelemetry.MAX_REQUEST_NAMES)]
    for name in known:
        _fire(name)

    _fire("/one_too_many")
    _fire(known[0])
    _fire("/one_too_many")

    expected = {name: 1 for name in known}
    expected[known[0]] = 2
    expected[OVERFLOW_NAME] = 2
    assert _counts_by_name(metric_reader) == expected
