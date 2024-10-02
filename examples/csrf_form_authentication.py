from locust import HttpUser, between, task

import re


class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8089"
    wait_time = between(2, 5)

    @task
    def authenticate(self):
        with self.client.get("/sign-in", catch_response=True) as response:
            match = re.search(
                r'<form.*name="authenticity_token"[^>]*value="([^"]*)"',
                response.text,
            )
            token = match.group(1)

        with self.client.post(
            "/sign-in",
            {
                "user[email]": "username",
                "user[password]": "password",
                "authenticity_token": token,
            },
            catch_response=True,
        ) as response:
            if "welcome" not in response.url:
                response.failure("Login failed")
