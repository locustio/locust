"""
Example of implementing authentication with a custom form for Locust when the --web-login
flag is given

This is only to serve as a starting point, proper authentication should be implemented
according to your projects specifications.

For more information, see https://docs.locust.io/en/stable/extending-locust.html#authentication
"""

from __future__ import annotations

from locust import HttpUser, events, task

import os

from flask import Blueprint, redirect, request, session, url_for
from flask_login import UserMixin, login_user


class LocustHttpUser(HttpUser):
    @task
    def example(self):
        self.client.get("/")


class AuthUser(UserMixin):
    def __init__(self, username):
        self.username = username
        self.is_admin = False
        self.user_group: str | None = None

    def get_id(self):
        return self.username


def load_user(user_id):
    return AuthUser(user_id)


@events.init.add_listener
def locust_init(environment, **_kwargs):
    if environment.web_ui:
        auth_blueprint = Blueprint("auth", "web_ui_auth", url_prefix=environment.parsed_options.web_base_path)

        environment.web_ui.login_manager.user_loader(load_user)

        environment.web_ui.app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

        environment.web_ui.auth_args = {
            "custom_form": {
                "inputs": [
                    {
                        "label": "Username",
                        "name": "username",
                    },
                    # boolean checkmark field
                    {"label": "Admin", "name": "is_admin", "default_value": False},
                    # select field
                    {"label": "User Group", "name": "user_group", "choices": ["developer", "manager"]},
                    {
                        "label": "Password",
                        "name": "password",
                        "is_secret": True,
                    },
                    {
                        "label": "Confirm Password",
                        "name": "confirm_password",
                        "is_secret": True,
                    },
                ],
                "callback_url": f"{environment.parsed_options.web_base_path}/login_submit",
                "submit_button_text": "Submit",
            },
        }

        @auth_blueprint.route("/login_submit", methods=["POST"])
        def login_submit():
            username = request.form.get("username")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            is_admin = request.form.get("is_admin") == "on"
            user_group = request.form.get("user_group")

            if password != confirm_password:
                session["auth_error"] = "Passwords do not match!"

                return redirect(url_for("locust.login"))

            # Implement real password verification here
            if password:
                current_user = AuthUser(username)

                # do something with your custom variables
                current_user.is_admin = is_admin
                current_user.user_group = user_group

                login_user(AuthUser(username))

                return redirect(url_for("locust.index"))

            session["auth_error"] = "Invalid username or password"

            return redirect(url_for("locust.login"))

        environment.web_ui.app.register_blueprint(auth_blueprint)
