"""
Example demonstrating custom command-line arguments in distributed mode.

This example shows how custom arguments are properly passed from master to workers
and how they appear correctly in the Web UI.

To run this example in distributed mode:

1. Start the master:
   locust -f custom_args_distributed.py --master --arg1 "master-value" --arg2 100

2. Start one or more workers:
   locust -f custom_args_distributed.py --worker

3. Open the Web UI at http://localhost:8089
   - You should see the custom arguments with their values set from command line
   - You can modify these values in the Web UI before starting the test
   - The updated values will be passed to all workers

Note: This was previously broken (issue #3206) where the Web UI would show
default values instead of the values passed via command line.
"""

from locust import HttpUser, constant, events, task


@events.init_command_line_parser.add_listener
def add_custom_arguments(parser):
    """Add custom command-line arguments that will be visible in the Web UI"""
    parser.add_argument(
        "--arg1",
        type=str,
        help="Custom string argument",
        default="default-string",
        include_in_web_ui=True,  # Make this argument editable in Web UI
    )

    parser.add_argument(
        "--arg2",
        type=int,
        help="Custom integer argument",
        default=10,
        include_in_web_ui=True,  # Make this argument editable in Web UI
    )

    parser.add_argument(
        "--secret-token",
        type=str,
        help="Secret token (will be masked in Web UI)",
        default="secret123",
        include_in_web_ui=True,
        is_secret=True,  # This will mask the value in Web UI
    )


class MyUser(HttpUser):
    """Example user that uses custom arguments"""

    host = "http://example.com"
    wait_time = constant(1)

    @task
    def my_task(self):
        """Task that uses custom arguments"""
        arg1 = self.environment.parsed_options.arg1
        arg2 = self.environment.parsed_options.arg2
        secret = self.environment.parsed_options.secret_token

        # Log the arguments (in real scenarios, use them for your test logic)
        print(f"Task executing with: arg1={arg1}, arg2={arg2}, secret={'*' * len(secret)}")

        # In a real test, you might use these arguments like this:
        # self.client.get(f"/api/endpoint?param={arg1}")
        # for _ in range(arg2):
        #     self.client.post("/api/data", headers={"Authorization": f"Bearer {secret}"})
