from locust import events

import logging
import os
import socket
from urllib.parse import urlparse

from ._version import __version__

logger = logging.getLogger(__name__)
MAX_REQUEST_NAMES = 20
request_names: set[str] = set()


def setup_opentelemetry(locustfile: str, profile: str | None) -> bool:
    try:
        from opentelemetry import _logs, metrics, trace
        from opentelemetry.sdk.resources import Resource
    except ImportError:
        logger.error("OpenTelemetry SDK is not installed, opentelemetry not enabled. Run 'pip install locust[otel]'")
        return False

    traces_exporters = {e.strip().lower() for e in os.getenv("OTEL_TRACES_EXPORTER", "otlp").split(",") if e.strip()}
    metrics_exporters = {e.strip().lower() for e in os.getenv("OTEL_METRICS_EXPORTER", "otlp").split(",") if e.strip()}
    logs_exporters = {e.strip().lower() for e in os.getenv("OTEL_LOGS_EXPORTER", "otlp").split(",") if e.strip()}

    if traces_exporters == {"none"} and metrics_exporters == {"none"} and logs_exporters == {"none"}:
        logger.info("No OpenTelemetry exporters configured, opentelemetry not enabled")
        return False

    resource = Resource.create(
        {
            "service.name": os.getenv("OTEL_SERVICE_NAME", "locust"),
            "service.version": __version__,
            "host.name": socket.gethostname(),
            "filename": locustfile,
            "profile": profile or "",
        }
    )

    if traces_exporters:
        tracer_provider = _setup_tracer_provider(resource, traces_exporters)
        trace.set_tracer_provider(tracer_provider)

    if metrics_exporters:
        meter_provider = _setup_meter_provider(resource, metrics_exporters)
        metrics.set_meter_provider(meter_provider)
        ttlb_histogram = metrics.get_meter("locust").create_histogram(
            "locust.client.duration", unit="s", description="Time to last byte for requests"
        )

        @events.request.add_listener
        def on_request(name, response_time, exception, **kwargs):
            if len(request_names) < MAX_REQUEST_NAMES:
                request_names.add(name)
                attributes = {"name": name}
            else:
                attributes = {"name": "Too many unique request names"}

            if exception:
                attributes["error.type"] = exception.__class__.__name__

            ttlb_histogram.record(response_time / 1000.0, attributes=attributes)

    if logs_exporters:
        logger_provider = _setup_logger_provider(resource, logs_exporters)
        _logs.set_logger_provider(logger_provider)

    _setup_auto_instrumentation()

    logger.debug("OpenTelemetry configured!")
    return True


def _setup_tracer_provider(resource, traces_exporters):
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor

    tracer_provider = TracerProvider(resource=resource)

    for exporter in traces_exporters:
        if exporter == "otlp":
            protocol = (
                os.getenv("OTEL_EXPORTER_OTLP_TRACES_PROTOCOL", os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc"))
                .lower()
                .strip()
            )
            try:
                if protocol == "grpc":
                    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                elif protocol == "http/protobuf" or protocol == "http":
                    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
                else:
                    logger.warning(
                        f"Unknown OpenTelemetry otlp exporter protocol '{protocol}'. Use 'grpc' or 'http/protobuf'"
                    )
                    continue
            except ImportError:
                logger.warning(
                    f"OpenTelemetry otlp exporter for '{protocol}' is not available. Please install the required package: opentelemetry-exporter-otlp-proto-{'grpc' if protocol == 'grpc' else 'http'}"
                )
                continue

            tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
            logger.debug("Configured traces exporter: otlp")

        elif exporter == "console":
            tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
            logger.debug("Configured traces exporter: console")

        elif exporter == "none":
            continue

        else:
            logger.warning(f"Unknown traces exporter '{exporter}'. Ignored")

    return tracer_provider


def _setup_meter_provider(resource, metrics_exporters):
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

    metric_readers = []

    for exporter in metrics_exporters:
        if exporter == "otlp":
            protocol = (
                os.getenv("OTEL_EXPORTER_OTLP_METRICS_PROTOCOL", os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc"))
                .lower()
                .strip()
            )
            try:
                if protocol == "grpc":
                    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
                elif protocol == "http/protobuf" or protocol == "http":
                    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
                else:
                    logger.warning(
                        f"Unknown OpenTelemetry otlp exporter protocol '{protocol}'. Use 'grpc' or 'http/protobuf'"
                    )
                    continue
            except ImportError:
                logger.warning(
                    f"OpenTelemetry otlp exporter for '{protocol}' is not available. Please install the required package: opentelemetry-exporter-otlp-proto-{'grpc' if protocol == 'grpc' else 'http'}"
                )
                continue

            metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
            metric_readers.append(metric_reader)
            logger.debug("Configured metrics exporter: otlp")

        elif exporter == "prometheus":
            # TODO: Add support for Prometheus metrics exporter
            logger.warning("Prometheus metrics exporter is not yet implemented!")

        elif exporter == "console":
            metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
            metric_readers.append(metric_reader)
            logger.debug("Configured metrics exporter: console")

        elif exporter == "none":
            continue

        else:
            logger.warning(f"Unknown metrics exporter '{exporter}'. Ignored")

    return MeterProvider(resource=resource, metric_readers=metric_readers)


def _setup_logger_provider(resource, logs_exporters):
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import (
        BatchLogRecordProcessor,
        ConsoleLogRecordExporter,
        SimpleLogRecordProcessor,
    )

    logger_provider = LoggerProvider(resource=resource)

    for exporter in logs_exporters:
        if exporter == "otlp":
            protocol = (
                os.getenv("OTEL_EXPORTER_OTLP_LOGS_PROTOCOL", os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc"))
                .lower()
                .strip()
            )
            try:
                if protocol == "grpc":
                    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
                elif protocol == "http/protobuf" or protocol == "http":
                    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
                else:
                    logger.warning(
                        f"Unknown OpenTelemetry otlp exporter protocol '{protocol}'. Use 'grpc' or 'http/protobuf'"
                    )
                    continue
            except ImportError:
                logger.warning(
                    f"OpenTelemetry otlp exporter for '{protocol}' is not available. Please install the required package: opentelemetry-exporter-otlp-proto-{'grpc' if protocol == 'grpc' else 'http'}"
                )
                continue

            logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
            logger.debug("Configured logs exporter: otlp")

        elif exporter == "console":
            logger_provider.add_log_record_processor(SimpleLogRecordProcessor(ConsoleLogRecordExporter()))
            logger.debug("Configured logs exporter: console")

        elif exporter == "none":
            continue

        else:
            logger.warning(f"Unknown logs exporter '{exporter}'. Ignored")

    # set up logging bridge
    otel_handler = LoggingHandler(logger_provider=logger_provider)
    otel_handler.name = "opentelemetry"
    logging.getLogger().addHandler(otel_handler)
    # locust loggers are configured with propagate=False, so they need this handler explicitly.
    logging.getLogger("locust").addHandler(otel_handler)
    # stats loggings is a little too verbose for otel
    # logging.getLogger("locust.stats_logger").addHandler(otel_handler)

    return logger_provider


def _setup_auto_instrumentation():
    try:
        import requests
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.trace import Span

        def request_hook(span: Span, request: requests.PreparedRequest):
            if name := getattr(request, "_explicit_name", None):
                span.update_name(f"{request.method} {name}")
            else:
                parsed = urlparse(request.url)
                span.update_name(f"{request.method} {str(parsed.path) or '/'}")

        RequestsInstrumentor().instrument(request_hook=request_hook)
    except ImportError:
        logger.info(
            "OpenTelemetry 'requests' instrumentation is not installed. Please install 'opentelemetry-instrumentation-requests'"
        )

    try:
        from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

        URLLib3Instrumentor().instrument()
    except ImportError:
        logger.info(
            "OpenTelemetry 'urllib3' instrumentation is not installed. Please install 'opentelemetry-instrumentation-urllib3'"
        )
