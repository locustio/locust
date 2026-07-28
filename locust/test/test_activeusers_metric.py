from locust import User, constant, task
from locust.env import Environment

from .testcases import LocustTestCase


class SimpleUser(User):
    wait_time = constant(0)

    @task
    def noop(self):
        pass


class UserCount(LocustTestCase):

    def _get_reported_user_count(self,label: str) -> None:
        metrics_data = self.reader.get_metrics_data()
        metric = metrics_data.resource_metrics[0].scope_metrics[0].metrics[0]
        data_point = metric.data.data_points[0]
        return data_point.value
    
    def test_user_count_gauge_reports_running_users(self):
        try:
            from opentelemetry import metrics
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import InMemoryMetricReader
            import locust
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
        self.assertEqual(self.runner.user_count,self._get_reported_user_count("after start"))
        self.addCleanup(self.runner.stop)

        self.runner.stop()
        self.assertEqual(self.runner.user_count,self._get_reported_user_count("after stop"))