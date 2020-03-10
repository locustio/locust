==========================
Using Locust as a library
==========================

It's possible to use Locust as a library instead of running Locust by invoking the ``locust`` command.

Here's an example::

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
    env = Environment(locust_classes=[User])
    runner = LocalLocustRunner(environment=env)
    # start a WebUI instance
    web_ui = WebUI(runner=runner, environment=env)
    gevent.spawn(lambda: web_ui.start("127.0.0.1", 8089))
    
    # start a greenlet that periodically outputs the current stats
    gevent.spawn(stats_printer(env.stats))
    
    # start the test
    runner.start(1, hatch_rate=10)
    # wait for the greenlets (indefinitely)
    runner.greenlet.join()
