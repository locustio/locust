import unittest

from locust import User


class TestUserClass(unittest.TestCase):
    class MyClassScopedUser(User):
        pass

    def test_fullname_module_scoped(self):
        self.assertEqual(MyModuleScopedUser.fullname(), "locust.test.test_users.MyModuleScopedUser")

    def test_fullname_class_scoped(self):
        self.assertEqual(self.MyClassScopedUser.fullname(), "locust.test.test_users.TestUserClass.MyClassScopedUser")

    def test_fullname_function_scoped(self):
        class MyFunctionScopedUser(User):
            pass

        self.assertEqual(
            MyFunctionScopedUser.fullname(),
            "locust.test.test_users.TestUserClass.test_fullname_function_scoped.MyFunctionScopedUser",
        )


class MyModuleScopedUser(User):
    pass
