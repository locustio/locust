from locust import DynamicConfig, User
from locust.env import Environment

import re

import gevent
import pytest

from .testcases import LocustTestCase


class ConfigA(DynamicConfig):
    config_bucket = {"ratio": 1, "enabled": True, "nested": {"a": [1, 2]}}


class ConfigB(DynamicConfig):
    config_bucket = {"rate": 0.5}


def make_user_classes():
    class UserA(User):
        dynamic_config = ConfigA()

    class UserB(User):
        dynamic_config = ConfigB()

    class UserWithoutConfig(User):
        pass

    return UserA, UserB, UserWithoutConfig


def test_instances_do_not_share_state_or_modify_defaults():
    first, second = ConfigA(), ConfigA()
    first.update_config_bucket({"ratio": 5})
    first.get_config_bucket()["nested"]["a"].append(3)

    assert second.get_config_bucket() == {"ratio": 1, "enabled": True, "nested": {"a": [1, 2]}}
    assert ConfigA.config_bucket["ratio"] == 1
    assert ConfigA.config_bucket["nested"]["a"] == [1, 2]


def test_update_config_bucket_keeps_other_values():
    config = ConfigA()
    config.update_config_bucket({"enabled": False})
    assert config.get_config_bucket() == {"ratio": 1, "enabled": False, "nested": {"a": [1, 2]}}


def test_apply_sets_attributes_on_user_class():
    user_a, _, _ = make_user_classes()
    config = ConfigA()
    config.update_config_bucket({"ratio": 7})
    config.apply(user_a)
    assert user_a.ratio == 7
    assert user_a.enabled is True


def test_apply_can_be_overridden():
    class DoublingConfig(DynamicConfig):
        config_bucket = {"ratio": 2}

        def apply(self, user_class):
            super().apply(user_class)
            user_class.double_ratio = self.config_bucket["ratio"] * 2

    class MyUser(User):
        dynamic_config = DoublingConfig()

    Environment(user_classes=[MyUser]).update_dynamic_config({"MyUser": {"ratio": 5}})
    assert MyUser.ratio == 5
    assert MyUser.double_ratio == 10


class TestDynamicConfigEnvironment(LocustTestCase):
    def setUp(self):
        super().setUp()
        self.user_a, self.user_b, self.user_without_config = make_user_classes()
        self.env = Environment(user_classes=[self.user_a, self.user_b, self.user_without_config])

    def test_defaults_are_applied_on_environment_creation(self):
        self.assertEqual(self.user_a.ratio, 1)
        self.assertEqual(self.user_b.rate, 0.5)

    def test_get_dynamic_config_only_has_classes_with_config(self):
        self.assertEqual(
            self.env.get_dynamic_config(),
            {"UserA": {"ratio": 1, "enabled": True, "nested": {"a": [1, 2]}}, "UserB": {"rate": 0.5}},
        )

    def test_no_dynamic_config(self):
        self.assertEqual(Environment(user_classes=[self.user_without_config]).get_dynamic_config(), {})

    def test_update_multiple_user_classes(self):
        self.env.update_dynamic_config({"UserA": {"ratio": 3}, "UserB": {"rate": 2.5}})

        self.assertEqual(self.user_a.ratio, 3)
        self.assertIs(self.user_a.enabled, True)
        self.assertEqual(self.user_b.rate, 2.5)

    def test_update_single_user_class_leaves_others_untouched(self):
        self.env.update_dynamic_config({"UserB": {"rate": 9}})

        self.assertEqual(self.user_b.rate, 9)
        self.assertEqual(self.user_a.ratio, 1)
        self.assertEqual(self.env.get_dynamic_config()["UserA"]["ratio"], 1)

    def test_update_is_visible_to_running_user_instances(self):
        user = self.user_a(self.env)
        self.env.update_dynamic_config({"UserA": {"ratio": 4}})
        self.assertEqual(user.ratio, 4)

    def test_invalid_updates_change_nothing(self):
        invalid_updates = [
            ({"UserA": {"ratio": 3}, "Missing": {"x": 1}}, "User class 'Missing' has no dynamic config"),
            ({"UserWithoutConfig": {"x": 1}}, "User class 'UserWithoutConfig' has no dynamic config"),
            (
                {"UserB": {"rate": 3}, "UserA": {"ratio": 3, "bogus": 1}},
                "Unknown setting(s) for user class 'UserA': bogus",
            ),
            ({"UserA": 5}, "must be an object"),
            ([1, 2], "must be an object"),
            (None, "must be an object"),
        ]
        for update, message in invalid_updates:
            with self.subTest(update=update):
                with pytest.raises(ValueError, match=re.escape(message)):
                    self.env.update_dynamic_config(update)
                self.assertEqual(self.user_a.ratio, 1)
                self.assertEqual(self.user_b.rate, 0.5)

    def test_distributed_update_reaches_workers_and_late_joiners(self):
        master = self.env.create_master_runner("*", 0)

        # fresh classes, because the workers of this test share the process (and class objects) with the master
        worker_a, worker_b, _ = make_user_classes()
        worker_env = Environment(user_classes=[worker_a, worker_b])
        worker_env.create_worker_runner("127.0.0.1", master.server.port)
        gevent.sleep(0.2)

        self.env.update_dynamic_config({"UserA": {"ratio": 6}, "UserB": {"rate": 8}})
        gevent.sleep(0.2)
        self.assertEqual((worker_a.ratio, worker_b.rate), (6, 8))

        # a worker that connects afterwards gets the current config instead of the defaults
        late_a, late_b, _ = make_user_classes()
        late_env = Environment(user_classes=[late_a, late_b])
        self.assertEqual(late_a.ratio, 1)
        late_env.create_worker_runner("127.0.0.1", master.server.port)
        gevent.sleep(0.2)
        self.assertEqual((late_a.ratio, late_b.rate), (6, 8))
