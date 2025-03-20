# Note: this User is experimental and may change without notice.
# The filename is oai.py so it doesnt clash with the openai package.
from locust.user import User

import os
import time
from collections.abc import Generator
from contextlib import contextmanager

import httpx
from openai import OpenAI  # dont forget to install openai

# convenience for when running in Locust Cloud, where only LOCUST_* env vars are forwarded
if "LOCUST_OPENAI_API_KEY" in os.environ:
    os.environ["OPENAI_API_KEY"] = os.environ["LOCUST_OPENAI_API_KEY"]

if not "OPENAI_API_KEY" in os.environ:
    raise Exception("You need to set OPENAI_API_KEY or LOCUST_OPENAI_API_KEY env var to use OpenAIUser")


class OpenAIClient(OpenAI):
    def __init__(self, request_event, user, *args, **kwargs):
        self.request_name = None  # used to override url-based request names
        self.user = user  # currently unused, but could be useful later

        def request_start(request):
            request.start_time = time.time()
            request.start_perf_counter = time.perf_counter()

        def request_end(response):
            exception = None
            response.read()
            response_time = (time.perf_counter() - response.request.start_perf_counter) * 1000
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                exception = e
            request_event.fire(
                request_type=response.request.method,
                name=self.request_name if self.request_name else response.url.path,
                context={},
                response=response,
                exception=exception,
                start_time=response.request.start_time,
                response_time=response_time,
                # Store the number of output tokens as response_length instead of the actual payload size because it is more useful
                response_length=response.json().get("usage", {}).get("output_tokens", 0),
                url=response.url,
            )

        super().__init__(
            *args,
            **kwargs,
            http_client=httpx.Client(event_hooks={"request": [request_start], "response": [request_end]}),
        )

    @contextmanager
    def rename_request(self, name: str) -> Generator[None]:
        """Group requests using the "with" keyword"""

        self.request_name = name
        try:
            yield
        finally:
            self.request_name = None


class OpenAIUser(User):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = OpenAIClient(self.environment.events.request, user=self)
