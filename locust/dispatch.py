import itertools
import math
import time
from copy import deepcopy
from typing import (
    Dict,
    Generator,
    List,
)

import gevent

from locust.runners import WorkerNode


def dispatch_users(
        worker_nodes: List[WorkerNode],
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

    balanced_users = balance_users_among_workers(
        worker_nodes,
        user_class_occurrences,
    )

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

    wait_between_dispatch = math.ceil(1 / spawn_rate)

    number_of_users_each_dispatch = math.ceil(spawn_rate)

    dispatched_users = deepcopy(initial_dispatched_users)

    less_users_than_desired = all(
            sum(x[user_class] for x in dispatched_users.values())
            < sum(x[user_class] for x in effective_balanced_users.values())
            for user_class in user_class_occurrences.keys()
    )

    if less_users_than_desired:
        while sum(sum(x.values()) for x in effective_balanced_users.values()) > 0:
            found = False
            number_of_users_in_current_dispatch = 0
            for user_class in user_class_occurrences.keys():
                if all(x[user_class] == 0 for x in effective_balanced_users.values()):
                    continue
                for worker_node_id in itertools.cycle(effective_balanced_users.keys()):
                    if effective_balanced_users[worker_node_id][user_class] == 0:
                        continue
                    dispatched_users[worker_node_id][user_class] += 1
                    effective_balanced_users[worker_node_id][user_class] -= 1
                    number_of_users_in_current_dispatch += 1
                    if number_of_users_in_current_dispatch == number_of_users_each_dispatch:
                        found = True
                        break
                    if all(x[user_class] == 0 for x in effective_balanced_users.values()):
                        break
                if found:
                    break

            ts = time.time()
            yield {
                worker_node_id: dict(sorted(user_class_occurrences.items(), key=lambda x: x[0]))
                for worker_node_id, user_class_occurrences in sorted(dispatched_users.items(), key=lambda x: x[0])
            }
            delta = time.time() - ts
            gevent.sleep(max(0.0, wait_between_dispatch - delta))

    else:
        while sum(sum(x.values()) for x in effective_balanced_users.values()) > 0:
            found = False
            if all_users_have_been_dispatched(dispatched_users, effective_balanced_users, user_class_occurrences):
                break
            number_of_users_in_current_dispatch = 0
            for user_class in user_class_occurrences.keys():
                if all_users_of_current_class_have_been_dispatched(dispatched_users, effective_balanced_users, user_class):
                    continue
                if all(x[user_class] == 0 for x in effective_balanced_users.values()):
                    continue
                for worker_node_id in itertools.cycle(effective_balanced_users.keys()):
                    if effective_balanced_users[worker_node_id][user_class] == 0:
                        continue
                    dispatched_users[worker_node_id][user_class] += 1
                    effective_balanced_users[worker_node_id][user_class] -= 1
                    number_of_users_in_current_dispatch += 1
                    if number_of_users_in_current_dispatch == number_of_users_each_dispatch:
                        found = True
                        break
                    if all(x[user_class] == 0 for x in effective_balanced_users.values()):
                        break
                if found:
                    break

            if not found:
                # We have no more users to dispatch and
                # number_of_users_in_current_dispatch < number_of_users_each_dispatch,
                # thus we need to break out of the while loop
                break

            if all(
                    sum(x[user_class] for x in dispatched_users.values())
                    >= sum(x[user_class] for x in balanced_users.values())
                    for user_class in user_class_occurrences.keys()
            ):
                # TODO: Explain
                break

            ts = time.time()
            yield {
                worker_node_id: dict(sorted(user_class_occurrences.items(), key=lambda x: x[0]))
                for worker_node_id, user_class_occurrences in sorted(dispatched_users.items(), key=lambda x: x[0])
            }
            delta = time.time() - ts
            gevent.sleep(max(0.0, wait_between_dispatch - delta))

        # If we are here, it means we have an excess of users for one or more user classes.
        # Hence, we need to dispatch a last set of users that will bring the desired users
        # distribution to the desired one.
        # TODO: Explain why we don't stop the users at "spawn_rate"
        #       and why we stop the excess users once at the end.
        yield balanced_users


# TODO: test
def all_users_have_been_dispatched(
        dispatched_users: Dict[str, Dict[str, int]],
        effective_balanced_users: Dict[str, Dict[str, int]],
        user_class_occurrences: Dict[str, int],
) -> bool:
    return all(
        sum(x[user_class] for x in dispatched_users.values())
        > sum(x[user_class] for x in effective_balanced_users.values())
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
            > sum(x[user_class] for x in effective_balanced_users.values())
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


def current_dispatch_ready(
        balanced_users: Dict[str, Dict[str, int]],
        dispatched_users: Dict[str, Dict[str, int]],
        number_of_users_each_dispatch: int,
) -> bool:
    if sum(sum(x.values()) for x in dispatched_users.values()) == number_of_users_each_dispatch:
        return True
    if sum(sum(x.values()) for x in balanced_users.values()) == 0:
        return True
    return False


def balance_users_among_workers(
        worker_nodes: List[WorkerNode],
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
