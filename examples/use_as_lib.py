#!/usr/bin/env python3
from locust import HttpUser, events, task
from locust.env import Environment
from locust.log import setup_logging
from locust.stats import stats_history, stats_printer

import gevent

setup_logging("INFO", None)


class MyUser(HttpUser):
    host = "https://docs.locust.io"

    @task
    def t(self):
        self.client.get("/")


# setup Environment and Runner
env = Environment(user_classes=[MyUser], events=events)
runner = env.create_local_runner()

# start a WebUI instance
web_ui = env.create_web_ui("127.0.0.1", 8089)

# execute init event handlers (only really needed if you have registered any)
env.events.init.fire(environment=env, runner=runner, web_ui=web_ui)

# start a greenlet that periodically outputs the current stats
gevent.spawn(stats_printer(env.stats))

# start a greenlet that save current stats to history
gevent.spawn(stats_history, env.runner)

# start the test
runner.start(1, spawn_rate=10)

# in 60 seconds stop the runner
gevent.spawn_later(60, lambda: runner.quit())

# wait for the greenlets
runner.greenlet.join()

# stop the web server for good measures
web_ui.stop()
