import contextlib
import itertools
import math
import time
from collections.abc import Iterator
from copy import deepcopy
from operator import attrgetter
from typing import Dict, Generator, List, TYPE_CHECKING, Type

import gevent
import roundrobin

from locust import User

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
        # NOTE: We use "sorted" to ensure repeatable behaviour.
        #       This is especially important when iterating over a dictionary which, prior to py3.7, was
        #       completely unordered. For >=Py3.7, a dictionary keeps the insertion order. Even then,
        #       it is safer to sort the keys when repeatable behaviour is required.
        self._worker_nodes = sorted(worker_nodes, key=lambda w: w.id)

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

        self._worker_node_id_generator = itertools.cycle(map(attrgetter("id"), self._worker_nodes))

        self._current_user_count = sum(map(sum, map(dict.values, self._users_on_workers.values())))

        # To keep track of how long it takes for each dispatch iteration to compute
        self._dispatch_iteration_durations = []

    @property
    def dispatch_iteration_durations(self) -> List[float]:
        return self._dispatch_iteration_durations

    def __next__(self) -> Dict[str, Dict[str, int]]:
        return next(self._dispatcher_generator)

    def _dispatcher(self) -> Generator[Dict[str, Dict[str, int]], None, None]:
        # TODO: Ensure initial users on workers are ok. If not, send a single dispatch
        #       to set the workers with the adequate users. After having done that,
        #       we need to update `self._users_on_workers` and `self._current_user_count`.

        if self._current_user_count == self._target_user_count:
            yield self._initial_users_on_workers
            return

        while self._current_user_count < self._target_user_count:
            with self._wait_between_dispatch_iteration_context():
                yield self._ramp_up()

        while self._current_user_count > self._target_user_count:
            with self._wait_between_dispatch_iteration_context():
                yield self._ramp_down()

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

    def _ramp_up(self) -> Dict[str, Dict[str, int]]:
        initial_user_count = self._current_user_count
        for user in self._user_gen_generator:
            worker_name = next(self._worker_node_id_generator)
            self._users_on_workers[worker_name][user] += 1
            self._current_user_count += 1
            if self._current_user_count >= min(
                initial_user_count + self._user_count_per_dispatch_iteration, self._target_user_count
            ):
                return deepcopy(self._users_on_workers)

    def _ramp_down(self) -> Dict[str, Dict[str, int]]:
        initial_user_count = self._current_user_count
        for user in self._user_gen_generator:
            while True:
                worker_name = next(self._worker_node_id_generator)
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

    def _user_gen(self) -> Generator[str, None, None]:
        gen = roundrobin.smooth([(user_class.__name__, user_class.weight) for user_class in self._user_classes])
        while True:
            yield gen()
