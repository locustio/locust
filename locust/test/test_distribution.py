import time
import unittest

from locust import User
from locust.distribution import distribute_users


class TestDistribution(unittest.TestCase):
    def test_distribution_no_user_classes(self):
        user_classes_count = distribute_users(user_classes=[], user_count=0)
        self.assertDictEqual(user_classes_count, {})

        user_classes_count = distribute_users(user_classes=[], user_count=1)
        self.assertDictEqual(user_classes_count, {})

    def test_distribution_equal_weights_and_fewer_amount_than_user_classes(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=0)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 0, "User3": 0})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=1)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 0, "User3": 0})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=2)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 0})

    def test_distribution_equal_weights(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 1

        class User3(User):
            weight = 1

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=3)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 1})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=4)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 1, "User3": 1})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=5)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 2, "User3": 2})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=6)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 2, "User3": 2})

    def test_distribution_unequal_and_unique_weights_and_fewer_amount_than_user_classes(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 2

        class User3(User):
            weight = 3

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=0)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 0, "User3": 0})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=1)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 0, "User3": 1})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=2)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 1, "User3": 1})

    def test_distribution_unequal_and_unique_weights(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 2

        class User3(User):
            weight = 3

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=3)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 1})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=4)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 2})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=5)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 2, "User3": 2})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=6)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 2, "User3": 3})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=10)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 3, "User3": 5})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=11)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 4, "User3": 5})

    def test_distribution_unequal_and_non_unique_weights_and_fewer_amount_than_user_classes(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 2

        class User3(User):
            weight = 2

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=0)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 0, "User3": 0})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=1)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 1, "User3": 0})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=2)
        self.assertDictEqual(user_classes_count, {"User1": 0, "User2": 1, "User3": 1})

    def test_distribution_unequal_and_non_unique_weights(self):
        class User1(User):
            weight = 1

        class User2(User):
            weight = 2

        class User3(User):
            weight = 2

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=3)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 1})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=4)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 1, "User3": 2})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=5)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 2, "User3": 2})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=6)
        self.assertDictEqual(user_classes_count, {"User1": 1, "User2": 3, "User3": 2})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=10)
        self.assertDictEqual(user_classes_count, {"User1": 2, "User2": 4, "User3": 4})

        user_classes_count = distribute_users(user_classes=[User1, User2, User3], user_count=11)
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
            user_classes_count = distribute_users(
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

    def test_distribution_large_number_of_user_classes(self):
        class User01(User):
            weight = 5

        class User02(User):
            weight = 55

        class User03(User):
            weight = 37

        class User04(User):
            weight = 2

        class User05(User):
            weight = 97

        class User06(User):
            weight = 41

        class User07(User):
            weight = 33

        class User08(User):
            weight = 19

        class User09(User):
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

        class User16(User):
            weight = 5

        class User17(User):
            weight = 55

        class User18(User):
            weight = 37

        class User19(User):
            weight = 2

        class User20(User):
            weight = 97

        class User21(User):
            weight = 41

        class User22(User):
            weight = 33

        class User23(User):
            weight = 19

        class User24(User):
            weight = 19

        class User25(User):
            weight = 34

        class User26(User):
            weight = 78

        class User27(User):
            weight = 76

        class User28(User):
            weight = 28

        class User29(User):
            weight = 62

        class User30(User):
            weight = 69

        class User31(User):
            weight = 41

        class User32(User):
            weight = 33

        class User33(User):
            weight = 19

        class User34(User):
            weight = 19

        class User35(User):
            weight = 34

        class User36(User):
            weight = 78

        class User37(User):
            weight = 76

        class User38(User):
            weight = 28

        class User39(User):
            weight = 62

        class User40(User):
            weight = 69

        class User41(User):
            weight = 41

        class User42(User):
            weight = 33

        class User43(User):
            weight = 19

        class User44(User):
            weight = 19

        class User45(User):
            weight = 34

        class User46(User):
            weight = 78

        class User47(User):
            weight = 76

        class User48(User):
            weight = 28

        class User49(User):
            weight = 62

        class User50(User):
            weight = 69

        # for user_count in range(100_000 - 99_999, 100_000 + 500_000 + 1):
        # for user_count in range(100_000 - 99_999, 100_000 + 500_000 + 1):
        user_count = 100_000
        user_classes_count = distribute_users(
            user_classes=[
                User01,
                User02,
                User03,
                User04,
                User05,
                User06,
                User07,
                User08,
                User09,
                User10,
                User11,
                User12,
                User13,
                User14,
                User15,
                User16,
                User17,
                User18,
                User19,
                User20,
                User21,
                User22,
                User23,
                User24,
                User25,
                User26,
                User27,
                User28,
                User29,
                User30,
                User31,
                User32,
                User33,
                User34,
                User35,
                User36,
                User37,
                User38,
                User39,
                User40,
                User41,
                User42,
                User43,
                User44,
                User45,
                User46,
                User47,
                User48,
                User49,
                User50,
            ],
            user_count=user_count,
        )

        self.assertEqual(sum(user_classes_count.values()), user_count)
