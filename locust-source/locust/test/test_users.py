import unittest

from urllib3 import PoolManager

from locust import User, HttpUser
from locust.test.testcases import WebserverTestCase


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


class TestHttpUserWithWebserver(WebserverTestCase):
    def test_shared_pool_manager(self):
        shared_pool_manager = PoolManager(maxsize=1, block=True)

        class MyUserA(HttpUser):
            host = "http://127.0.0.1:%i" % self.port
            pool_manager = shared_pool_manager

        class MyUserB(HttpUser):
            host = "http://127.0.0.1:%i" % self.port
            pool_manager = shared_pool_manager

        user_a = MyUserA(self.environment)
        user_b = MyUserB(self.environment)

        user_a.client.get("/ultra_fast")
        user_b.client.get("/ultra_fast")
        user_b.client.get("/ultra_fast")
        user_a.client.get("/ultra_fast")

        self.assertEqual(1, self.connections_count)
        self.assertEqual(4, self.requests_count)

    def test_pool_manager_per_user_instance(self):
        class MyUser(HttpUser):
            host = "http://127.0.0.1:%i" % self.port

        user_a = MyUser(self.environment)
        user_b = MyUser(self.environment)

        user_a.client.get("/ultra_fast")
        user_b.client.get("/ultra_fast")
        user_b.client.get("/ultra_fast")
        user_a.client.get("/ultra_fast")

        self.assertEqual(2, self.connections_count)
        self.assertEqual(4, self.requests_count)
