from locust import User, constant, task
from locust.env import Environment

from .testcases import LocustTestCase


class SimpleUser(User):
    wait_time = constant(0)

    @task
    def noop(self):
        pass


class UserCount(LocustTestCase):
    def _get_metric(self, name):
        metrics_data = self.reader.get_metrics_data()

        for resource_metrics in metrics_data.resource_metrics:
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    if metric.name == name:
                        return metric

        self.fail(f"Metric {name!r} not found")

    def test_user_count_gauge_reports_running_users(self):
        try:
            import locust

            from opentelemetry import metrics
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import InMemoryMetricReader
        except ImportError:
            self.skipTest("OpenTelemetry SDK is not installed")

        from locust.opentelemetry import setup_opentelemetry

        self.reader = InMemoryMetricReader()
        metrics.set_meter_provider(MeterProvider(metric_readers=[self.reader]))

        environment = Environment(user_classes=[SimpleUser], events=locust.events)
        self.runner = environment.create_local_runner()

        setup_opentelemetry("activeusers_metric.py", None)
        environment.events.init.fire(environment=environment, runner=self.runner, web_ui=None)

        self.assertEqual(0, self.runner.user_count)

        self.runner.start(3, spawn_rate=3)
        self.runner.spawning_greenlet.join(timeout=5)

        metric = self._get_metric("locust.users.count")
        self.assertEqual(self.runner.user_count, metric.data.data_points[0].value)
        self.addCleanup(self.runner.stop)

        self.runner.stop()
        metric = self._get_metric("locust.users.count")
        self.assertEqual(self.runner.user_count, metric.data.data_points[0].value)
