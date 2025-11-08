from locust import HttpUser, events, task


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--my-argument", type=str, env_var="LOCUST_MY_ARGUMENT", default="", help="It's working")
    # Choices will validate command line input and show a dropdown in the web UI
    parser.add_argument("--env", choices=["dev", "staging", "prod"], default="dev", help="Environment")
    # In combination with choices, is_multiple makes the dropdown in the web UI allow multiple selections
    parser.add_argument("--endpoints", choices=["a", "b", "c"], is_multiple=True, default=["a"], help="Endpoints")
    # Set `include_in_web_ui` to False if you want to hide from the web UI
    parser.add_argument("--my-ui-invisible-argument", include_in_web_ui=False, default="I am invisible")
    # Set `is_secret` to True if you want the text input to be password masked in the web UI
    parser.add_argument("--my-ui-password-argument", is_secret=True, default="I am a secret")
    # Use a boolean default value if you want the input to be a checkmark
    parser.add_argument("--my-ui-boolean-argument", default=True)
    # Set `is_required` to mark a form field as required
    parser.add_argument("--my-ui-required-argument", is_required=True, default="I am required")


@events.test_start.add_listener
def _(environment, **kw):
    print(f"Custom argument supplied: {environment.parsed_options.my_argument}")


class WebsiteUser(HttpUser):
    @task
    def my_task(self):
        print(f"my_argument={self.environment.parsed_options.my_argument}")
        print(f"my_ui_invisible_argument={self.environment.parsed_options.my_ui_invisible_argument}")
