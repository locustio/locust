from locust import HttpLocust, TaskSet, task, between
from locust import events


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        '--custom-argument',
        help="It's working"
    )

@events.init.add_listener
def _(environment, **kw):
    print("Custom argument supplied: %s" % environment.options.custom_argument)


class WebsiteUser(HttpLocust):
    """
    Locust user class that does requests to the locust web server running on localhost
    """
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)
    class task_set(TaskSet):
        @task
        def my_task(self):
            pass
