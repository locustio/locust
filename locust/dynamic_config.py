from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .user.users import User


class DynamicConfig:
    """
    Settings of a :class:`User <locust.User>` class that can be changed while a test is running,
    for example from the web UI.

    Subclass it, list the settings and their default values in :attr:`config_bucket` and attach an
    instance to your user class using :attr:`User.dynamic_config <locust.User.dynamic_config>`.
    Every key in the bucket is available as an attribute of the user class, so tasks read the current
    value with ``self.<key>``::

        class MyConfig(DynamicConfig):
            config_bucket = {"think_time": 1, "enable_checkout": True}

        class MyUser(HttpUser):
            dynamic_config = MyConfig()

            @task
            def checkout(self):
                if self.enable_checkout:
                    ...

    Each user class has its own config, so a locustfile with several user classes can have several.
    """

    config_bucket: dict[str, Any] = {}
    """Setting names and their default values. Values must be JSON serializable."""

    def __init__(self) -> None:
        # a per-instance copy keeps runtime changes out of the class level defaults
        self.config_bucket = copy.deepcopy(type(self).config_bucket)

    def get_config_bucket(self) -> dict[str, Any]:
        """Returns the current settings."""
        return self.config_bucket

    def update_config_bucket(self, values: dict[str, Any]) -> None:
        """Updates the given settings and leaves the others unchanged."""
        self.config_bucket.update(values)

    def apply(self, user_class: type[User]) -> None:
        """
        Assigns the current settings as attributes of ``user_class``.

        Called by Locust on startup and every time the settings change. It can be overridden
        for extra processing, but then it must still set the attributes (or call ``super().apply()``).
        """
        for key, value in self.config_bucket.items():
            setattr(user_class, key, value)
