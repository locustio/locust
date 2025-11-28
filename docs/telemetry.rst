.. _telemetry:

=========================
OpenTelemetry Integration
=========================

Locust now optionally integrates with OpenTelemetry (OTel), enabling you to automatically export traces
and metrics from your load tests to any OTel-compatible backend (OTLP, Prometheus, Jaeger, Tempo, etc.).
This makes it easy to correlate load-test activity with application and infrastructure telemetry in your observability stack.

The configuration is done via environment variables. See the `OpenTelemetry documentation <https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/>`_
for details on how to configure exporters, resource attributes, sampling, etc.

Setup
-----

To enable OpenTelemetry, you need to download ``locust`` with the OpenTelemetry dependencies:

.. code-block:: console

   $ pip install locust[otel]

Then, pass the command line argument ``--otel`` to enable OpenTelemetry:

.. code-block:: console

   $ locust --otel
   ...


Exporters
---------

Locust supports the following OpenTelemetry exporters, for both traces and metrics, out of the box:

- OTLP (gRPC and HTTP) - this is the default exporter using gRPC protocol
- Console (useful for debugging)

For traces, ``BatchSpanProcessor`` is used and can be configured with these `variables <https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#batch-span-processor>`_.

For metrics, ``PeriodicExportingMetricReader`` is used and is configurable with the corresponding `variables <https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#periodic-exporting-metricreader>`_.


Auto Instrumentation
--------------------

.. note::

   Currently, only the ``requests`` library is auto-instrumented. This mean that only ``HttpUser`` will have it's HTTP requests made during your load tests automatically generate spans,
   and metrics with no additional configuration needed.

   We plan to add auto-instrumentation for more libraries in future releases.


Supported Users
~~~~~~~~~~~~~~~
+--------------+-----------------------+
| User Class   | Instrumented Library  |
+--------------+-----------------------+
| ``HttpUser`` | ``requests``          |
+--------------+-----------------------+

If you need instrumentation for other libraries (e.g., database clients, messaging libraries), you can manually set up additional instrumentation
using the OpenTelemetry Python SDK as per the `OpenTelemetry Python documentation <https://opentelemetry.io/docs/instrumentation/python/>`_.


Example
-------

.. code-block:: console

   $ export OTEL_EXPORTER_OTLP_HEADERS=X-XX-TOKEN=<xxxxxxxxxx>
   $ export OTEL_METRICS_EXPORTER=none
   $ export OTEL_TRACES_EXPORTER=otlp,console
   $ export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://<xxxxxxxxxx>
   $ export OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=http
   $ locust --otel
   [2025-11-28 16:27:01,916] locust/INFO/locust.main: Starting Locust, OpenTelemetry enabled
   [2025-11-28 16:27:01,916] locust/INFO/locust.main: Starting web interface at http://0.0.0.0:8089, press enter to open your default browser.
   ...

