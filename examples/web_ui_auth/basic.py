"""
Example of implementing authentication for Locust when the --web-login flag is given

This is only to serve as a starting point, proper authentication should be implemented
according to your projects specifications.

For more information, see https://docs.locust.io/en/stable/extending-locust.html#authentication
"""

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

    def get_id(self):
        return self.username


def load_user(username):
    return AuthUser(username)


@events.init.add_listener
def locust_init(environment, **_kwargs):
    if environment.web_ui:
        auth_blueprint = Blueprint("auth", "web_ui_auth", url_prefix=environment.parsed_options.base_path)

        environment.web_ui.login_manager.user_loader(load_user)

        environment.web_ui.app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

        environment.web_ui.auth_args = {
            "username_password_callback": f"{environment.parsed_options.base_path}/login_submit",
            "auth_providers": [
                {
                    "label": "Github",
                    "callback_url": "/login/github",
                    "icon_url": "https://static-00.iconduck.com/assets.00/github-icon-1024x994-4h5sdmko.png",
                },
            ],
        }

        @auth_blueprint.route("/login/github")
        def google_login():
            # Implement authentication with desired auth provider
            username = "username"
            session["username"] = username
            login_user(AuthUser("username"))

            return redirect(url_for("locust.index"))

        @auth_blueprint.route("/login_submit", methods=["POST"])
        def login_submit():
            username = request.form.get("username")
            password = request.form.get("password")

            # Implement real password verification here
            if password:
                login_user(AuthUser(username))

                return redirect(url_for("locust.index"))

            session["auth_error"] = "Invalid username or password"

            return redirect(url_for("locust.login"))

        environment.web_ui.app.register_blueprint(auth_blueprint)
