import functools
import itertools
import math
import time
from collections.abc import Iterator
from copy import deepcopy
from operator import itemgetter, methodcaller, ne
from typing import Dict, Generator, List, TYPE_CHECKING

import gevent

if TYPE_CHECKING:
    from locust.runners import WorkerNode


class UsersDispatcher(Iterator):
    """
    Iterator that dispatches the users to the workers.
    The users already running on the workers are also taken into
    account.

    The dispatcher waits an appropriate amount of time between each iteration
    in order for the spawn rate to be respected whether running in
    local or distributed mode.

    The spawn rate is only applied when additional users are needed.
    Hence, if the desired user count contains less users than what is currently running,
    the dispatcher won't wait and will only run for
    one iteration. The rationale for not stopping users at the spawn rate
    is that stopping them is a blocking operation, especially when
    a stop timeout is specified. When a stop timeout is specified combined with users having long-running tasks,
    attempting to stop the users at a spawn rate will lead to weird behaviours (users being killed even though the
    stop timeout is not reached yet).

    The terminology used in the users dispatcher is:
      - Dispatch cycle
            A dispatch cycle corresponds to a ramp-up from start to finish. So,
            going from 10 to 100 users with a spawn rate of 1/s corresponds to one
            dispatch cycle. An instance of the `UsersDispatcher` class "lives" for
            one dispatch cycle only.
      - Dispatch iteration
            A dispatch cycle contains one or more dispatch iterations. In the previous example
            of going from 10 to 100 users with a spawn rate of 1/s, there are 100 dispatch iterations.
            That is, from 10 to 11 users is a dispatch iteration, from 12 to 13 is another, and so on.
            If the spawn rate were to be 2/s, then there would be 50 dispatch iterations for this dispatch cycle.
            For a more extreme case with a spawn rate of 120/s, there would be only a single dispatch iteration
            from 10 to 100.
    """

    def __init__(self, worker_nodes: "List[WorkerNode]", user_classes_count: Dict[str, int], spawn_rate: float):
        """
        :param worker_nodes: List of worker nodes
        :param user_classes_count: Desired number of users for each class
        :param spawn_rate: The spawn rate
        """
        # NOTE: We use "sorted" in some places in this module. It is done to ensure repeatable behaviour.
        #       This is especially important when iterating over a dictionary which, prior to py3.7, was
        #       completely unordered. For >=Py3.7, a dictionary keeps the insertion order. Even then,
        #       it is safer to sort the keys when repeatable behaviour is required.
        self._worker_nodes = sorted(worker_nodes, key=lambda w: w.id)

        self._user_classes_count = user_classes_count

        self._user_classes = sorted(user_classes_count.keys())

        self._spawn_rate = spawn_rate

        self._desired_users_assigned_to_workers = _WorkersUsersAssignor(
            user_classes_count, worker_nodes
        ).desired_users_assigned_to_workers

        # This represents the desired users distribution minus the already running users among the workers.
        # The values inside this dictionary are updated during the current dispatch cycle. For example,
        # if we dispatch 1 user of UserClass1 to worker 1, then we will decrement by 1 the user count
        # for UserClass1 of worker 1. Naturally, the current dispatch cycle is done once all the values
        # reach zero.
        self._users_left_to_assigned = {
            worker_node.id: {
                user_class: max(
                    0,
                    self._desired_users_assigned_to_workers[worker_node.id][user_class]
                    - self._initial_dispatched_users()[worker_node.id][user_class],
                )
                for user_class in self._user_classes_count.keys()
            }
            for worker_node in self._worker_nodes
        }

        self._user_count_per_dispatch = max(1, math.floor(self._spawn_rate))

        self._wait_between_dispatch = self._user_count_per_dispatch / self._spawn_rate

        # We use deepcopy because we will update the values inside `dispatched_users`
        # to keep track of the number of dispatched users for the current dispatch cycle.
        # It is essentially the same thing as for the `effective_assigned_users` dictionary,
        # but in reverse.
        self._dispatched_users = deepcopy(self._initial_dispatched_users())

        # Initialize the generator that is used in `__next__`
        self._dispatcher_generator = self._dispatcher()

    @functools.lru_cache()
    def _initial_dispatched_users(self) -> Dict[str, Dict[str, int]]:
        """Represents the already running users among the workers at the start of the dispatch"""
        return {
            worker_node.id: {
                user_class: worker_node.user_classes_count.get(user_class, 0)
                for user_class in self._user_classes_count.keys()
            }
            for worker_node in self._worker_nodes
        }

    def __next__(self) -> Dict[str, Dict[str, int]]:
        return next(self._dispatcher_generator)

    def _dispatcher(self) -> Generator[Dict[str, Dict[str, int]], None, None]:
        """Main iterator logic for dispatching users during this dispatch cycle"""
        if self._desired_users_assignment_can_be_obtained_in_a_single_dispatch_iteration:
            yield self._desired_users_assigned_to_workers

        else:
            while not self._all_users_have_been_dispatched:
                ts = time.perf_counter()
                yield self._users_to_dispatch_for_current_iteration
                if not self._all_users_have_been_dispatched:
                    delta = time.perf_counter() - ts
                    sleep_duration = max(0.0, self._wait_between_dispatch - delta)
                    assert sleep_duration <= 10, sleep_duration
                    gevent.sleep(sleep_duration)

    @property
    def _desired_users_assignment_can_be_obtained_in_a_single_dispatch_iteration(self) -> bool:
        # The following calculates the number of users left to dispatch
        # taking into account workers that have an excess of users.
        user_count_left_to_dispatch_excluding_excess_users = sum(
            max(
                0,
                sum(map(itemgetter(user_class), self._desired_users_assigned_to_workers.values()))
                - self._dispatched_user_class_count(user_class),
            )
            for user_class in self._user_classes_count.keys()
        )

        return self._user_count_per_dispatch >= user_count_left_to_dispatch_excluding_excess_users

    @property
    def _users_to_dispatch_for_current_iteration(self) -> Dict[str, Dict[str, int]]:
        """
        Compute the users to dispatch for the current dispatch iteration.
        """
        if all(
            self._dispatched_user_class_count(user_class) >= user_count
            for user_class, user_count in self._user_classes_count.items()
        ):
            # User count for every user class is greater than or equal to the target user count of each class.
            # This means that we're at the last iteration of this dispatch cycle. If some user classes are in
            # excess, this last iteration will stop those excess users.
            self._dispatched_users.update(self._desired_users_assigned_to_workers)
            self._users_left_to_assigned.update(
                {
                    worker_node_id: {user_class: 0 for user_class in user_classes_count.keys()}
                    for worker_node_id, user_classes_count in self._dispatched_users.items()
                }
            )

        else:
            user_count_in_current_dispatch = 0

            for i, user_class_to_add in enumerate(itertools.cycle(self._user_classes)):
                # For large number of user classes and large number of workers, this assertion might fail.
                # If this happens, you can remove it or increase the threshold. Right now, the assertion
                # is there as a safeguard for situations that can't be easily tested (i.e. large scale distributed tests).
                assert i < 5000, "Looks like dispatch is stuck in an infinite loop (iteration {})".format(i)

                if self._all_users_have_been_dispatched:
                    break

                if all(
                    self._dispatched_user_class_count(user_class) >= user_count
                    for user_class, user_count in self._user_classes_count.items()
                ):
                    break

                if self._dispatched_user_class_count(user_class_to_add) >= self._user_classes_count[user_class_to_add]:
                    continue

                if self._try_next_user_class_in_order_to_stay_balanced_during_ramp_up(user_class_to_add):
                    continue

                for j, worker_node_id in enumerate(itertools.cycle(sorted(self._users_left_to_assigned.keys()))):
                    assert j < int(
                        2 * self._number_of_workers
                    ), "Looks like dispatch is stuck in an infinite loop (iteration {})".format(j)
                    if self._users_left_to_assigned[worker_node_id][user_class_to_add] == 0:
                        continue
                    self._dispatched_users[worker_node_id][user_class_to_add] += 1
                    self._users_left_to_assigned[worker_node_id][user_class_to_add] -= 1
                    user_count_in_current_dispatch += 1
                    break

                if user_count_in_current_dispatch == self._user_count_per_dispatch:
                    break

        return {
            worker_node_id: dict(sorted(user_classes_count.items(), key=itemgetter(0)))
            for worker_node_id, user_classes_count in sorted(self._dispatched_users.items(), key=itemgetter(0))
        }

    @property
    def _number_of_workers(self) -> int:
        return len(self._users_left_to_assigned)

    @property
    def _all_users_have_been_dispatched(self) -> bool:
        user_count_left_to_dispatch = sum(map(sum, map(dict.values, self._users_left_to_assigned.values())))
        return user_count_left_to_dispatch == 0

    def _try_next_user_class_in_order_to_stay_balanced_during_ramp_up(self, user_class_to_add: str) -> bool:
        """
        Whether to skip to the next user class or not. This is done so that
        the distribution of user class stays approximately balanced from one dispatch
        iteration to another.
        """
        # For performance reasons, we use `functools.lru_cache()` on the `self._dispatched_user_classes_count`
        # method because its value does not change within the scope of the current method. However, the next time
        # `self._try_next_user_class_in_order_to_stay_balanced_during_ramp_up` is invoked, we need
        # `self._dispatched_user_classes_count` to be recomputed.
        self._dispatched_user_classes_count.cache_clear()

        if all(user_count > 0 for user_count in self._dispatched_user_classes_count().values()):
            # We're here because each user class have at least one user running. Thus,
            # we need to ensure that the distribution of users corresponds to the weights.
            if not self._adding_this_user_class_respects_distribution_better_than_adding_any_other_user_class(
                user_class_to_add
            ):
                return True
            else:
                return False

        else:
            # Because each user class doesn't have at least one running user, we use a simpler strategy
            # that make sure each user class appears once.
            for next_user_class in filter(functools.partial(ne, user_class_to_add), self._user_classes):
                if sum(map(itemgetter(next_user_class), self._users_left_to_assigned.values())) == 0:
                    # No more users of class `next_user_class` to dispatch
                    continue
                if (
                    self._dispatched_user_classes_count()[user_class_to_add]
                    - self._dispatched_user_classes_count()[next_user_class]
                    >= 1
                ):
                    # There's already enough users for `user_class_to_add` in the current dispatch. Hence, we should
                    # not consider `user_class_to_add` and go to the next user class instead.
                    return True
            return False

    def _dispatched_user_class_count(self, user_class: str) -> int:
        """Number of dispatched users at this time for the given user class"""
        return sum(map(itemgetter(user_class), self._dispatched_users.values()))

    def _adding_this_user_class_respects_distribution_better_than_adding_any_other_user_class(
        self, user_class_to_add: str
    ) -> bool:
        distance = self._distance_from_ideal_distribution()
        distance_after_adding_user_class = self._distance_from_ideal_distribution_after_adding_this_user_class(
            user_class_to_add
        )
        if distance_after_adding_user_class > distance and all(
            not self._adding_this_user_class_respects_distribution(user_class)
            for user_class in self._user_classes_count.keys()
            if user_class != user_class_to_add
        ):
            # If we are here, it means that if one user of `user_class_to_add` is added
            # then the distribution will be the best we can get. In other words, adding
            # one user of any other user class won't yield a better distribution.
            return True
        return distance_after_adding_user_class <= distance

    def _adding_this_user_class_respects_distribution(self, user_class_to_add: str) -> bool:
        if (
            self._distance_from_ideal_distribution_after_adding_this_user_class(user_class_to_add)
            <= self._distance_from_ideal_distribution()
        ):
            return True
        return False

    def _distance_from_ideal_distribution(self) -> float:
        """How far are we from the ideal distribution given the current set of running users?"""
        weights = [
            self._dispatched_user_classes_count()[user_class] / sum(self._dispatched_user_classes_count().values())
            for user_class in self._user_classes
        ]

        return math.sqrt(sum(map(lambda x: (x[1] - x[0]) ** 2, zip(weights, self._desired_relative_weights()))))

    def _distance_from_ideal_distribution_after_adding_this_user_class(self, user_class_to_add: str) -> float:
        """
        How far are we from the ideal distribution if we were to add `user_class_to_add` to the pool of running users?
        """
        relative_weights_with_added_user_class = [
            (
                self._dispatched_user_classes_count()[user_class] + 1
                if user_class == user_class_to_add
                else self._dispatched_user_classes_count()[user_class]
            )
            / (sum(self._dispatched_user_classes_count().values()) + 1)
            for user_class in self._user_classes
        ]

        return math.sqrt(
            sum(
                map(
                    lambda x: (x[1] - x[0]) ** 2,
                    zip(relative_weights_with_added_user_class, self._desired_relative_weights()),
                )
            )
        )

    @functools.lru_cache()
    def _desired_relative_weights(self) -> List[float]:
        """The relative weight of each user class we desire"""
        return [
            self._user_classes_count[user_class] / sum(self._user_classes_count.values())
            for user_class in self._user_classes
        ]

    @functools.lru_cache()
    def _dispatched_user_classes_count(self) -> Dict[str, int]:
        """The user count for each user class that are dispatched at this time"""
        return {
            user_class: self._dispatched_user_class_count(user_class) for user_class in self._user_classes_count.keys()
        }


class _WorkersUsersAssignor:
    """Helper to compute the users assigned to the workers"""

    def __init__(self, user_classes_count: Dict[str, int], worker_nodes: "List[WorkerNode]"):
        self._user_classes_count = user_classes_count
        self._user_classes = sorted(user_classes_count.keys())
        self._worker_nodes = sorted(worker_nodes, key=lambda w: w.id)

    @property
    def desired_users_assigned_to_workers(self) -> Dict[str, Dict[str, int]]:
        """The users assigned to the workers.

        The assignment is done in a way that each worker gets around the same number of users of each user class.
        If some user classes are more represented than others, then it is not possible to equally distribute
        the users from each user class to all workers. It is done in a best-effort.

        The assignment also ensures that each worker runs the same amount of users (irrespective of the user class
        of those users). If the total user count does not yield an integer when divided by the number of workers,
        then some workers will have one more user than the others.
        """
        assigned_users = {
            worker_node.id: {user_class: 0 for user_class in self._user_classes} for worker_node in self._worker_nodes
        }

        # We need to copy to prevent modifying `user_classes_count`.
        user_classes_count = self._user_classes_count.copy()

        user_count = sum(user_classes_count.values())

        # If `remainder > 0`, it means that some workers will have `users_per_worker + 1` users.
        users_per_worker, remainder = divmod(user_count, len(self._worker_nodes))

        for user_class in self._user_classes:
            if sum(user_classes_count.values()) == 0:
                # No more users of any user class to assign to workers, so we can exit this loop.
                break

            # Assign users of `user_class` to the workers in a round-robin fashion.
            for worker_node in itertools.cycle(self._worker_nodes):
                if user_classes_count[user_class] == 0:
                    break

                number_of_users_left_to_assign = user_count - self._number_of_assigned_users_across_workers(
                    assigned_users
                )

                if (
                    self._number_of_assigned_users_for_worker(assigned_users, worker_node) == users_per_worker
                    and number_of_users_left_to_assign > remainder
                ):
                    continue

                elif (
                    self._number_of_assigned_users_for_worker(assigned_users, worker_node) == users_per_worker + 1
                    and number_of_users_left_to_assign < remainder
                ):
                    continue

                assigned_users[worker_node.id][user_class] += 1
                user_classes_count[user_class] -= 1

        return assigned_users

    @staticmethod
    def _number_of_assigned_users_for_worker(
        assigned_users: Dict[str, Dict[str, int]], worker_node: "WorkerNode"
    ) -> int:
        """User count running on the given worker"""
        return sum(assigned_users[worker_node.id].values())

    @staticmethod
    def _number_of_assigned_users_across_workers(assigned_users: Dict[str, Dict[str, int]]) -> int:
        """Total user count running on the workers"""
        return sum(map(sum, map(methodcaller("values"), assigned_users.values())))
