"""
This file contains a benchmark to validate the performance of Locust itself.
More precisely, the performance of the `UsersDispatcher` class which is responsible
for calculating the distribution of users on each worker. This benchmark is to be used
by people working on Locust's development.
"""

from locust import User
from locust.dispatch import UsersDispatcher
from locust.runners import WorkerNode

import argparse
import gc
import itertools
import statistics
import time

from prettytable import PrettyTable

NUMBER_OF_USER_CLASSES: int = 1000
USER_CLASSES: list[type[User]] = []
WEIGHTS = list(range(1, NUMBER_OF_USER_CLASSES + 1))

for i, x in enumerate(WEIGHTS):
    exec(f"class User{i}(User): weight = {x}")

# Equivalent to:
#
# class User0(User):
#     weight = 5
#
# class User1(User):
#     weight = 55
# .
# .
# .

exec("USER_CLASSES = [" + ",".join(f"User{i}" for i in range(len(WEIGHTS))) + "]")
# Equivalent to:
#
# USER_CLASSES = [
#     User0,
#     User1,
#     .
#     .
#     .
# ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--full-benchmark", action="store_true", help="run benchmark on full test matrix")
    parser.add_argument(
        "-i",
        "--include-fixed-users",
        action="store_true",
        help="add test cases when 50 percent of users use User.fixed_count instead of User.weight",
    )
    parser.add_argument("-r", "--repeat", default=1, type=int, help="number of test cases with the same parameters")
    parser.add_argument("-s", "--save-output", action="store_true", help="save test results to files")
    args = parser.parse_args()

    now = time.time()

    worker_count_cases = [10, 100, 1000]
    user_count_cases = [10_000, 100_000, 1_000_000]
    number_of_user_classes_cases = [1, 30, 1000]
    spawn_rate_cases = [100, 10_000]
    fixed_count_cases = [False, True] if args.include_fixed_users else [False]
    # [0% fixed_count users, 50% fixed_count users] if args.mixed_user_types else [0% fixed_count users]
    repeat_cases = list(range(1, args.repeat + 1))

    if not args.full_benchmark:
        worker_count_cases = [max(worker_count_cases)]
        user_count_cases = [max(user_count_cases)]
        number_of_user_classes_cases = [max(number_of_user_classes_cases)]
        spawn_rate_cases = [max(spawn_rate_cases)]

    case_count = (
        len(worker_count_cases)
        * len(user_count_cases)
        * len(number_of_user_classes_cases)
        * len(spawn_rate_cases)
        * len(fixed_count_cases)
        * len(repeat_cases)
    )

    results = {}

    try:
        for case_index, (
            worker_count,
            user_count,
            number_of_user_classes,
            spawn_rate,
            fixed_users,
            iteration,
        ) in enumerate(
            itertools.product(
                worker_count_cases,
                user_count_cases,
                number_of_user_classes_cases,
                spawn_rate_cases,
                fixed_count_cases,
                repeat_cases,
            )
        ):
            workers = [WorkerNode(str(i)) for i in range(worker_count)]
            if fixed_users:
                sum_fixed_weight = 0
                for j in range(0, number_of_user_classes, 2):
                    sum_fixed_weight += USER_CLASSES[j].weight

                for j in range(0, number_of_user_classes, 2):  # set fixed_weights for 50% of users
                    USER_CLASSES[j].fixed_count = max(1, USER_CLASSES[j].weight // sum_fixed_weight)  # type: ignore # assigned .weight is int

            ts = time.process_time()
            users_dispatcher = UsersDispatcher(
                worker_nodes=workers,
                user_classes=USER_CLASSES[:number_of_user_classes],
            )
            instantiate_duration = time.process_time() - ts

            # Ramp-up
            gc.disable()
            ts = time.process_time()
            users_dispatcher.new_dispatch(target_user_count=user_count, spawn_rate=spawn_rate)
            new_dispatch_ramp_up_duration = time.process_time() - ts
            gc.enable()

            assert len(users_dispatcher.dispatch_iteration_durations) == 0
            users_dispatcher._wait_between_dispatch = 0
            all_dispatched_users_ramp_up = list(users_dispatcher)
            dispatch_iteration_durations_ramp_up = users_dispatcher.dispatch_iteration_durations[:]

            # Ramp-down
            gc.disable()
            ts = time.process_time()
            users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=spawn_rate)
            new_dispatch_ramp_down_duration = time.process_time() - ts
            gc.enable()

            assert len(users_dispatcher.dispatch_iteration_durations) == 0
            users_dispatcher._wait_between_dispatch = 0
            all_dispatched_users_ramp_down = list(users_dispatcher)
            dispatch_iteration_durations_ramp_down = users_dispatcher.dispatch_iteration_durations[:]

            if fixed_users:
                for j in range(0, number_of_user_classes, 2):
                    USER_CLASSES[j].fixed_count = None

            cpu_ramp_up = "{:3.3f}/{:3.3f}/{:3.3f}".format(  # noqa: UP032
                1000 * statistics.mean(dispatch_iteration_durations_ramp_up),
                1000 * min(dispatch_iteration_durations_ramp_up),
                1000 * max(dispatch_iteration_durations_ramp_up),
            )  # noqa: UP032
            cpu_ramp_down = "{:3.3f}/{:3.3f}/{:3.3f}".format(  # noqa: UP032
                1000 * statistics.mean(dispatch_iteration_durations_ramp_down),
                1000 * min(dispatch_iteration_durations_ramp_down),
                1000 * max(dispatch_iteration_durations_ramp_down),
            )

            print(
                "{:04.0f}/{:04.0f} - {:,} workers - {:,} users - {} user classes - {:,} users/s - instantiate: {:.3f}ms - new_dispatch (ramp-up/ramp-down): {:.3f}ms/{:.3f}ms - cpu_ramp_up: {}ms - cpu_ramp_down: {}ms".format(  # noqa: UP032
                    case_index + 1,
                    case_count,
                    worker_count,
                    user_count,
                    number_of_user_classes,
                    spawn_rate,
                    instantiate_duration * 1000,
                    new_dispatch_ramp_up_duration * 1000,
                    new_dispatch_ramp_down_duration * 1000,
                    cpu_ramp_up,
                    cpu_ramp_down,
                )
            )

            results[(worker_count, user_count, number_of_user_classes, spawn_rate, fixed_users, iteration)] = (
                cpu_ramp_up,
                cpu_ramp_down,
            )

    finally:
        table = PrettyTable()
        table.field_names = [
            "Workers",
            "Users",
            "User Classes",
            "Spawn Rate",
            "Fixed Users",
            "Iteration",
            "Ramp-Up (avg/min/max) (ms)",
            "Ramp-Down (avg/min/max) (ms)",
        ]
        table.align["Workers"] = "l"
        table.align["Users"] = "l"
        table.align["User Classes"] = "l"
        table.align["Spawn Rate"] = "l"
        table.align["Fixed Users"] = "l"
        table.align["Iteration"] = "c"
        table.align["Ramp-Up (avg/min/max) (ms)"] = "c"
        table.align["Ramp-Down (avg/min/max) (ms)"] = "c"
        table.add_rows(
            [
                [
                    f"{worker_count:,}",
                    f"{user_count:,}",
                    number_of_user_classes,
                    f"{spawn_rate:,}",
                    "50%" if fixed_users else "0%",
                    iteration,
                    cpu_ramp_up,
                    cpu_ramp_down,
                ]
                for (worker_count, user_count, number_of_user_classes, spawn_rate, fixed_users, iteration), (
                    cpu_ramp_up,
                    cpu_ramp_down,
                ) in results.items()
            ]
        )
        print()
        print(table)

        if args.save_output:
            with open(f"results-dispatch-benchmarks-{int(now)}.txt", "w") as file:
                file.write(table.get_string())

            with open(f"results-dispatch-benchmarks-{int(now)}.json", "w") as file:
                file.write(table.get_json_string())
