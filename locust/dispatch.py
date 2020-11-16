import itertools
import math
import time
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
    initial_dispatched_users = {
        worker_node.id: {
            user_class: worker_node.user_class_occurrences.get(user_class, 0)
            for user_class in user_class_occurrences.keys()
        }
        for worker_node in worker_nodes
    }

    # This represents the desired users distribution
    balanced_users = balance_users_among_workers(
        worker_nodes,
        user_class_occurrences,
    )

    # This represents the desired users distribution minus the already running users
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
            number_of_users_in_current_dispatch = 0
            for user_class in user_class_occurrences.keys():
                if all(x[user_class] == 0 for x in effective_balanced_users.values()):
                    continue
                done, number_of_users_in_current_dispatch = distribute_current_user_class_among_workers(
                    dispatched_users,
                    effective_balanced_users,
                    user_class,
                    number_of_users_in_current_dispatch,
                    number_of_users_per_dispatch,
                )
                if done:
                    break

            ts = time.time()
            yield {
                worker_node_id: dict(sorted(user_class_occurrences.items(), key=lambda x: x[0]))
                for worker_node_id, user_class_occurrences in sorted(dispatched_users.items(), key=lambda x: x[0])
            }
            if sum(sum(x.values()) for x in effective_balanced_users.values()) > 0:
                delta = time.time() - ts
                gevent.sleep(max(0.0, wait_between_dispatch - delta))

    elif (
            not less_users_than_desired
            and number_of_users_left_to_dispatch(dispatched_users, balanced_users, user_class_occurrences) <= number_of_users_per_dispatch
    ):
        yield balanced_users

    else:
        while not all_users_have_been_dispatched(dispatched_users, effective_balanced_users, user_class_occurrences):
            number_of_users_in_current_dispatch = 0
            for user_class in user_class_occurrences.keys():
                if all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, user_class):
                    continue
                done, number_of_users_in_current_dispatch = distribute_current_user_class_among_workers(
                    dispatched_users,
                    effective_balanced_users,
                    user_class,
                    number_of_users_in_current_dispatch,
                    number_of_users_per_dispatch,
                )
                if done:
                    break

            ts = time.time()
            yield {
                worker_node_id: dict(sorted(user_class_occurrences.items(), key=lambda x: x[0]))
                for worker_node_id, user_class_occurrences in sorted(dispatched_users.items(), key=lambda x: x[0])
            }
            if not all_users_have_been_dispatched(dispatched_users, effective_balanced_users, user_class_occurrences):
                delta = time.time() - ts
                gevent.sleep(max(0.0, wait_between_dispatch - delta))

        # If we are here, it means we have an excess of users for one or more user classes.
        # Hence, we need to dispatch a last set of users that will bring the desired users
        # distribution to the desired one.
        # TODO: Explain why we don't stop the users at "spawn_rate"
        #       and why we stop the excess users once at the end.
        yield balanced_users


# TODO: test
def number_of_users_left_to_dispatch(
        dispatched_users: Dict[str, Dict[str, int]],
        balanced_users: Dict[str, Dict[str, int]],
        user_class_occurrences: Dict[str, int],
) -> int:
    return sum(
        max(
            0,
            sum(x[user_class] for x in balanced_users.values())
            - sum(x[user_class] for x in dispatched_users.values())
        )
        for user_class in user_class_occurrences.keys()
    )


def distribute_current_user_class_among_workers(
        dispatched_users: Dict[str, Dict[str, int]],
        effective_balanced_users: Dict[str, Dict[str, int]],
        user_class: str,
        number_of_users_in_current_dispatch: int,
        number_of_users_per_dispatch: int,
):
    done = False
    for worker_node_id in itertools.cycle(effective_balanced_users.keys()):
        if effective_balanced_users[worker_node_id][user_class] == 0:
            continue
        dispatched_users[worker_node_id][user_class] += 1
        effective_balanced_users[worker_node_id][user_class] -= 1
        number_of_users_in_current_dispatch += 1
        if number_of_users_in_current_dispatch == number_of_users_per_dispatch:
            done = True
            break
        if all(x[user_class] == 0 for x in effective_balanced_users.values()):
            break
    return done, number_of_users_in_current_dispatch


# TODO: test
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


# TODO: test
def all_users_of_current_class_have_been_dispatched(
        dispatched_users: Dict[str, Dict[str, int]],
        effective_balanced_users: Dict[str, Dict[str, int]],
        user_class: str,
) -> bool:
    return (
        sum(x[user_class] for x in dispatched_users.values())
        >= sum(x[user_class] for x in effective_balanced_users.values())
    )


# TODO: test
def add_dispatched_users(
        dispatched_users1: Dict[str, Dict[str, int]],
        dispatched_users2: Dict[str, Dict[str, int]],
) -> Dict[str, Dict[str, int]]:
    worker_node_ids = sorted(
        set(dispatched_users1.keys()).union(
            dispatched_users2.keys()
        )
    )
    user_classes = sorted(
        set(y for x in dispatched_users1.values() for y in x.keys()).union(
            y for x in dispatched_users2.values() for y in x.keys()
        )
    )
    return {
        worker_node_id: {
            user_class: (
                dispatched_users1.get(worker_node_id, {}).get(user_class, 0)
                + dispatched_users2.get(worker_node_id, {}).get(user_class, 0)
            )
            for user_class in user_classes
        }
        for worker_node_id in worker_node_ids
    }


def balance_users_among_workers(
        worker_nodes,  # type: List[WorkerNode]
        user_class_occurrences: Dict[str, int],
) -> Dict[str, Dict[str, int]]:
    balanced_users = {
        worker_node.id: {
            user_class: 0 for user_class in sorted(user_class_occurrences.keys())
        } for worker_node in worker_nodes
    }

    user_class_occurrences = user_class_occurrences.copy()

    for user_class in sorted(user_class_occurrences.keys()):
        if sum(user_class_occurrences.values()) == 0:
            break
        for worker_node in itertools.cycle(worker_nodes):
            if user_class_occurrences[user_class] == 0:
                break
            balanced_users[worker_node.id][user_class] += 1
            user_class_occurrences[user_class] -= 1

    return balanced_users
