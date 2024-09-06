from __future__ import annotations

import contextlib
import itertools
import math
import time
from collections import defaultdict
from collections.abc import Iterator
from heapq import heapify, heapreplace
from math import log2
from operator import attrgetter
from typing import TYPE_CHECKING

import gevent

if TYPE_CHECKING:
    from locust import User
    from locust.runners import WorkerNode

    from collections.abc import Generator, Iterable
    from typing import TypeVar

    T = TypeVar("T")


def _kl_generator(users: Iterable[tuple[T, float]]) -> Generator[T | None]:
    """Generator based on Kullback-Leibler divergence

    For example, given users A, B with weights 5 and 1 respectively,
    this algorithm will yield AAABAAAAABAA.
    """
    heap = [(x * log2(x / (x + 1.0)), x + 1.0, x, name) for name, x in users if x > 0]
    if not heap:
        while True:
            yield None

    heapify(heap)
    while True:
        _, x, weight, name = heap[0]
        # (divergence diff, number of generated elements + initial weight, initial weight, name) = heap[0]
        yield name
        kl_diff = weight * log2(x / (x + 1.0))
        # calculate how much choosing element i for (x + 1)th time decreases divergence
        heapreplace(heap, (kl_diff, x + 1.0, weight, name))


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

    def __init__(self, worker_nodes: list[WorkerNode], user_classes: list[type[User]]):
        """
        :param worker_nodes: List of worker nodes
        :param user_classes: The user classes
        """
        self._worker_nodes = worker_nodes
        self._sort_workers()
        self._original_user_classes = sorted(user_classes, key=attrgetter("__name__"))
        self._user_classes = sorted(user_classes, key=attrgetter("__name__"))

        assert len(user_classes) > 0
        assert len(set(self._user_classes)) == len(self._user_classes)

        self._target_user_count: int = 0

        self._spawn_rate: float = 0.0

        self._user_count_per_dispatch_iteration: int = 0

        self._wait_between_dispatch: float = 0.0

        self._initial_users_on_workers = {
            worker_node.id: {user_class.__name__: 0 for user_class in self._user_classes}
            for worker_node in worker_nodes
        }

        self._users_on_workers = self._fast_users_on_workers_copy(self._initial_users_on_workers)

        self._current_user_count = self.get_current_user_count()

        self._dispatcher_generator: Generator[dict[str, dict[str, int]]] = None  # type: ignore
        # a generator is assigned (in new_dispatch()) to _dispatcher_generator before it's used

        self._user_generator = self._user_gen()

        self._worker_node_generator = itertools.cycle(self._worker_nodes)

        # To keep track of how long it takes for each dispatch iteration to compute
        self._dispatch_iteration_durations: list[float] = []

        self._active_users: list[tuple[WorkerNode, str]] = []

        # TODO: Test that attribute is set when dispatching and unset when done dispatching
        self._dispatch_in_progress = False

        self._rebalance = False

        self._try_dispatch_fixed = True

        self._no_user_to_spawn = False

    def get_current_user_count(self) -> int:
        return sum(map(sum, map(dict.values, self._users_on_workers.values())))

    @property
    def dispatch_in_progress(self) -> bool:
        return self._dispatch_in_progress

    @property
    def dispatch_iteration_durations(self) -> list[float]:
        return self._dispatch_iteration_durations

    def __next__(self) -> dict[str, dict[str, int]]:
        users_on_workers = next(self._dispatcher_generator)
        # TODO: Is this necessary to copy the users_on_workers if we know
        #       it won't be mutated by external code?
        return self._fast_users_on_workers_copy(users_on_workers)

    def _sort_workers(self):
        # Sorting workers ensures repeatable behaviour
        worker_nodes_by_id = sorted(self._worker_nodes, key=lambda w: w.id)

        # Give every worker an index indicating how many workers came before it on that host
        workers_per_host = defaultdict(int)
        for worker_node in worker_nodes_by_id:
            host = worker_node.id.split("_")[0]
            worker_node._index_within_host = workers_per_host[host]
            workers_per_host[host] = workers_per_host[host] + 1

        # Sort again, first by index within host, to ensure Users get started evenly across hosts
        self._worker_nodes = sorted(self._worker_nodes, key=lambda worker: (worker._index_within_host, worker.id))

    def _dispatcher(self) -> Generator[dict[str, dict[str, int]]]:
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
                if self._no_user_to_spawn:
                    self._no_user_to_spawn = False
                    break

        while self._current_user_count > self._target_user_count:
            with self._wait_between_dispatch_iteration_context():
                yield self._remove_users_from_workers()
                if self._rebalance:
                    self._rebalance = False
                    yield self._users_on_workers

        self._dispatch_in_progress = False

    def new_dispatch(
        self, target_user_count: int, spawn_rate: float, user_classes: list[type[User]] | None = None
    ) -> None:
        """
        Initialize a new dispatch cycle.

        :param target_user_count: The desired user count at the end of the dispatch cycle
        :param spawn_rate: The spawn rate
        :param user_classes: The user classes to be used for the new dispatch
        """
        if user_classes is not None and self._user_classes != sorted(user_classes, key=attrgetter("__name__")):
            self._user_classes = sorted(user_classes, key=attrgetter("__name__"))
            self._user_generator = self._user_gen()

        self._target_user_count = target_user_count

        self._spawn_rate = spawn_rate

        self._user_count_per_dispatch_iteration = max(1, math.floor(self._spawn_rate))

        self._wait_between_dispatch = self._user_count_per_dispatch_iteration / self._spawn_rate

        self._initial_users_on_workers = self._users_on_workers

        self._users_on_workers = self._fast_users_on_workers_copy(self._initial_users_on_workers)

        self._current_user_count = self.get_current_user_count()

        self._dispatcher_generator = self._dispatcher()

        self._dispatch_iteration_durations.clear()

    def add_worker(self, worker_node: WorkerNode) -> None:
        """
        This method is to be called when a new worker connects to the master. When
        a new worker is added, the users dispatcher will flag that a rebalance is required
        and ensure that the next dispatch iteration will be made to redistribute the users
        on the new pool of workers.

        :param worker_node: The worker node to add.
        """
        self._worker_nodes.append(worker_node)
        self._sort_workers()
        self._prepare_rebalance()

    def remove_worker(self, worker_node: WorkerNode) -> None:
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
        # Reset users before recalculating since the current users is used to calculate how many
        # fixed users to add.
        self._users_on_workers = {
            worker_node.id: {user_class.__name__: 0 for user_class in self._original_user_classes}
            for worker_node in self._worker_nodes
        }
        self._try_dispatch_fixed = True

        users_on_workers, user_gen, worker_gen, active_users = self._distribute_users(self._current_user_count)

        self._users_on_workers = users_on_workers
        self._active_users = active_users

        # It's important to reset the generators by using the ones from `_distribute_users`
        # so that the next iterations are smooth and continuous.
        self._user_generator = user_gen
        self._worker_node_generator = worker_gen

        self._rebalance = True

    @contextlib.contextmanager
    def _wait_between_dispatch_iteration_context(self) -> Generator[None]:
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

    def _add_users_on_workers(self) -> dict[str, dict[str, int]]:
        """Add users on the workers until the target number of users is reached for the current dispatch iteration

        :return: The users that we want to run on the workers
        """
        current_user_count_target = min(
            self._current_user_count + self._user_count_per_dispatch_iteration, self._target_user_count
        )

        for user in self._user_generator:
            if not user:
                self._no_user_to_spawn = True
                break
            worker_node = next(self._worker_node_generator)
            self._users_on_workers[worker_node.id][user] += 1
            self._current_user_count += 1
            self._active_users.append((worker_node, user))
            if self._current_user_count >= current_user_count_target:
                break

        return self._users_on_workers

    def _remove_users_from_workers(self) -> dict[str, dict[str, int]]:
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
            self._try_dispatch_fixed = True
            if self._current_user_count == 0 or self._current_user_count <= current_user_count_target:
                return self._users_on_workers

    def _get_user_current_count(self, user: str) -> int:
        count = 0
        for users_on_node in self._users_on_workers.values():
            count += users_on_node.get(user, 0)

        return count

    def _distribute_users(
        self, target_user_count: int
    ) -> tuple[dict[str, dict[str, int]], Iterator[str | None], itertools.cycle, list[tuple[WorkerNode, str]]]:
        """
        This function might take some time to complete if the `target_user_count` is a big number. A big number
        is typically > 50 000. However, this function is only called if a worker is added or removed while a test
        is running. Such a situation should be quite rare.
        """
        user_gen = self._user_gen()

        worker_gen = itertools.cycle(self._worker_nodes)

        users_on_workers = {
            worker_node.id: {user_class.__name__: 0 for user_class in self._original_user_classes}
            for worker_node in self._worker_nodes
        }

        active_users = []

        user_count = 0
        while user_count < target_user_count:
            user = next(user_gen)
            if not user:
                break
            worker_node = next(worker_gen)
            users_on_workers[worker_node.id][user] += 1
            user_count += 1
            active_users.append((worker_node, user))

        return users_on_workers, user_gen, worker_gen, active_users

    def _user_gen(self) -> Iterator[str | None]:
        weighted_users_gen = _kl_generator((u.__name__, u.weight) for u in self._user_classes if not u.fixed_count)

        while True:
            if self._try_dispatch_fixed:  # Fixed_count users are spawned before weight users.
                # Some peoples treat this implementation detail as a feature.
                self._try_dispatch_fixed = False
                fixed_users_missing = [
                    (u.__name__, miss)
                    for u in self._user_classes
                    if u.fixed_count and (miss := u.fixed_count - self._get_user_current_count(u.__name__)) > 0
                ]
                total_miss = sum(miss for _, miss in fixed_users_missing)
                fixed_users_gen = _kl_generator(fixed_users_missing)  # type: ignore[arg-type]
                # https://mypy.readthedocs.io/en/stable/common_issues.html#variance
                for _ in range(total_miss):
                    yield next(fixed_users_gen)
            else:
                yield next(weighted_users_gen)

    @staticmethod
    def _fast_users_on_workers_copy(users_on_workers: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
        """deepcopy is too slow, so we use this custom copy function.

        The implementation was profiled and compared to other implementations such as dict-comprehensions
        and the one below is the most efficient.
        """
        return dict(zip(users_on_workers.keys(), map(dict.copy, users_on_workers.values())))
