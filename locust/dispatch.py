import contextlib
import itertools
import math
import time
from collections.abc import Iterator
from operator import attrgetter
from typing import Dict, Generator, List, TYPE_CHECKING, Tuple, Type

import gevent
import typing

from roundrobin import smooth

from locust import User

if TYPE_CHECKING:
    from locust.runners import WorkerNode


# To profile line-by-line, uncomment the code below (i.e. `import line_profiler ...`) and
# place `@profile` on the functions/methods you wish to profile. Then, in the unit test you are
# running, use `from locust.dispatch import profile; profile.print_stats()` at the end of the unit test.
# Placing it in a `finally` block is recommended.
# import line_profiler
#
# profile = line_profiler.LineProfiler()


class UsersDispatcher(Iterator):
    """
    Iterator that dispatches the users to the workers.

    The dispatcher waits an appropriate amount of time between each iteration
    in order for the spawn rate to be respected whether running in
    local or distributed mode.

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

    def __init__(self, worker_nodes: "List[WorkerNode]", user_classes: List[Type[User]]):
        """
        :param worker_nodes: List of worker nodes
        :param user_classes: The user classes
        """
        # NOTE: We use "sorted" to ensure repeatable behaviour.
        #       This is especially important when iterating over a dictionary which, prior to py3.7, was
        #       completely unordered. For >=Py3.7, a dictionary keeps the insertion order. Even then,
        #       it is safer to sort the keys when repeatable behaviour is required.
        self._worker_nodes = sorted(worker_nodes, key=lambda w: w.id)

        self._user_classes = sorted(user_classes, key=attrgetter("__name__"))

        assert len(user_classes) > 0
        assert len(set(self._user_classes)) == len(self._user_classes)

        self._target_user_count = None

        self._spawn_rate = None

        self._user_count_per_dispatch_iteration = None

        self._wait_between_dispatch = None

        self._initial_users_on_workers = {
            worker_node.id: {user_class.__name__: 0 for user_class in self._user_classes}
            for worker_node in worker_nodes
        }

        self._users_on_workers = self._fast_users_on_workers_copy(self._initial_users_on_workers)

        self._current_user_count = sum(map(sum, map(dict.values, self._users_on_workers.values())))

        self._dispatcher_generator = None

        self._user_generator = self._user_gen()

        self._worker_node_generator = itertools.cycle(self._worker_nodes)

        # To keep track of how long it takes for each dispatch iteration to compute
        self._dispatch_iteration_durations = []

        self._active_users = []

        # TODO: Test that attribute is set when dispatching and unset when done dispatching
        self._dispatch_in_progress = False

        self._rebalance = False

    @property
    def dispatch_in_progress(self):
        return self._dispatch_in_progress

    @property
    def dispatch_iteration_durations(self) -> List[float]:
        return self._dispatch_iteration_durations

    def __next__(self) -> Dict[str, Dict[str, int]]:
        users_on_workers = next(self._dispatcher_generator)
        # TODO: Is this necessary to copy the users_on_workers if we know
        #       it won't be mutated by external code?
        return self._fast_users_on_workers_copy(users_on_workers)

    def _dispatcher(self) -> Generator[Dict[str, Dict[str, int]], None, None]:
        self._dispatch_in_progress = True

        if self._rebalance:
            self._rebalance = False
            yield self._users_on_workers
            if self._current_user_count == self._target_user_count:
                return

        if self._current_user_count == self._target_user_count:
            yield self._initial_users_on_workers
            self._dispatch_in_progress = False
            return

        while self._current_user_count < self._target_user_count:
            with self._wait_between_dispatch_iteration_context():
                yield self._add_users_on_workers()
                if self._rebalance:
                    self._rebalance = False
                    yield self._users_on_workers

        while self._current_user_count > self._target_user_count:
            with self._wait_between_dispatch_iteration_context():
                yield self._remove_users_from_workers()
                if self._rebalance:
                    self._rebalance = False
                    yield self._users_on_workers

        self._dispatch_in_progress = False

    def new_dispatch(self, target_user_count: int, spawn_rate: float) -> None:
        """
        Initialize a new dispatch cycle.

        :param target_user_count: The desired user count at the end of the dispatch cycle
        :param spawn_rate: The spawn rate
        """
        self._target_user_count = target_user_count

        self._spawn_rate = spawn_rate

        self._user_count_per_dispatch_iteration = max(1, math.floor(self._spawn_rate))

        self._wait_between_dispatch = self._user_count_per_dispatch_iteration / self._spawn_rate

        self._initial_users_on_workers = self._users_on_workers

        self._users_on_workers = self._fast_users_on_workers_copy(self._initial_users_on_workers)

        self._current_user_count = sum(map(sum, map(dict.values, self._users_on_workers.values())))

        self._dispatcher_generator = self._dispatcher()

        self._dispatch_iteration_durations.clear()

    def add_worker(self, worker_node: "WorkerNode") -> None:
        """
        This method is to be called when a new worker connects to the master. When
        a new worker is added, the users dispatcher will flag that a rebalance is required
        and ensure that the next dispatch iteration will be made to redistribute the users
        on the new pool of workers.

        :param worker_node: The worker node to add.
        """
        self._worker_nodes.append(worker_node)
        self._worker_nodes = sorted(self._worker_nodes, key=lambda w: w.id)
        self._prepare_rebalance()

    def remove_worker(self, worker_node: "WorkerNode") -> None:
        """
        This method is similar to the above `add_worker`. When a worker disconnects
        (because of e.g. network failure, worker failure, etc.), this method will ensure that the next
        dispatch iteration redistributes the users on the remaining workers.

        :param worker_node: The worker node to remove.
        """
        self._worker_nodes = [w for w in self._worker_nodes if w.id != worker_node.id]
        if len(self._worker_nodes) == 0:
            # TODO: Test this
            return
        self._prepare_rebalance()

    def _prepare_rebalance(self) -> None:
        """
        When a rebalance is required because of added and/or removed workers, we compute the desired state as if
        we started from 0 user. So, if we were currently running 500 users, then the `_distribute_users` will
        perform a fake ramp-up without any waiting and return the final distribution.
        """
        users_on_workers, user_gen, worker_gen, active_users = self._distribute_users(self._current_user_count)

        self._users_on_workers = users_on_workers
        self._active_users = active_users

        # It's important to reset the generators by using the ones from `_distribute_users`
        # so that the next iterations are smooth and continuous.
        self._user_generator = user_gen
        self._worker_node_generator = worker_gen

        self._rebalance = True

    @contextlib.contextmanager
    def _wait_between_dispatch_iteration_context(self) -> None:
        t0_rel = time.perf_counter()

        # We don't use `try: ... finally: ...` because we don't want to sleep
        # if there's an exception within the context.
        yield

        delta = time.perf_counter() - t0_rel

        self._dispatch_iteration_durations.append(delta)

        # print("Dispatch cycle took {:.3f}ms".format(delta * 1000))

        if self._current_user_count == self._target_user_count:
            # No sleep when this is the last dispatch iteration
            return

        sleep_duration = max(0.0, self._wait_between_dispatch - delta)
        gevent.sleep(sleep_duration)

    def _add_users_on_workers(self) -> Dict[str, Dict[str, int]]:
        """Add users on the workers until the target number of users is reached for the current dispatch iteration

        :return: The users that we want to run on the workers
        """
        current_user_count_target = min(
            self._current_user_count + self._user_count_per_dispatch_iteration, self._target_user_count
        )
        for user in self._user_generator:
            worker_node = next(self._worker_node_generator)
            self._users_on_workers[worker_node.id][user] += 1
            self._current_user_count += 1
            self._active_users.append((worker_node, user))
            if self._current_user_count >= current_user_count_target:
                return self._users_on_workers

    def _remove_users_from_workers(self) -> Dict[str, Dict[str, int]]:
        """Remove users from the workers until the target number of users is reached for the current dispatch iteration

        :return: The users that we want to run on the workers
        """
        current_user_count_target = max(
            self._current_user_count - self._user_count_per_dispatch_iteration, self._target_user_count
        )
        while True:
            try:
                worker_node, user = self._active_users.pop()
            except IndexError:
                return self._users_on_workers
            self._users_on_workers[worker_node.id][user] -= 1
            self._current_user_count -= 1
            if self._current_user_count == 0 or self._current_user_count <= current_user_count_target:
                return self._users_on_workers

    def _distribute_users(
        self, target_user_count: int
    ) -> Tuple[dict, Generator[str, None, None], typing.Iterator["WorkerNode"], List[Tuple["WorkerNode", str]]]:
        """
        This function might take some time to complete if the `target_user_count` is a big number. A big number
        is typically > 50 000. However, this function is only called if a worker is added or removed while a test
        is running. Such a situation should be quite rare.
        """
        user_gen = self._user_gen()

        worker_gen = itertools.cycle(self._worker_nodes)

        users_on_workers = {
            worker_node.id: {user_class.__name__: 0 for user_class in self._user_classes}
            for worker_node in self._worker_nodes
        }

        active_users = []

        user_count = 0
        while user_count < target_user_count:
            user = next(user_gen)
            worker_node = next(worker_gen)
            users_on_workers[worker_node.id][user] += 1
            user_count += 1
            active_users.append((worker_node, user))

        return users_on_workers, user_gen, worker_gen, active_users

    def _user_gen(self) -> Generator[str, None, None]:
        """
        This method generates users according to their weights using
        a smooth weighted round-robin algorithm implemented by https://github.com/linnik/roundrobin.

        For example, given users A, B with weights 5 and 1 respectively, this algorithm
        will yield AAABAAAAABAA. The smooth aspect of this algorithm is what makes it possible
        to keep the distribution during ramp-up and ramp-down. If we were to use a normal
        weighted round-robin algorithm, we'd get AAAAABAAAAAB which would make the distribution
        less accurate during ramp-up/down.
        """
        # Normalize the weights so that the smallest weight will be equal to "target_min_weight".
        # The value "2" was experimentally determined because it gave a better distribution especially
        # when dealing with weights which are close to each others, e.g. 1.5, 2, 2.4, etc.
        target_min_weight = 2
        min_weight = min(u.weight for u in self._user_classes)
        normalized_weights = [
            (user_class.__name__, round(target_min_weight * user_class.weight / min_weight))
            for user_class in self._user_classes
        ]
        gen = smooth(normalized_weights)
        # Instead of calling `gen()` for each user, we cycle through a generator of fixed-length
        # `generation_length_to_get_proper_distribution`. Doing so greatly improves performance because
        # we only ever need to call `gen()` a relatively small number of times. The length of this generator
        # is chosen as the sum of the normalized weights. So, for users A, B, C of weights 2, 5, 6, the length is
        # 2 + 5 + 6 = 13 which would yield the distribution `CBACBCBCBCABC` that gets repeated over and over
        # until the target user count is reached.
        generation_length_to_get_proper_distribution = sum(
            normalized_weight[1] for normalized_weight in normalized_weights
        )
        yield from itertools.cycle(gen() for _ in range(generation_length_to_get_proper_distribution))

    @staticmethod
    def _fast_users_on_workers_copy(users_on_workers: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
        """deepcopy is too slow, so we use this custom copy function.

        The implementation was profiled and compared to other implementations such as dict-comprehensions
        and the one below is the most efficient.
        """
        return dict(zip(users_on_workers.keys(), map(dict.copy, users_on_workers.values())))
