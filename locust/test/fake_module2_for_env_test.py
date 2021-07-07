"""Module for locust.test.test_env.TestEnvironment.test_user_classes_with_same_name_is_error"""

from locust import User


class MyUserWithSameName(User):
    pass
