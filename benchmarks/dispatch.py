"""
This file contains a benchmark to validate the performance of Locust itself.
More precisely, the performance of the `UsersDispatcher` class which is responsible
for calculating the distribution of users on each workers. This benchmark is to be used
by people working on Locust's development.
"""

from locust import User
from locust.dispatch import UsersDispatcher
from locust.runners import WorkerNode

import itertools
import statistics
import time

from prettytable import PrettyTable

# fmt: off
WEIGHTS = [
     5, 55, 37,  2, 97, 41, 33, 19, 19, 34,
    78, 76, 28, 62, 69,  5, 55, 37,  2, 97,
    41, 33, 19, 19, 34, 78, 76, 28, 62, 69,
    41, 33, 19, 19, 34, 78, 76, 28, 62, 69,
    41, 33, 19, 19, 34, 78, 76, 28, 62, 69,
     5, 55, 37,  2, 97, 41, 33, 19, 19, 34,
    78, 76, 28, 62, 69,  5, 55, 37,  2, 97,
    41, 33, 19, 19, 34, 78, 76, 28, 62, 69,
    41, 33, 19, 19, 34, 78, 76, 28, 62, 69,
    41, 33, 19, 19, 34, 78, 76, 28, 62, 69,
]
# fmt: on

for i, x in enumerate(WEIGHTS):
    exec(f"class User{i+1}(User): weight = {x}")

# Equivalent to:
#
# class User1(User):
#     weight = 5
#
# class User2(User):
#     weight = 55
# .
# .
# .
# class User100(User):
#     weight = 69

exec("USER_CLASSES = [" + ",".join(f"User{i+1}" for i in range(len(WEIGHTS))) + "]")
# Equivalent to:
#
# USER_CLASSES = [
#     User1,
#     User2,
#     .
#     .
#     .
#     User100,
# ]


if __name__ == "__main__":
    now = time.time()

    worker_count_cases = [10, 100, 500, 1000, 5000, 10_000, 15_000, 20_000]
    user_count_cases = [10, 100, 1000, 10_000, 50_000, 100_000, 500_000]
    number_of_user_classes_cases = [1, 10, 40, 60, 80, 100]
    spawn_rate_cases = [1, 10, 100, 500, 1000, 2500, 5000, 10_000, 20_000, 25_000]

    case_count = (
        len(worker_count_cases) * len(user_count_cases) * len(number_of_user_classes_cases) * len(spawn_rate_cases)
    )

    results = {}

    try:
        for case_index, (worker_count, user_count, number_of_user_classes, spawn_rate) in enumerate(
            itertools.product(worker_count_cases, user_count_cases, number_of_user_classes_cases, spawn_rate_cases)
        ):
            if user_count / spawn_rate > 1000:
                print(f"Skipping user_count = {user_count:,} - spawn_rate = {spawn_rate:,}")
                continue

            workers = [WorkerNode(str(i + 1)) for i in range(worker_count)]

            ts = time.perf_counter()
            users_dispatcher = UsersDispatcher(
                worker_nodes=workers,
                user_classes=USER_CLASSES[:number_of_user_classes],  # noqa: F821 (Undefined name `USER_CLASSES`) -> It's created inside "exec"
            )
            instantiate_duration = time.perf_counter() - ts

            # Ramp-up
            ts = time.perf_counter()
            users_dispatcher.new_dispatch(target_user_count=user_count, spawn_rate=spawn_rate)
            new_dispatch_ramp_up_duration = time.perf_counter() - ts
            assert len(users_dispatcher.dispatch_iteration_durations) == 0
            users_dispatcher._wait_between_dispatch = 0
            all_dispatched_users_ramp_up = list(users_dispatcher)
            dispatch_iteration_durations_ramp_up = users_dispatcher.dispatch_iteration_durations[:]

            # Ramp-down
            ts = time.perf_counter()
            users_dispatcher.new_dispatch(target_user_count=0, spawn_rate=spawn_rate)
            new_dispatch_ramp_down_duration = time.perf_counter() - ts
            assert len(users_dispatcher.dispatch_iteration_durations) == 0
            users_dispatcher._wait_between_dispatch = 0
            all_dispatched_users_ramp_down = list(users_dispatcher)
            dispatch_iteration_durations_ramp_down = users_dispatcher.dispatch_iteration_durations[:]

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

            results[(worker_count, user_count, number_of_user_classes, spawn_rate)] = (cpu_ramp_up, cpu_ramp_down)

    finally:
        table = PrettyTable()
        table.field_names = [
            "Workers",
            "Users",
            "User Classes",
            "Spawn Rate",
            "Ramp-Up (avg/min/max) (ms)",
            "Ramp-Down (avg/min/max) (ms)",
        ]
        table.align["Workers"] = "l"
        table.align["Users"] = "l"
        table.align["User Classes"] = "l"
        table.align["Spawn Rate"] = "l"
        table.align["Ramp-Up (avg/min/max) (ms)"] = "c"
        table.align["Ramp-Down (avg/min/max) (ms)"] = "c"
        table.add_rows(
            [
                [
                    f"{worker_count:,}",
                    f"{user_count:,}",
                    number_of_user_classes,
                    f"{spawn_rate:,}",
                    cpu_ramp_up,
                    cpu_ramp_down,
                ]
                for (worker_count, user_count, number_of_user_classes, spawn_rate), (
                    cpu_ramp_up,
                    cpu_ramp_down,
                ) in results.items()
            ]
        )
        print()
        print()
        print()
        print(table)

        with open(f"results-dispatch-benchmarks-{int(now)}.txt", "w") as file:
            file.write(table.get_string())

        with open(f"results-dispatch-benchmarks-{int(now)}.json", "w") as file:
            file.write(table.get_json_string())
