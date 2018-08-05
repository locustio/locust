# -*- coding: utf-8 -*-
import math

class _LocustInfo(object):
    def __init__(self, locust, ratio):
        self.locust = locust
        self.ratio = ratio
        self.count = 0

    def lower_count(self, total_count):
        return int(math.floor(self.ratio * total_count))

    def upper_count(self, total_count):
        return int(math.ceil(self.ratio * total_count))

    def miscount(self, total_count):
        return total_count * self.ratio - self.count

class LocustsCollection(object):
    """
    LocustCollection maintain accurate distribution of locust classes among available locust executors according to the locust weight
    Algorithm maintain next invariant:
        1. Let p_i = weight_i / sum(weights)
        2. Let count_i = p_i * locusts_count
        3. Then, for every locust class there is at most two interger points near to count_i: floor(count_i) and ceil(count_i)
        4. At every moment each locust class executed by floor(count_i) or ceil(count_i) locust executors
    """
    def __init__(self, locust_classes):
        total_weight = sum(locust.weight for locust in locust_classes)
        self._locusts = [_LocustInfo(locust, locust.weight / float(total_weight)) 
                         for locust in locust_classes]
        self.size = 0

    @property
    def classes(self):
        return list(map(lambda l: l.locust, self._locusts))

    def spawn_locusts(self, spawn_count):
        spawned = []
        new_size = self.size + spawn_count
        for locust in self._locusts:
            adjust_spawn_count = max(0, locust.lower_count(new_size) - locust.count)
            spawned.extend(self._change_locust_count(locust, adjust_spawn_count))
        return spawned + self._make_final_size_adjusment(new_size)

    def kill_locusts(self, kill_count):
        killed = []
        new_size = self.size - kill_count
        for locust in self._locusts:
            adjust_kill_count = max(0, locust.count - locust.upper_count(new_size))
            killed.extend(self._change_locust_count(locust, -adjust_kill_count))
        return killed + self._make_final_size_adjusment(new_size)

    def _change_locust_count(self, locust, count):
        self.size += count
        locust.count += count
        return [locust.locust for _ in range(abs(count))]

    def _make_final_size_adjusment(self, new_size):
        adjusted = []
        adjusted_size = abs(self.size - new_size)
        add_locusts = self.size < new_size
        sorted_locusts = sorted(self._locusts, key=lambda l: l.miscount(new_size), reverse=add_locusts)
        for locust in list(sorted_locusts)[:adjusted_size]:
            adjusted.extend(self._change_locust_count(locust, 1 if add_locusts else -1))
        return adjusted
