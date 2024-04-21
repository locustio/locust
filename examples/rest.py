from locust import FastHttpUser, run_single_user, task
from locust.contrib.fasthttp import RestResponseContextManager
from locust.user.wait_time import constant

from collections.abc import Generator
from contextlib import contextmanager


class MyUser(FastHttpUser):
    host = "https://postman-echo.com"
    wait_time = constant(180)  # be nice to postman-echo.com, and dont run this at scale.

    @task
    def t(self):
        # should work
        with self.rest("GET", "/get", json={"foo": 1}) as resp:
            if resp.js["args"]["foo"] != 1:
                resp.failure(f"Unexpected value of foo in response {resp.text}")

        # should work
        with self.rest("POST", "/post", json={"foo": 1}) as resp:
            if resp.js["data"]["foo"] != 1:
                resp.failure(f"Unexpected value of foo in response {resp.text}")
            # assertions are a nice short way to express your expectations about the response. The AssertionError thrown will be caught
            # and fail the request, including the message and the payload in the failure content.
            assert resp.js["data"]["foo"] == 1, "Unexpected value of foo in response"

        # assertions are a nice short way to validate the response. The AssertionError they raise
        # will be caught by rest() and mark the request as failed

        with self.rest("POST", "/post", json={"foo": 1}) as resp:
            # mark the request as failed with the message "Assertion failed"
            assert resp.js["data"]["foo"] == 2

        with self.rest("POST", "/post", json={"foo": 1}) as resp:
            # custom failure message
            assert resp.js["data"]["foo"] == 2, "my custom error message"

        with self.rest("POST", "/post", json={"foo": 1}) as resp:
            # use a trailing comma to append the response text to the custom message
            assert resp.js["data"]["foo"] == 2, "my custom error message with response text,"

        with self.rest("", "/post", json={"foo": 1}) as resp:
            # assign and assert in one line
            assert (foo := resp.js["foo"])
            print(f"the number {foo} is awesome")

        # rest() catches most exceptions, so any programming mistakes you make automatically marks the request as a failure
        # and stores the callstack in the failure message
        with self.rest("POST", "/post", json={"foo": 1}) as resp:
            1 / 0  # pylint: disable=pointless-statement

        # response isn't even json, but RestUser will already have been marked it as a failure, so we dont have to do it again
        with self.rest("GET", "/") as resp:
            pass

        with self.rest("GET", "/") as resp:
            # If resp.js is None (which it will be when there is a connection failure, a non-json responses etc),
            # reading from resp.js will raise a TypeError (instead of an AssertionError), so lets avoid that:
            if resp.js:
                assert resp.js["foo"] == 2
            # or, as a mildly confusing oneliner:
            assert not resp.js or resp.js["foo"] == 2

        # 404
        with self.rest("GET", "http://example.com/") as resp:
            pass

        # connection closed
        with self.rest("POST", "http://example.com:42/", json={"foo": 1}) as resp:
            pass


# An example of how you might write a common base class for an API that always requires
# certain headers, or where you always want to check the response in a certain way
class RestUserThatLooksAtErrors(FastHttpUser):
    abstract = True

    @contextmanager
    def rest(self, method, url, **kwargs) -> Generator[RestResponseContextManager, None, None]:
        extra_headers = {"my_header": "my_value"}
        with super().rest(method, url, headers=extra_headers, **kwargs) as resp:
            if resp.js and "error" in resp.js and resp.js["error"] is not None:
                resp.failure(resp.js["error"])
            yield resp


class MyOtherRestUser(RestUserThatLooksAtErrors):
    host = "https://postman-echo.com"
    wait_time = constant(180)  # be nice to postman-echo.com, and dont run this at scale.

    @task
    def t(self):
        with self.rest("GET", "/") as _resp:
            pass


if __name__ == "__main__":
    run_single_user(MyUser)
