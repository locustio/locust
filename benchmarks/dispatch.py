"""
This file contains a benchmark to validate the performance of Locust itself.
More precisely, the performance of the `UsersDispatcher` class which is responsible
for calculating the distribution of users on each workers. This benchmark is to be used
by people working on Locust's development.
"""

import itertools
import statistics
import time

from prettytable import PrettyTable

from locust import User
from locust.dispatch import UsersDispatcher
from locust.runners import WorkerNode


class User1(User):
    weight = 5


class User2(User):
    weight = 55


class User3(User):
    weight = 37


class User4(User):
    weight = 2


class User5(User):
    weight = 97


class User6(User):
    weight = 41


class User7(User):
    weight = 33


class User8(User):
    weight = 19


class User9(User):
    weight = 19


class User10(User):
    weight = 34


class User11(User):
    weight = 78


class User12(User):
    weight = 76


class User13(User):
    weight = 28


class User14(User):
    weight = 62


class User15(User):
    weight = 69


class User16(User):
    weight = 5


class User17(User):
    weight = 55


class User18(User):
    weight = 37


class User19(User):
    weight = 2


class User20(User):
    weight = 97


class User21(User):
    weight = 41


class User22(User):
    weight = 33


class User23(User):
    weight = 19


class User24(User):
    weight = 19


class User25(User):
    weight = 34


class User26(User):
    weight = 78


class User27(User):
    weight = 76


class User28(User):
    weight = 28


class User29(User):
    weight = 62


class User30(User):
    weight = 69


class User31(User):
    weight = 41


class User32(User):
    weight = 33


class User33(User):
    weight = 19


class User34(User):
    weight = 19


class User35(User):
    weight = 34


class User36(User):
    weight = 78


class User37(User):
    weight = 76


class User38(User):
    weight = 28


class User39(User):
    weight = 62


class User40(User):
    weight = 69


class User41(User):
    weight = 41


class User42(User):
    weight = 33


class User43(User):
    weight = 19


class User44(User):
    weight = 19


class User45(User):
    weight = 34


class User46(User):
    weight = 78


class User47(User):
    weight = 76


class User48(User):
    weight = 28


class User49(User):
    weight = 62


class User50(User):
    weight = 69


class User51(User):
    weight = 5


class User52(User):
    weight = 55


class User53(User):
    weight = 37


class User54(User):
    weight = 2


class User55(User):
    weight = 97


class User56(User):
    weight = 41


class User57(User):
    weight = 33


class User58(User):
    weight = 19


class User59(User):
    weight = 19


class User60(User):
    weight = 34


class User61(User):
    weight = 78


class User62(User):
    weight = 76


class User63(User):
    weight = 28


class User64(User):
    weight = 62


class User65(User):
    weight = 69


class User66(User):
    weight = 5


class User67(User):
    weight = 55


class User68(User):
    weight = 37


class User69(User):
    weight = 2


class User70(User):
    weight = 97


class User71(User):
    weight = 41


class User72(User):
    weight = 33


class User73(User):
    weight = 19


class User74(User):
    weight = 19


class User75(User):
    weight = 34


class User76(User):
    weight = 78


class User77(User):
    weight = 76


class User78(User):
    weight = 28


class User79(User):
    weight = 62


class User80(User):
    weight = 69


class User81(User):
    weight = 41


class User82(User):
    weight = 33


class User83(User):
    weight = 19


class User84(User):
    weight = 19


class User85(User):
    weight = 34


class User86(User):
    weight = 78


class User87(User):
    weight = 76


class User88(User):
    weight = 28


class User89(User):
    weight = 62


class User90(User):
    weight = 69


class User91(User):
    weight = 41


class User92(User):
    weight = 33


class User93(User):
    weight = 19


class User94(User):
    weight = 19


class User95(User):
    weight = 34


class User96(User):
    weight = 78


class User97(User):
    weight = 76


class User98(User):
    weight = 28


class User99(User):
    weight = 62


class User100(User):
    weight = 69


USER_CLASSES = [
    User1,
    User2,
    User3,
    User4,
    User5,
    User6,
    User7,
    User8,
    User9,
    User10,
    User11,
    User12,
    User13,
    User14,
    User15,
    User16,
    User17,
    User18,
    User19,
    User20,
    User21,
    User22,
    User23,
    User24,
    User25,
    User26,
    User27,
    User28,
    User29,
    User30,
    User31,
    User32,
    User33,
    User34,
    User35,
    User36,
    User37,
    User38,
    User39,
    User40,
    User41,
    User42,
    User43,
    User44,
    User45,
    User46,
    User47,
    User48,
    User49,
    User50,
    User51,
    User52,
    User53,
    User54,
    User55,
    User56,
    User57,
    User58,
    User59,
    User60,
    User61,
    User62,
    User63,
    User64,
    User65,
    User66,
    User67,
    User68,
    User69,
    User70,
    User71,
    User72,
    User73,
    User74,
    User75,
    User76,
    User77,
    User78,
    User79,
    User80,
    User81,
    User82,
    User83,
    User84,
    User85,
    User86,
    User87,
    User88,
    User89,
    User90,
    User91,
    User92,
    User93,
    User94,
    User95,
    User96,
    User97,
    User98,
    User99,
    User100,
]


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
                print("Skipping user_count = {:,} - spawn_rate = {:,}".format(user_count, spawn_rate))
                continue

            workers = [WorkerNode(str(i + 1)) for i in range(worker_count)]

            ts = time.perf_counter()
            users_dispatcher = UsersDispatcher(worker_nodes=workers, user_classes=USER_CLASSES[:number_of_user_classes])
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

            cpu_ramp_up = "{:3.3f}/{:3.3f}/{:3.3f}".format(
                1000 * statistics.mean(dispatch_iteration_durations_ramp_up),
                1000 * min(dispatch_iteration_durations_ramp_up),
                1000 * max(dispatch_iteration_durations_ramp_up),
            )
            cpu_ramp_down = "{:3.3f}/{:3.3f}/{:3.3f}".format(
                1000 * statistics.mean(dispatch_iteration_durations_ramp_down),
                1000 * min(dispatch_iteration_durations_ramp_down),
                1000 * max(dispatch_iteration_durations_ramp_down),
            )

            print(
                "{:04.0f}/{:04.0f} - {:,} workers - {:,} users - {} user classes - {:,} users/s - instantiate: {:.3f}ms - new_dispatch (ramp-up/ramp-down): {:.3f}ms/{:.3f}ms - cpu_ramp_up: {}ms - cpu_ramp_down: {}ms".format(
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
                    "{:,}".format(worker_count),
                    "{:,}".format(user_count),
                    number_of_user_classes,
                    "{:,}".format(spawn_rate),
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

        with open("results-dispatch-benchmarks-{}.txt".format(int(now)), "wt") as file:
            file.write(table.get_string())

        with open("results-dispatch-benchmarks-{}.json".format(int(now)), "wt") as file:
            file.write(table.get_json_string())
