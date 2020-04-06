import gevent
from locust import HttpLocust, TaskSet, task, between
from locust.runners import LocalLocustRunner
from locust.env import Environment
from locust.stats import stats_printer
from locust.log import setup_logging
from locust.web import WebUI

setup_logging("INFO", None)


class User(HttpLocust):
    wait_time = between(1, 3)
    host = "https://docs.locust.io"
    
    class task_set(TaskSet):
        @task
        def my_task(self):
            self.client.get("/")
        
        @task
        def task_404(self):
            self.client.get("/non-existing-path")

# setup Environment and Runner
env = Environment()
runner = LocalLocustRunner(environment=env, locust_classes=[User])
# start a WebUI instance
web_ui = WebUI(environment=env)
gevent.spawn(lambda: web_ui.start("127.0.0.1", 8089))


# TODO: fix 
#def on_request_success(request_type, name, response_time, response_length, **kwargs):
#    report_to_grafana("%_%s" % (request_type, name), response_time)
#env.events.request_succes.add_listener(on_request_success)

# start a greenlet that periodically outputs the current stats
gevent.spawn(stats_printer(runner.stats))

# start the test
runner.start(1, hatch_rate=10)
# wait for the greenlets (indefinitely)
runner.greenlet.join()
