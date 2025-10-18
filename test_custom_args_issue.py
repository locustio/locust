"""
Test to reproduce issue #3206: Custom argument values not passed to workers in distributed mode
"""

from locust import User, constant, events, task
from locust.argument_parser import parse_options, ui_extra_args_dict
from locust.env import Environment

from time import sleep
from unittest import mock


@events.init_command_line_parser.add_listener
def add_custom_arguments(parser):
    parser.add_argument(
        "--arg1",
        type=str,
        help="Some argument 1",
        default="Foo",
        include_in_web_ui=True,
    )
    parser.add_argument(
        "--arg2",
        type=int,
        help=f"Some argument 2 (default: {10})",
        default=10,
        include_in_web_ui=True,
    )


class TestUser(User):
    wait_time = constant(1)

    @task
    def my_task(self):
        print(
            f"Worker sees custom args: "
            f"arg1={self.environment.parsed_options.arg1}, "
            f"arg2={self.environment.parsed_options.arg2}"
        )


def test_webui_shows_custom_args_from_cmdline():
    """Test that custom arguments passed via command line are shown in web UI"""
    # Parse options with custom arguments from command line
    parsed_options = parse_options(
        [
            "--arg1",
            "cmdline-value",
            "--arg2",
            "123",
        ]
    )

    print(f"Command line args: arg1={parsed_options.arg1}, arg2={parsed_options.arg2}")

    # Get UI extra args (without passing parsed_options - the old way)
    extra_options_old = ui_extra_args_dict()
    print("\nWeb UI extra args (old way, no parsed_options):")
    if "arg1" in extra_options_old:
        print(f"  arg1={extra_options_old['arg1']['default_value']}")
    if "arg2" in extra_options_old:
        print(f"  arg2={extra_options_old['arg2']['default_value']}")

    # Get UI extra args (with passing parsed_options - the new way)
    extra_options_new = ui_extra_args_dict(parsed_options=parsed_options)
    print("\nWeb UI extra args (new way, with parsed_options):")
    if "arg1" in extra_options_new:
        print(f"  arg1={extra_options_new['arg1']['default_value']}")
    if "arg2" in extra_options_new:
        print(f"  arg2={extra_options_new['arg2']['default_value']}")

    # Assertions
    assert "arg1" in extra_options_new, "arg1 should be in extra_options"
    assert "arg2" in extra_options_new, "arg2 should be in extra_options"
    assert extra_options_new["arg1"]["default_value"] == "cmdline-value", (
        f"Expected 'cmdline-value' but got '{extra_options_new['arg1']['default_value']}'"
    )
    assert extra_options_new["arg2"]["default_value"] == 123, (
        f"Expected 123 but got {extra_options_new['arg2']['default_value']}"
    )

    print("\n✓ Test passed! Web UI now correctly shows custom arguments from command line.")


def test_custom_args_updated_via_webui():
    """Test that custom arguments updated via web UI are passed to workers"""
    with mock.patch("locust.runners.WORKER_REPORT_INTERVAL", new=0.3):
        # Start Master runner with initial custom arg values
        master_env = Environment(user_classes=[TestUser])
        master = master_env.create_master_runner("*", 0)
        master_env.parsed_options = parse_options(
            [
                "--arg1",
                "initial-value",
                "--arg2",
                "100",
            ]
        )

        print(f"\nMaster initial args: arg1={master_env.parsed_options.arg1}, arg2={master_env.parsed_options.arg2}")

        sleep(0)

        # Start Worker runner
        worker_env = Environment(user_classes=[TestUser])
        _worker = worker_env.create_worker_runner("127.0.0.1", master.server.port)

        # Give worker time to connect
        sleep(0.1)

        # Simulate web UI updating custom arguments (like what happens in web.py swarm() function)
        print("Simulating Web UI updating custom arguments...")
        parsed_options_dict = vars(master_env.parsed_options)
        parsed_options_dict["arg1"] = "updated-from-webui"
        parsed_options_dict["arg2"] = 999
        print(f"Master updated args: arg1={master_env.parsed_options.arg1}, arg2={master_env.parsed_options.arg2}")

        # Start the test with updated values
        master.start(1, spawn_rate=1)
        sleep(0.5)

        # Check worker's parsed_options
        print(f"Worker received args: arg1={worker_env.parsed_options.arg1}, arg2={worker_env.parsed_options.arg2}")

        # Assertions
        assert worker_env.parsed_options.arg1 == "updated-from-webui", (
            f"Expected 'updated-from-webui' but got '{worker_env.parsed_options.arg1}'"
        )
        assert worker_env.parsed_options.arg2 == 999, f"Expected 999 but got {worker_env.parsed_options.arg2}"

        print("✓ Test passed! Worker correctly received updated custom arguments.")

        master.quit()
        sleep(0.1)


if __name__ == "__main__":
    print("=" * 80)
    print("Test 1: Web UI should show custom arguments from command line")
    print("=" * 80)
    test_webui_shows_custom_args_from_cmdline()

    print("\n" + "=" * 80)
    print("Test 2: Workers should receive custom arguments updated via Web UI")
    print("=" * 80)
    test_custom_args_updated_via_webui()

    print("\n" + "=" * 80)
    print("All tests passed! Issue #3206 is fixed.")
    print("=" * 80)
