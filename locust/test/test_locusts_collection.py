import unittest

from locust.locusts_collection import LocustsCollection

class MockLocust(object):
    def __init__(self, weight):
        self.weight = weight
    def __str__(self):
        return 'locust(w={})'.format(self.weight)
    def __repr__(self):
        return 'MockLocust({})'.format(self.weight)
class TestLocustsCollection(unittest.TestCase):
    def test_spawn_locusts_1_class(self):
        locust = MockLocust(1)
        collection = LocustsCollection([locust])
        spawned = collection.spawn_locusts(4)
        self.assertItemsEqual(spawned, [locust, locust, locust, locust])
        
    def test_spawn_locusts_3_classes(self):
        l1, l2, l3 = MockLocust(1), MockLocust(1), MockLocust(1)
        collection = LocustsCollection([l1, l2, l3])
        s1 = collection.spawn_locusts(1)
        s2 = collection.spawn_locusts(1)
        s3 = collection.spawn_locusts(1)
        self.assertItemsEqual(s1 + s2 + s3, [l1, l2, l3])

    def test_kill_locusts_1_class(self):
        locust = MockLocust(1)
        collection = LocustsCollection([locust])
        spawned = collection.spawn_locusts(4)
        killed1 = collection.kill_locusts(3)
        killed2 = collection.kill_locusts(1)
        self.assertItemsEqual(killed1, [locust, locust, locust])
        self.assertItemsEqual(killed2, [locust])

    def test_kill_locusts_3_classes(self):
        l1, l2, l3 = MockLocust(1), MockLocust(1), MockLocust(1)
        collection = LocustsCollection([l1, l2, l3])
        spawned = collection.spawn_locusts(3)
        k1 = collection.kill_locusts(1)
        k2 = collection.kill_locusts(1)
        k3 = collection.kill_locusts(1)
        self.assertItemsEqual(k1 + k2 + k3, [l1, l2, l3])

    def test_spawn_complex_weight_distribution(self):
        l1, l3, l5 = MockLocust(1), MockLocust(3), MockLocust(5)
        collection = LocustsCollection([l1, l3, l5])
        s1 = collection.spawn_locusts(1)
        s2 = collection.spawn_locusts(3)
        s3 = collection.spawn_locusts(5)
        self.assertItemsEqual(s1, [l5])
        self.assertItemsEqual(s2, [l1, l3, l5])
        self.assertItemsEqual(s3, [l3, l3, l5, l5, l5])

    def test_kill_complex_weight_distribution(self):
        l1, l3, l5 = MockLocust(1), MockLocust(3), MockLocust(5)
        collection = LocustsCollection([l1, l3, l5])
        spawned = collection.spawn_locusts(9)
        k1 = collection.kill_locusts(1)
        k2 = collection.kill_locusts(3)
        k3 = collection.kill_locusts(5)
        self.assertItemsEqual(k1, [l5])
        self.assertItemsEqual(k2, [l1, l3, l5])
        self.assertItemsEqual(k3, [l3, l3, l5, l5, l5])

    def test_spawn_and_kill(self):
        l1, l3, l5 = MockLocust(1), MockLocust(3), MockLocust(5)
        collection = LocustsCollection([l1, l3, l5])
        s1 = collection.spawn_locusts(4)
        k1 = collection.kill_locusts(1)
        k2 = collection.kill_locusts(2)
        s2 = collection.spawn_locusts(3)
        self.assertItemsEqual(s1, [l1, l3, l5, l5])
        self.assertItemsEqual(k1, [l1])
        self.assertItemsEqual(k2, [l3, l5])
        self.assertItemsEqual(s2, [l1, l3, l5])

    def test_spawn_many_locusts(self):
        l1, l3, l5 = MockLocust(2), MockLocust(3), MockLocust(5)
        collection = LocustsCollection([l1, l3, l5])
        spawned = collection.spawn_locusts(100)
        self.assertItemsEqual(spawned, [l1 for _ in range(20)] + 
                                       [l3 for _ in range(30)] + 
                                       [l5 for _ in range(50)])
