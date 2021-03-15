import itertools
import math
import time
from collections import namedtuple
from copy import deepcopy
from typing import (
    Dict,
    Generator,
    List,
    TYPE_CHECKING,
)

import gevent

if TYPE_CHECKING:
    from locust.runners import WorkerNode


def dispatch_users(
    worker_nodes,  # type: List[WorkerNode]
    user_class_occurrences: Dict[str, int],
    spawn_rate: float,
) -> Generator[Dict[str, Dict[str, int]], None, None]:
    """
    Generator function that dispatches the users
    in `user_class_occurrences` to the workers.
    The currently running users is also taken into
    account.

    It waits an appropriate amount of time between each iteration
    in order for the spawn rate to be respected, whether running in
    local or distributed mode.

    The spawn rate is only applicable when additional users are needed.
    Hence, if `user_class_occurrences` contains less users than there are
    currently running, this function won't wait and will only run for
    one iteration. The logic for not stopping users at a rate of `spawn_rate`
    is that stopping them is a blocking operation, especially when
    having a `stop_timeout` and users with tasks running for a few seconds or
    more. If we were to dispatch multiple spawn messages to have a ramp down,
    we'd run into problems where the previous spawning would be killed
    by the new message. See the call to `self.spawning_greenlet.kill()` in
    `:py:meth:`locust.runners.LocalRunner.start` and `:py:meth:`locust.runners.WorkerRunner.worker`.

    :param worker_nodes: List of worker nodes
    :param user_class_occurrences: Desired number of users for each class
    :param spawn_rate: The spawn rate
    """
    # Get repeatable behaviour.
    worker_nodes = sorted(worker_nodes, key=lambda w: w.id)

    # This represents the already running users among the workers
    initial_dispatched_users = {
        worker_node.id: {
            user_class: worker_node.user_class_occurrences.get(user_class, 0)
            for user_class in user_class_occurrences.keys()
        }
        for worker_node in worker_nodes
    }

    # This represents the desired users distribution among the workers
    balanced_users = balance_users_among_workers(
        worker_nodes,
        user_class_occurrences,
    )

    # This represents the desired users distribution minus the already running users among the workers
    effective_balanced_users = {
        worker_node.id: {
            user_class: max(
                0,
                balanced_users[worker_node.id][user_class] - initial_dispatched_users[worker_node.id][user_class],
            )
            for user_class in user_class_occurrences.keys()
        }
        for worker_node in worker_nodes
    }

    number_of_users_per_dispatch = max(1, math.floor(spawn_rate))

    wait_between_dispatch = number_of_users_per_dispatch / spawn_rate

    dispatched_users = deepcopy(initial_dispatched_users)

    # The amount of users in each user class
    # is less than the desired amount
    less_users_than_desired = all(
        sum(x[user_class] for x in dispatched_users.values())
        < sum(x[user_class] for x in effective_balanced_users.values())
        for user_class in user_class_occurrences.keys()
    )

    if less_users_than_desired:
        while sum(sum(x.values()) for x in effective_balanced_users.values()) > 0:
            users_to_dispatch = get_users_to_dispatch_for_current_iteration(
                user_class_occurrences, dispatched_users, effective_balanced_users, number_of_users_per_dispatch
            )

            ts = time.time()
            yield users_to_dispatch
            if sum(sum(x.values()) for x in effective_balanced_users.values()) > 0:
                delta = time.time() - ts
                sleep_duration = max(0.0, wait_between_dispatch - delta)
                assert sleep_duration <= 10, sleep_duration
                gevent.sleep(sleep_duration)

    elif (
        number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_class_occurrences)
        <= number_of_users_per_dispatch
    ):
        yield balanced_users

    else:
        while not all_users_have_been_dispatched(dispatched_users, effective_balanced_users, user_class_occurrences):
            users_to_dispatch = get_users_to_dispatch_for_current_iteration(
                user_class_occurrences, dispatched_users, effective_balanced_users, number_of_users_per_dispatch
            )

            ts = time.time()
            yield users_to_dispatch
            delta = time.time() - ts
            sleep_duration = max(0.0, wait_between_dispatch - delta)
            assert sleep_duration <= 10, sleep_duration
            gevent.sleep(sleep_duration)

        # If we are here, it means we have an excess of users for one or more user classes.
        # Hence, we need to dispatch a last set of users that will bring the users
        # distribution to the desired one.
        yield balanced_users


def get_users_to_dispatch_for_current_iteration(
    user_class_occurrences: Dict[str, int],
    dispatched_users: Dict[str, Dict[str, int]],
    effective_balanced_users: Dict[str, Dict[str, int]],
    number_of_users_per_dispatch: int,
) -> Dict[str, Dict[str, int]]:
    ts_dispatch = time.time()

    number_of_users_in_current_dispatch = 0

    for i, user_class in enumerate(itertools.cycle(user_class_occurrences.keys())):
        assert i < 5000, "Looks like dispatch is stuck in an infinite loop (iteration {})".format(i)

        if sum(map(sum, map(dict.values, effective_balanced_users.values()))) == 0:
            break

        if all_users_of_current_class_have_been_dispatched(effective_balanced_users, user_class):
            continue

        if go_to_next_user_class(user_class, user_class_occurrences, dispatched_users, effective_balanced_users):
            continue

        for j, worker_node_id in enumerate(itertools.cycle(effective_balanced_users.keys())):
            assert j < 100, "Looks like dispatch is stuck in an infinite loop (iteration {})".format(j)
            if effective_balanced_users[worker_node_id][user_class] == 0:
                continue
            dispatched_users[worker_node_id][user_class] += 1
            effective_balanced_users[worker_node_id][user_class] -= 1
            number_of_users_in_current_dispatch += 1
            break

        if number_of_users_in_current_dispatch == number_of_users_per_dispatch:
            break

    assert time.time() - ts_dispatch < 0.5, "Dispatch iteration took too much time: {}s".format(
        time.time() - ts_dispatch
    )

    return {
        worker_node_id: dict(sorted(user_class_occurrences.items(), key=lambda x: x[0]))
        for worker_node_id, user_class_occurrences in sorted(dispatched_users.items(), key=lambda x: x[0])
    }


def go_to_next_user_class(
    user_class: str,
    user_class_occurrences: Dict[str, int],
    dispatched_users: Dict[str, Dict[str, int]],
    effective_balanced_users: Dict[str, Dict[str, int]],
) -> bool:
    """
    Whether to skip to next user class or not. This is done so that
    the distribution of user class stays approximately balanced during
    a ramp up.
    """
    dispatched_user_class_occurrences = {
        user_class_: sum(x[user_class_] for x in dispatched_users.values())
        for user_class_ in user_class_occurrences.keys()
    }
    for user_class_ in sorted(user_class_occurrences.keys()):
        if user_class_ == user_class:
            continue
        if sum(x[user_class_] for x in effective_balanced_users.values()) == 0:
            continue
        if dispatched_user_class_occurrences[user_class] - dispatched_user_class_occurrences[user_class_] >= 1:
            return True
    return False


def number_of_users_left_to_dispatch(
    dispatched_users: Dict[str, Dict[str, int]],
    balanced_users: Dict[str, Dict[str, int]],
    user_class_occurrences: Dict[str, int],
) -> int:
    return sum(
        max(
            0,
            sum(x[user_class] for x in balanced_users.values()) - sum(x[user_class] for x in dispatched_users.values()),
        )
        for user_class in user_class_occurrences.keys()
    )


def all_users_have_been_dispatched(
    dispatched_users: Dict[str, Dict[str, int]],
    effective_balanced_users: Dict[str, Dict[str, int]],
    user_class_occurrences: Dict[str, int],
) -> bool:
    return all(
        sum(x[user_class] for x in dispatched_users.values())
        >= sum(x[user_class] for x in effective_balanced_users.values())
        for user_class in user_class_occurrences.keys()
    )


def all_users_of_current_class_have_been_dispatched(
    effective_balanced_users: Dict[str, Dict[str, int]],
    user_class: str,
) -> bool:
    return all(x[user_class] == 0 for x in effective_balanced_users.values())


def balance_users_among_workers(
    worker_nodes,  # type: List[WorkerNode]
    user_class_occurrences: Dict[str, int],
) -> Dict[str, Dict[str, int]]:
    """
    Balance the users among the workers so that
    each worker gets around the same number of users of each user class
    """
    balanced_users = {
        worker_node.id: {user_class: 0 for user_class in sorted(user_class_occurrences.keys())}
        for worker_node in worker_nodes
    }

    user_class_occurrences = user_class_occurrences.copy()

    total_users = sum(user_class_occurrences.values())
    users_per_worker, remainder = divmod(total_users, len(worker_nodes))

    for user_class in sorted(user_class_occurrences.keys()):
        if sum(user_class_occurrences.values()) == 0:
            break
        for worker_node in itertools.cycle(worker_nodes):
            if user_class_occurrences[user_class] == 0:
                break
            if (
                sum(balanced_users[worker_node.id].values()) == users_per_worker
                and total_users - sum(map(sum, map(lambda x: x.values(), balanced_users.values()))) > remainder
            ):
                continue
            elif (
                sum(balanced_users[worker_node.id].values()) == users_per_worker + 1
                and total_users - sum(map(sum, map(lambda x: x.values(), balanced_users.values()))) < remainder
            ):
                continue
            balanced_users[worker_node.id][user_class] += 1
            user_class_occurrences[user_class] -= 1

    return balanced_users
