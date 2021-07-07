import contextlib
import functools
import itertools
import json
import math
import tempfile
import time
from collections.abc import Iterator
from copy import deepcopy
from operator import add, attrgetter, itemgetter, lt, methodcaller, ne, sub
from typing import Dict, Generator, List, TYPE_CHECKING, Tuple, Type

import gevent
import roundrobin

from locust import User
from locust.distribution import distribute_users

if TYPE_CHECKING:
    from locust.runners import WorkerNode


# To profile line-by-line, uncomment the code below (i.e. `import line_profiler ...`) and
# place `#@profile` on the functions/methods you wish to profile. Then, in the unit test you are
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

    def __init__(
        self,
        worker_nodes: "List[WorkerNode]",
        user_classes: List[Type[User]],
        previous_target_user_count: int,
        target_user_count: int,
        spawn_rate: float,
    ):
        """
        :param worker_nodes: List of worker nodes
        :param user_classes: The user classes
        :param previous_target_user_count: The desired user count at the end of the previous dispatch cycle
        :param target_user_count: The desired user count at the end of the dispatch cycle
        :param spawn_rate: The spawn rate
        """
        # NOTE: We use "sorted" in some places in this module. It is done to ensure repeatable behaviour.
        #       This is especially important when iterating over a dictionary which, prior to py3.7, was
        #       completely unordered. For >=Py3.7, a dictionary keeps the insertion order. Even then,
        #       it is safer to sort the keys when repeatable behaviour is required.
        self._worker_nodes = sorted(worker_nodes, key=lambda w: w.id)

        self._worker_nodes_id: List[str] = [w.id for w in self._worker_nodes]  # TODO: Needed?

        self._worker_count = len(self._worker_nodes)

        self._user_classes = sorted(user_classes, key=attrgetter("__name__"))

        self._previous_target_user_count = previous_target_user_count

        self._target_user_count = target_user_count

        self._spawn_rate = spawn_rate

        self._initial_users_on_workers = {
            worker_node.id: {
                user_class.__name__: worker_node.user_classes_count.get(user_class.__name__, 0)
                for user_class in self._user_classes
            }
            for worker_node in worker_nodes
        }

        self._users_on_workers = deepcopy(self._initial_users_on_workers)

        self._user_count_per_dispatch_iteration = max(1, math.floor(self._spawn_rate))

        self._wait_between_dispatch = self._user_count_per_dispatch_iteration / self._spawn_rate

        self._dispatcher_generator = self._dispatcher()

        self._user_gen_generator = self._user_gen()

        self._user_gen2_generator = self._user_gen2()

        self._worker_names_generator = itertools.cycle(self._worker_nodes_id)

        self._iteration = 0  # TODO: Needed?

        self._current_user_count = sum(map(sum, map(dict.values, self._users_on_workers.values())))

        self._active_users = []

        self._stopped_users = []

        #
        user_classes_count = distribute_users(self._user_classes, self._target_user_count)
        distributed_users = []
        for user_class in itertools.cycle(self._user_classes):
            if sum(user_classes_count.values()) == 0:
                break
            if user_classes_count[user_class.__name__] > 0:
                distributed_users.append(user_class.__name__)
                user_classes_count[user_class.__name__] -= 1

        # self._distributed_users_iterator = itertools.cycle(distributed_users)
        self._distributed_users_iterator = roundrobin.smooth(
            [(user_class.__name__, user_class.weight) for user_class in self._user_classes]
        )

        self._dispatch_iteration_durations = []

    @property
    def dispatch_iteration_durations(self) -> List[float]:
        return self._dispatch_iteration_durations

    def __next__(self) -> Dict[str, Dict[str, int]]:
        return next(self._dispatcher_generator)

    def _dispatcher(self) -> Generator[Dict[str, Dict[str, int]], None, None]:
        """Main iterator logic for dispatching users during this dispatch cycle"""
        # TODO: Ensure initial users on worker is ok. If not, send a single dispatch
        #       to first set the workers with the adequate users. After having done that,
        #       we need to update `self._users_on_workers` and `self._current_user_count`

        if self._current_user_count < self._target_user_count:
            while self._current_user_count < self._target_user_count:
                with self._wait_between_dispatch_iteration_context():
                    yield self._ramp_up()
                    self._iteration += 1

        elif self._current_user_count > self._target_user_count:
            while self._current_user_count > self._target_user_count:
                with self._wait_between_dispatch_iteration_context():
                    yield self._ramp_down()
                    self._iteration += 1

        else:
            yield self._initial_users_on_workers
            self._iteration += 1

    @contextlib.contextmanager
    def _wait_between_dispatch_iteration_context(self) -> None:
        t0_rel = time.perf_counter()

        # We don't use `try: ... finally: ...` because we don't want to sleep
        # if there's an exception within the context.
        yield

        delta = time.perf_counter() - t0_rel

        self._dispatch_iteration_durations.append(delta)

        print("Dispatch cycle took {:.3f}ms".format(delta * 1000))

        if self._current_user_count == self._target_user_count:
            # No sleep when this is the last dispatch iteration
            return

        sleep_duration = max(0.0, self._wait_between_dispatch - delta)
        gevent.sleep(sleep_duration)

    def _ramp_up(self) -> Dict[str, Dict[str, int]]:
        initial_user_count = self._current_user_count
        for user in self._user_gen2_generator:
            worker_name = next(self._worker_names_generator)
            self._users_on_workers[worker_name][user] += 1
            self._current_user_count += 1
            if self._current_user_count >= min(
                initial_user_count + self._user_count_per_dispatch_iteration, self._target_user_count
            ):
                return deepcopy(self._users_on_workers)

        # while True:
        #     # Respawn stopped users if any exist
        #     while self._stopped_users:
        #         worker_name, user = self._stopped_users.pop()
        #         self._active_users.append([worker_name, user])
        #         self._users_on_workers[worker_name][user] += 1
        #         self._current_user_count += 1
        #         if self._current_user_count >= self._target_user_count:
        #             assert False
        #             # return
        #
        #     for users in self._user_gen_generator:
        #         for user in users:
        #             users_on_selected_worker = None
        #             for worker_name, users_on_worker in self._users_on_workers.items():
        #                 # The condition on the right means the previous selected worker has
        #                 # more users of class `user` than the current `worker_name`. Thus,
        #                 # we should assign the `user` to the curent `worker_name`.
        #                 if (
        #                     users_on_selected_worker is None
        #                     or self._users_on_workers[worker_name][user] < users_on_selected_worker[user]
        #                 ):
        #                     users_on_selected_worker = users_on_worker
        #                     selected_worker_name = worker_name
        #             self._active_users.append([selected_worker_name, user])
        #             self._users_on_workers[selected_worker_name][user] += 1
        #             self._current_user_count += 1
        #             if self._current_user_count >= initial_user_count + self._user_count_per_dispatch_iteration:
        #                 return deepcopy(self._users_on_workers)

    def _user_gen2(self) -> Generator[str, None, None]:
        gen = roundrobin.smooth([(user_class.__name__, user_class.weight) for user_class in self._user_classes])
        while True:
            yield gen()

    def _ramp_down(self) -> Dict[str, Dict[str, int]]:
        initial_user_count = self._current_user_count
        for user in self._user_gen2_generator:
            while True:
                worker_name = next(self._worker_names_generator)
                if self._users_on_workers[worker_name][user] == 0:
                    continue
                self._users_on_workers[worker_name][user] -= 1
                self._current_user_count -= 1
                if (
                    self._current_user_count == 0
                    or self._current_user_count <= initial_user_count - self._user_count_per_dispatch_iteration
                ):
                    return deepcopy(self._users_on_workers)
                break

        # while self._current_user_count > initial_user_count - self._user_count_per_dispatch_iteration:
        #     worker_name, user = self._active_users.pop()
        #     self._stopped_users.append([worker_name, user])
        #     self._users_on_workers[worker_name][user] -= 1
        #     self._current_user_count -= 1
        # return deepcopy(self._users_on_workers)

    def _user_gen(self):
        # ensure_all_users_get_picked = []
        # other_users = []
        # for u in self._user_classes:
        #     for i in range(u.weight):
        #         if i == 0:
        #             ensure_all_users_get_picked.append(u.__name__)
        #         else:
        #             other_users.append(u.__name__)
        #
        # # other_users needs to be shuffled better. should be fairly easy,
        # # but I couldn't immediately find a good solution and I want to get stuck in the weeds...
        # weighted_users = ensure_all_users_get_picked + other_users

        user_classes_count = distribute_users(self._user_classes, self._target_user_count)
        distributed_users = []
        for user_class in itertools.cycle(self._user_classes):
            if sum(user_classes_count.values()) == 0:
                break
            if user_classes_count[user_class.__name__] > 0:
                distributed_users.append(user_class.__name__)
                user_classes_count[user_class.__name__] -= 1

        distributed_users_iterator = itertools.cycle(distributed_users)
        while True:
            yield next(self._batch_iter(self._user_count_per_dispatch_iteration, distributed_users_iterator))
            # yield next(self._batch_iter(self._worker_count, distributed_users_iterator))

    def _batch_iter(self, batch_size, iterator):
        yield [next(iterator) for _ in range(batch_size)]
