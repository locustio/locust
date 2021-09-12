from locust import HttpUser, TaskSet, task, between
from locust import events


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--my-argument", type=str, env_var="LOCUST_MY_ARGUMENT", default="", help="It's working")
    # Set `include_in_web_ui` to False if you want to hide from the web UI
    parser.add_argument("--my-ui-invisible-argument", include_in_web_ui=False, default="I am invisible")


@events.init.add_listener
def _(environment, **kw):
    print("Custom argument supplied: %s" % environment.parsed_options.my_argument)


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)

    @task
    def my_task(self):
        print(f"my_argument={self.environment.parsed_options.my_argument}")
        print(f"my_ui_invisible_argument={self.environment.parsed_options.my_ui_invisible_argument}")
