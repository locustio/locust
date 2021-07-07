import time
import unittest

from locust import User
from locust.distribution import weight_users


class TestDistribution(unittest.TestCase):
    def test_distribution_no_user_classes(self):
        user_classes_count = weight_users(user_classes=[], user_count=0)
        self.assertDictEqual(user_classes_count, {})

        user_classes_count = weight_users(user_classes=[], user_count=1)
        self.assertDictEqual(user_classes_count, {})

    def test_distribution_equal_weights_and_fewer_amount_than_user_classes(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=0)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 0, "User3": 0})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=1)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 0, "User3": 0})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=2)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 0})

    def test_distribution_equal_weights(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=3)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 1})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=4)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 1, "User3": 1})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=5)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 2, "User3": 2})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=6)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 2, "User3": 2})

    def test_distribution_unequal_and_unique_weights_and_fewer_amount_than_user_classes(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 2

        class User3(User):
            weight = 3

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=0)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 0, "User3": 0})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=1)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 0, "User3": 1})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=2)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 1, "User3": 1})

    def test_distribution_unequal_and_unique_weights(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 2

        class User3(User):
            weight = 3

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=3)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 1})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=4)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 2})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=5)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 2, "User3": 2})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=6)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 2, "User3": 3})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=10)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 3, "User3": 5})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=11)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 4, "User3": 5})

    def test_distribution_unequal_and_non_unique_weights_and_fewer_amount_than_user_classes(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 2

        class User3(User):
            weight = 2

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=0)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 0, "User3": 0})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=1)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 1, "User3": 0})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=2)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 1, "User3": 1})

    def test_distribution_unequal_and_non_unique_weights(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 2

        class User3(User):
            weight = 2

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=3)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 1})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=4)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 2})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=5)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 2, "User3": 2})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=6)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 3, "User3": 2})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=10)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 4, "User3": 4})

        user_classes_count = weight_users(user_classes=[User1, User2, User3], user_count=11)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 5, "User3": 4})

    def test_distribution_large_number_of_users(self):
        class User1(User):
            weight = 5

        class User2(User):
            weight = 55

        class User3(User):
            weight = 37

        class User4(User):
            weight = 2

        class User5(User):
            weight = 97

        class User6(User):
            weight = 41

        class User7(User):
            weight = 33

        class User8(User):
            weight = 19

        class User9(User):
            weight = 19

        class User10(User):
            weight = 34

        class User11(User):
            weight = 78

        class User12(User):
            weight = 76

        class User13(User):
            weight = 28

        class User14(User):
            weight = 62

        class User15(User):
            weight = 69

        for user_count in range(1044523783783, 1044523783783 + 1000):
            ts = time.perf_counter()
            user_classes_count = weight_users(
                user_classes=[
                    User1,
                    User2,
                    User3,
                    User4,
                    User5,
                    User6,
                    User7,
                    User8,
                    User9,
                    User10,
                    User11,
                    User12,
                    User13,
                    User14,
                    User15,
                ],
                user_count=user_count,
            )
            delta_ms = 1e3 * (time.perf_counter() - ts)
            self.assertEqual(sum(user_classes_count.values()), user_count)
            self.assertLessEqual(delta_ms, 100)
