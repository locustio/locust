from __future__ import annotations

import contextlib
import itertools
import math
import time
import logging
from operator import attrgetter, itemgetter
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    TypeVar,
    Iterator,
    Optional,
    final,
    overload,
    SupportsIndex,
)
from abc import ABCMeta, abstractmethod

import gevent

from roundrobin import smooth

if TYPE_CHECKING:
    from locust.runners import WorkerNode
    from locust.user import User

T = TypeVar("T")


# To profile line-by-line, uncomment the code below (i.e. `import line_profiler ...`) and
# place `@profile` on the functions/methods you wish to profile. Then, in the unit test you are
# running, use `from locust.dispatch import profile; profile.print_stats()` at the end of the unit test.
# Placing it in a `finally` block is recommended.
# import line_profiler
#
# profile = line_profiler.LineProfiler()

UserGenerator = Generator[Optional[str], None, None]
DistributedUsers = Dict[str, Dict[str, int]]
DispatcherGenerator = Generator[DistributedUsers, None, None]


logger = logging.getLogger(__name__)


class LengthOptimizedList(List[T]):
    """Simple implementation of a list that keeps track of its length for speed optimizations."""

    __optimized_length__: int

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.__optimized_length__ = 0

    def append(self, __object: Any) -> None:
        self.__optimized_length__ += 1
        super().append(__object)

    def pop(self, __index: SupportsIndex = -1) -> Any:
        self.__optimized_length__ -= 1
        return super().pop(__index)

    def __getattribute__(self, __name: str) -> Any:
        if __name not in ["append", "pop", "__optimized_length__", "__class__"]:
            raise NotImplementedError(f"{__name} is not implemented")
        return super().__getattribute__(__name)

    def __len__(self) -> int:
        return self.__optimized_length__


class UsersDispatcher(Iterator[DistributedUsers], metaclass=ABCMeta):
    """Base class for user dispatcher implementations.

    A dispatcher waits an appropriate amount of time between each iteration
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
        self._worker_nodes = worker_nodes
        self._sort_workers()
        self._user_classes = sorted(user_classes, key=attrgetter("__name__"))
        self._original_user_classes = self._user_classes.copy()

        assert len(user_classes) > 0
        assert len(set(self._user_classes)) == len(self._user_classes)

        self._initial_users_on_workers = {
            worker_node.id: {user_class.__name__: 0 for user_class in self._user_classes}
            for worker_node in worker_nodes
        }

        self._users_on_workers = self._fast_users_on_workers_copy(self._initial_users_on_workers)

        self._current_user_count: int | dict[str, int]

        # To keep track of how long it takes for each dispatch iteration to compute
        self._dispatch_iteration_durations: list[float] = []

        self._dispatch_in_progress: bool = False

        self._dispatcher_generator: DispatcherGenerator

        self._user_generator = self.create_user_generator()

        self._user_count_per_dispatch_iteration: int

        self._active_users: LengthOptimizedList[tuple[WorkerNode, str]] = LengthOptimizedList()

        self._spawn_rate: float

        self._wait_between_dispatch: float

        self._rebalance: bool = False

        self._no_user_to_spawn: bool = False

    @property
    def dispatch_iteration_durations(self) -> list[float]:
        return self._dispatch_iteration_durations

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

    @property
    def dispatch_in_progress(self):
        return self._dispatch_in_progress

    def get_current_user_count_total(self) -> int:
        return self._active_users.__optimized_length__

    def get_current_user_count(self, user_class_name: str) -> int:
        return sum([users_on_worker.get(user_class_name, 0) for users_on_worker in self._users_on_workers.values()])

    def has_reached_target_user_count(self) -> bool:
        return self.get_current_user_count_total() == self.get_target_user_count()

    def is_below_target_user_count(self) -> bool:
        return self.get_current_user_count_total() < self.get_target_user_count()

    def is_above_target_user_count(self) -> bool:
        return self.get_current_user_count_total() > self.get_target_user_count()

    @abstractmethod
    def get_target_user_count(self) -> int:
        ...

    @contextlib.contextmanager
    def _wait_between_dispatch_iteration_context(self) -> Generator[None, None, None]:
        t0_rel = time.perf_counter()

        # We don't use `try: ... finally: ...` because we don't want to sleep
        # if there's an exception within the context.
        yield

        delta = time.perf_counter() - t0_rel

        self._dispatch_iteration_durations.append(delta)

        # print("Dispatch cycle took {:.3f}ms".format(delta * 1000))

        if self.has_reached_target_user_count():
            # No sleep when this is the last dispatch iteration
            return

        sleep_duration = max(0.0, self._wait_between_dispatch - delta)
        gevent.sleep(sleep_duration)

    @staticmethod
    def infinite_cycle_gen(value_weights: list[tuple[type[User] | str, int]]) -> itertools.cycle[str | None]:
        if not value_weights:
            return itertools.cycle([None])

        # Normalize the weights so that the smallest weight will be equal to "target_min_weight".
        # The value "2" was experimentally determined because it gave a better distribution especially
        # when dealing with weights which are close to each others, e.g. 1.5, 2, 2.4, etc.
        target_min_weight = 2

        # 'Value' here means weight or fixed count
        try:
            min_value = min(weight for _, weight in value_weights if weight > 0)
        except ValueError:
            min_value = 0

        normalized_value_weights = [
            (
                getattr(value, "__name__", value),
                round(target_min_weight * weight / min_value) if min_value > 0 else 0,
            )
            for value, weight in value_weights
        ]
        generation_length_to_get_proper_distribution = sum(
            normalized_weight for _, normalized_weight in normalized_value_weights
        )
        gen = smooth(normalized_value_weights)

        # Instead of calling `gen()` for each user, we cycle through a generator of fixed-length
        # `generation_length_to_get_proper_distribution`. Doing so greatly improves performance because
        # we only ever need to call `gen()` a relatively small number of times. The length of this generator
        # is chosen as the sum of the normalized weights. So, for users A, B, C of weights 2, 5, 6, the length is
        # 2 + 5 + 6 = 13 which would yield the distribution `CBACBCBCBCABC` that gets repeated over and over
        # until the target user count is reached.
        return itertools.cycle(gen() for _ in range(generation_length_to_get_proper_distribution))

    @staticmethod
    def _fast_users_on_workers_copy(users_on_workers: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
        """deepcopy is too slow, so we use this custom copy function.

        The implementation was profiled and compared to other implementations such as dict-comprehensions
        and the one below is the most efficient.
        """
        # type is ignored due to: https://github.com/python/mypy/issues/1507
        return dict(zip(users_on_workers.keys(), map(dict.copy, users_on_workers.values())))  # type: ignore

    @final
    def dispatcher(self) -> DispatcherGenerator:
        self._dispatch_in_progress = True

        if self._rebalance:
            self._rebalance = False
            yield self._users_on_workers
            if self.has_reached_target_user_count():
                return

        if self.has_reached_target_user_count():
            yield self._initial_users_on_workers
            self._dispatch_in_progress = False
            return

        while self.is_below_target_user_count():
            with self._wait_between_dispatch_iteration_context():
                yield self.add_users_on_workers()
                if self._rebalance:
                    self._rebalance = False
                    yield self._users_on_workers
                if self._no_user_to_spawn:
                    self._no_user_to_spawn = False
                    break

        while self.is_above_target_user_count():
            with self._wait_between_dispatch_iteration_context():
                yield self.remove_users_from_workers()
                if self._rebalance:
                    self._rebalance = False
                    yield self._users_on_workers

        self._dispatch_in_progress = False

    def __next__(self) -> DistributedUsers:
        users_on_workers = next(self._dispatcher_generator)
        # TODO: Is this necessary to copy the users_on_workers if we know
        #       it won't be mutated by external code?
        return self._fast_users_on_workers_copy(users_on_workers)

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
        self.prepare_rebalance()

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
        self.prepare_rebalance()

    def prepare_rebalance(self) -> None:
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

        users_on_workers, user_gen, worker_gen, active_users = self.distribute_users(self._current_user_count)

        self._users_on_workers = users_on_workers
        self._active_users = active_users

        # It's important to reset the generators by using the ones from `_distribute_users`
        # so that the next iterations are smooth and continuous.
        self._user_generator = user_gen
        if worker_gen is not None:
            self._worker_node_generator = worker_gen

        self._rebalance = True

    @abstractmethod
    def new_dispatch(
        self,
        target_user_count: int | dict[str, int],
        spawn_rate: float,
        user_classes: list[type[User]] | None = None,
    ) -> None:
        ...

    @abstractmethod
    def add_users_on_workers(self) -> DistributedUsers:
        ...

    @abstractmethod
    def remove_users_from_workers(self) -> DistributedUsers:
        ...

    @abstractmethod
    def create_user_generator(self) -> UserGenerator:
        ...

    @overload
    def distribute_users(
        self, target_user_count: int
    ) -> tuple[DistributedUsers, UserGenerator, itertools.cycle, LengthOptimizedList[tuple[WorkerNode, str]]]:
        ...

    @overload
    def distribute_users(
        self, target_user_count: dict[str, int]
    ) -> tuple[DistributedUsers, UserGenerator, itertools.cycle | None, LengthOptimizedList[tuple[WorkerNode, str]]]:
        ...

    @abstractmethod
    def distribute_users(
        self, target_user_count: int | dict[str, int]
    ) -> tuple[DistributedUsers, UserGenerator, itertools.cycle | None, LengthOptimizedList[tuple[WorkerNode, str]]]:
        ...


class WeightedUsersDispatcher(UsersDispatcher):
    """
    Weight based iterator that dispatches users to the workers.

    Distribution of users are based on weights (`User.weight`), which will determine the amount of users of that type that will spawn.

    Its also possible to use `User.fixed_count` to spawn a fixed number of users of that type, in this case `User.weight` is ignored.
    """

    def __init__(self, worker_nodes: list[WorkerNode], user_classes: list[type[User]]):
        """
        :param worker_nodes: List of worker nodes
        :param user_classes: The user classes
        """
        super().__init__(worker_nodes, user_classes)

        self._target_user_count: int = None

        self._current_user_count: int = self.get_current_user_count_total()

        self._worker_node_generator = itertools.cycle(self._worker_nodes)

        self._try_dispatch_fixed = True

    def prepare_rebalance(self) -> None:
        self._try_dispatch_fixed = True
        super().prepare_rebalance()

    def get_target_user_count(self) -> int:
        return self._target_user_count

    def new_dispatch(
        self,
        target_user_count: int | dict[str, int],
        spawn_rate: float,
        user_classes: list[type[User]] | None = None,
    ) -> None:
        """
        Initialize a new dispatch cycle.

        :param target_user_count: The desired user count at the end of the dispatch cycle
        :param spawn_rate: The spawn rate
        :param user_classes: The user classes to be used for the new dispatch
        """
        if user_classes is not None and self._user_classes != sorted(user_classes, key=attrgetter("__name__")):
            self._user_classes = sorted(user_classes, key=attrgetter("__name__"))
            self._user_generator = self.create_user_generator()

        assert isinstance(target_user_count, int)

        self._target_user_count = target_user_count

        self._spawn_rate = spawn_rate

        self._user_count_per_dispatch_iteration = max(1, math.floor(self._spawn_rate))

        self._wait_between_dispatch = self._user_count_per_dispatch_iteration / self._spawn_rate

        self._initial_users_on_workers = self._users_on_workers

        self._users_on_workers = self._fast_users_on_workers_copy(self._initial_users_on_workers)

        self._current_user_count = self.get_current_user_count_total()

        self._dispatcher_generator = self.dispatcher()

        self._dispatch_iteration_durations.clear()

    def add_users_on_workers(self) -> DistributedUsers:
        """Add users on the workers until the target number of users is reached for the current dispatch iteration

        :return: The users that we want to run on the workers
        """
        current_user_count_target = min(
            self._current_user_count + self._user_count_per_dispatch_iteration, self._target_user_count
        )

        for user_class_name in self._user_generator:
            if not user_class_name:
                self._no_user_to_spawn = True
                break
            worker_node = next(self._worker_node_generator)
            self._users_on_workers[worker_node.id][user_class_name] += 1
            self._current_user_count += 1
            self._active_users.append((worker_node, user_class_name))
            if self._current_user_count >= current_user_count_target:
                break

        return self._users_on_workers

    def remove_users_from_workers(self) -> DistributedUsers:
        """Remove users from the workers until the target number of users is reached for the current dispatch iteration

        :return: The users that we want to run on the workers
        """
        current_user_count_target = max(
            self._current_user_count - self._user_count_per_dispatch_iteration, self._target_user_count
        )
        while True:
            try:
                worker_node, user_class_name = self._active_users.pop()
            except IndexError:
                return self._users_on_workers
            self._users_on_workers[worker_node.id][user_class_name] -= 1
            self._current_user_count -= 1
            self._try_dispatch_fixed = True
            if self._current_user_count == 0 or self._current_user_count <= current_user_count_target:
                return self._users_on_workers

    def distribute_users(
        self, target_user_count: int | dict[str, int]
    ) -> tuple[DistributedUsers, UserGenerator, itertools.cycle | None, LengthOptimizedList[tuple[WorkerNode, str]]]:
        """
        This function might take some time to complete if the `target_user_count` is a big number. A big number
        is typically > 50 000. However, this function is only called if a worker is added or removed while a test
        is running. Such a situation should be quite rare.
        """
        assert isinstance(target_user_count, int)

        user_gen = self.create_user_generator()

        worker_gen = itertools.cycle(self._worker_nodes)

        users_on_workers = {
            worker_node.id: {user_class.__name__: 0 for user_class in self._original_user_classes}
            for worker_node in self._worker_nodes
        }

        active_users: LengthOptimizedList[tuple[WorkerNode, str]] = LengthOptimizedList()

        user_count = 0
        while user_count < target_user_count:
            user_class_name = next(user_gen)
            if not user_class_name:
                break
            worker_node = next(worker_gen)
            users_on_workers[worker_node.id][user_class_name] += 1
            user_count += 1
            active_users.append((worker_node, user_class_name))

        return users_on_workers, user_gen, worker_gen, active_users

    def create_user_generator(self) -> UserGenerator:
        """
        This method generates users according to their weights using
        a smooth weighted round-robin algorithm implemented by https://github.com/linnik/roundrobin.

        For example, given users A, B with weights 5 and 1 respectively, this algorithm
        will yield AAABAAAAABAA. The smooth aspect of this algorithm is what makes it possible
        to keep the distribution during ramp-up and ramp-down. If we were to use a normal
        weighted round-robin algorithm, we'd get AAAAABAAAAAB which would make the distribution
        less accurate during ramp-up/down.
        """
        fixed_users = {u.__name__: u for u in self._user_classes if u.fixed_count}

        cycle_fixed_gen = self.infinite_cycle_gen([(u, u.fixed_count) for u in fixed_users.values()])
        cycle_weighted_gen = self.infinite_cycle_gen([(u, u.weight) for u in self._user_classes if not u.fixed_count])

        # Spawn users
        while True:
            if self._try_dispatch_fixed:
                self._try_dispatch_fixed = False
                current_fixed_users_count = {u: self.get_current_user_count(u) for u in fixed_users}
                spawned_classes: set[str] = set()
                while len(spawned_classes) != len(fixed_users):
                    user_class_name: str | None = next(cycle_fixed_gen)
                    if not user_class_name:
                        break

                    if current_fixed_users_count[user_class_name] < fixed_users[user_class_name].fixed_count:
                        current_fixed_users_count[user_class_name] += 1
                        yield user_class_name

                        # 'self._try_dispatch_fixed' was changed outhere,  we have to recalculate current count
                        if self._try_dispatch_fixed:
                            current_fixed_users_count = {u: self.get_current_user_count(u) for u in fixed_users}
                            spawned_classes.clear()
                            self._try_dispatch_fixed = False
                    else:
                        spawned_classes.add(user_class_name)

            yield next(cycle_weighted_gen)


class FixedUsersDispatcher(UsersDispatcher):
    """Fixed count (only) based iterator that dispatches users to the workers.

    Distribution is based on fixed count (`User.fixed_count`), it is also possible to group certain user types to the same
    workers by using `User.sticky_tag`. Available workers will then be assigned to one of the tags, and only spawn users with
    the same tag value.

    `User.weight`, if set on the user type, will be ignored with this dispatcher.
    """

    def __init__(self, worker_nodes: list[WorkerNode], user_classes: list[type[User]]) -> None:
        """
        :param worker_nodes: List of worker nodes
        :param user_classes: The user classes
        """
        super().__init__(worker_nodes, user_classes)

        self._users_to_sticky_tag = {
            user_class.__name__: user_class.sticky_tag or "__orphan__" for user_class in user_classes
        }

        self._user_class_name_to_type = {user_class.__name__: user_class for user_class in user_classes}

        self._workers_to_sticky_tag: dict[WorkerNode, str] = {}

        self._sticky_tag_to_workers: dict[str, itertools.cycle[WorkerNode]] = {}
        self.__sticky_tag_to_workers: dict[str, list[WorkerNode]] = {}

        # make sure there are not more sticky tags than worker nodes
        assert len(set(self._users_to_sticky_tag.values())) <= len(worker_nodes)

        self.__target_user_count_length__: int | None = None
        self.target_user_count = {user_class.__name__: user_class.fixed_count for user_class in self._user_classes}

        self._current_user_count: dict[str, int] = {user_class.__name__: 0 for user_class in self._user_classes}

    def get_target_user_count(self) -> int:
        if self.__target_user_count_length__ is None:
            self.__target_user_count_length__ = sum(self.target_user_count.values())

        return self.__target_user_count_length__

    @property
    def target_user_count(self) -> dict[str, int]:
        return self._target_user_count

    @target_user_count.setter
    def target_user_count(self, value: dict[str, int]) -> None:
        self.__target_user_count_length__ = None
        self._target_user_count = dict(sorted(value.items(), key=itemgetter(1), reverse=True))

    def prepare_rebalance(self) -> None:
        self._spread_sticky_tags_on_workers()
        super().prepare_rebalance()

    def new_dispatch(
        self,
        target_user_count: int | dict[str, int],
        spawn_rate: float,
        user_classes: list[type[User]] | None = None,
    ) -> None:
        """
        Initialize a new dispatch cycle.

        :param target_user_count: The desired user count, per user, at the end of the dispatch cycle
        :param spawn_rate: The spawn rate
        :param user_classes: The user classes to be used for the new dispatch
        """
        assert isinstance(target_user_count, dict)

        if user_classes is not None and self._user_classes != sorted(user_classes, key=attrgetter("__name__")):
            self._user_classes = sorted(user_classes, key=attrgetter("__name__"))

            # map original user classes (supplied when users dispatcher was created), with additional new ones (might be duplicates)
            self._users_to_sticky_tag = {
                user_class.__name__: user_class.sticky_tag or "__orphan__"
                for user_class in self._original_user_classes + user_classes
            }

            self._user_class_name_to_type = {
                user_class.__name__: user_class for user_class in self._original_user_classes + user_classes
            }

            user_class_names = [user_class.__name__ for user_class in user_classes]

            # only merge target user count for classes that has been specified in user classes
            target_user_count = {
                user_class_name: count
                for user_class_name, count in target_user_count.items()
                if user_class_name in user_class_names
            }

        if target_user_count != {}:
            self.target_user_count = {**self.target_user_count, **target_user_count}

        self._spawn_rate = spawn_rate

        self._user_count_per_dispatch_iteration = max(1, math.floor(self._spawn_rate))

        self._wait_between_dispatch = self._user_count_per_dispatch_iteration / self._spawn_rate

        self._spread_sticky_tags_on_workers()

        self._initial_users_on_workers = self._users_on_workers

        self._users_on_workers = self._fast_users_on_workers_copy(self._initial_users_on_workers)

        self._dispatcher_generator = self.dispatcher()

        self._dispatch_iteration_durations.clear()

        self._user_generator = self.create_user_generator()

    def add_users_on_workers(self) -> DistributedUsers:
        """Add users on the workers until the target number of users is reached for the current dispatch iteration

        :return: The users that we want to run on the workers
        """
        current_user_count_actual = self._active_users.__optimized_length__
        current_user_count_target = min(
            current_user_count_actual + self._user_count_per_dispatch_iteration, self.get_target_user_count()
        )

        current_user_count: dict[str, int] = {}
        for user_counts in self._users_on_workers.values():
            for user_class_name, count in user_counts.items():
                current_user_count.update({user_class_name: current_user_count.get(user_class_name, 0) + count})

        for user_class_name in self._user_generator:
            if not user_class_name:
                self._no_user_to_spawn = True
                break

            if current_user_count[user_class_name] + 1 > self.target_user_count[user_class_name]:
                continue

            sticky_tag = self._users_to_sticky_tag[user_class_name]
            worker_node = next(self._sticky_tag_to_workers[sticky_tag])
            self._users_on_workers[worker_node.id][user_class_name] += 1
            current_user_count_actual += 1
            current_user_count[user_class_name] += 1
            self._active_users.append((worker_node, user_class_name))

            if current_user_count_actual >= current_user_count_target:
                self._current_user_count = current_user_count
                break

        return self._users_on_workers

    def remove_users_from_workers(self) -> DistributedUsers:
        """Remove users from the workers until the target number of users is reached for the current dispatch iteration

        :return: The users that we want to run on the workers
        """
        current_user_count_actual = self._active_users.__optimized_length__
        current_user_count_target = max(
            current_user_count_actual - self._user_count_per_dispatch_iteration, self.get_target_user_count()
        )

        while True:
            try:
                worker_node, user = self._active_users.pop()
            except IndexError:
                return self._users_on_workers

            self._users_on_workers[worker_node.id][user] -= 1
            current_user_count_actual -= 1
            if current_user_count_actual == 0 or current_user_count_actual <= current_user_count_target:
                self._current_user_count.clear()
                for user_counts in self._users_on_workers.values():
                    for user_class_name, count in user_counts.items():
                        self._current_user_count.update(
                            {user_class_name: self._current_user_count.get(user_class_name, 0) + count}
                        )
                return self._users_on_workers

    def _spread_sticky_tags_on_workers(self) -> None:
        sticky_tag_user_count: dict[str, int] = {}

        # summarize target user count per sticky tag
        for user_class_name, sticky_tag in self._users_to_sticky_tag.items():
            user_count = self.target_user_count.get(user_class_name, None)
            if user_count is None:
                continue

            user_count = sticky_tag_user_count.get(sticky_tag, 0) + user_count
            sticky_tag_user_count.update({sticky_tag: user_count})

        logger.debug("user count per sticky tag: %r", sticky_tag_user_count)

        worker_node_count = len(self._worker_nodes)
        # sort sticky tags based on number of users (more user types should have more workers)
        sticky_tags: dict[str, int] = dict(sorted(sticky_tag_user_count.items(), key=itemgetter(1), reverse=True))
        sticky_tag_count = len(sticky_tag_user_count)

        # not enough sticky tags per worker, so cycle sticky tags so all workers gets a tag
        sticky_tags_f: Iterator[str]
        if worker_node_count > sticky_tag_count:
            # make sure each tag get at least one worker, then spread the remaining based on how many users that sticky tag has been assigned
            sticky_tags_f = itertools.chain(
                sticky_tags.keys(),
                self.infinite_cycle_gen([(sticky_tag, user_count) for sticky_tag, user_count in sticky_tags.items()]),
            )
        else:
            sticky_tags_f = iter(sticky_tags.keys())

        # map worker to sticky tag
        self._workers_to_sticky_tag.clear()
        for worker, sticky_tag in zip(self._worker_nodes, sticky_tags_f):
            self._workers_to_sticky_tag.update({worker: sticky_tag})

        # map sticky tag to workers
        orig__sticky_tag_to_workers = self.__sticky_tag_to_workers.copy()
        self.__sticky_tag_to_workers.clear()
        for worker, sticky_tag in self._workers_to_sticky_tag.items():
            self.__sticky_tag_to_workers.update(
                {sticky_tag: self.__sticky_tag_to_workers.get(sticky_tag, []) + [worker]}
            )

        logger.debug(
            "workers per sticky tag: %r",
            {
                sticky_tag: [worker.id for worker in workers]
                for sticky_tag, workers in self.__sticky_tag_to_workers.items()
            },
        )

        # check if workers has changed since last time
        # do not reset worker cycles if only target user count has changed
        changes_for_sticky_tag: dict[str, list[WorkerNode] | None] = {}
        for sticky_tag in self.__sticky_tag_to_workers:
            workers = self.__sticky_tag_to_workers.get(sticky_tag, None)
            if workers is not None and orig__sticky_tag_to_workers.get(sticky_tag, []) != workers:
                changes_for_sticky_tag.update({sticky_tag: workers})
            elif workers is None:
                changes_for_sticky_tag.update({sticky_tag: None})
            else:  # nothing has changed, keep the worker cycle as it was
                pass

        # apply changes
        for sticky_tag, change in changes_for_sticky_tag.items():
            if change is not None:
                self._sticky_tag_to_workers.update({sticky_tag: itertools.cycle(change)})
            else:
                del self._sticky_tag_to_workers[sticky_tag]

    def create_user_generator(self) -> UserGenerator:
        user_cycle: list[tuple[type[User] | str, int]] = [
            (self._user_class_name_to_type.get(user_class_name), fixed_count)
            for user_class_name, fixed_count in self.target_user_count.items()
        ]
        user_generator: itertools.cycle[str | None] = self.infinite_cycle_gen(user_cycle)

        while user_class_name := next(user_generator):
            if not user_class_name:
                break

            yield user_class_name

    def distribute_users(
        self, target_user_count: int | dict[str, int]
    ) -> tuple[DistributedUsers, UserGenerator, None, LengthOptimizedList[tuple[WorkerNode, str]]]:
        """Distribute users on available workers, and continue user cycle from there."""

        assert isinstance(target_user_count, dict)

        # used target as setup based on user class values, without changing the original value
        if target_user_count == {}:
            target_user_count = {**self.target_user_count}

        self._spread_sticky_tags_on_workers()

        user_gen = self.create_user_generator()

        users_on_workers = {
            worker_node.id: {user_class.__name__: 0 for user_class in self._original_user_classes}
            for worker_node in self._worker_nodes
        }

        active_users: LengthOptimizedList[tuple[WorkerNode, str]] = LengthOptimizedList()

        user_count_target = sum(target_user_count.values())
        current_user_count: dict[str, int] = {}
        for user_counts in users_on_workers.values():
            for user_class_name, count in user_counts.items():
                current_user_count.update({user_class_name: current_user_count.get(user_class_name, 0) + count})

        user_count_total = 0

        for user_class_name in user_gen:
            if not user_class_name:
                break

            if current_user_count[user_class_name] + 1 > target_user_count[user_class_name]:
                continue

            sticky_tag = self._users_to_sticky_tag[user_class_name]
            worker_node = next(self._sticky_tag_to_workers[sticky_tag])
            users_on_workers[worker_node.id][user_class_name] += 1
            user_count_total += 1
            current_user_count[user_class_name] += 1
            active_users.append((worker_node, user_class_name))

            if user_count_total >= user_count_target:
                self._current_user_count = current_user_count
                break

        return users_on_workers, user_gen, None, active_users
