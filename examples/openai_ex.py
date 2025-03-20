# You need to install the openai package and set OPENAI_API_KEY env var to run this

# OpenAIUser tracks the number of output tokens in the response_length field,
# because it is more useful than the actual payload size. This field is available to event handlers,
# but only graphed in Locust Cloud.

from locust import run_single_user, task
from locust.contrib.oai import OpenAIUser


class MyUser(OpenAIUser):
    @task
    def t(self):
        self.client.responses.create(
            model="gpt-4o",
            instructions="You are a coding assistant that speaks like it were a Monty Python skit.",
            input="How do I check if a Python object is an instance of a class?",
        )
        with self.client.rename_request("mini"):  # here's how to rename requests
            self.client.responses.create(
                model="gpt-4o-mini",
                instructions="You are a coding assistant that speaks like it were a Monty Python skit.",
                input="How do I check if a Python object is an instance of a class?",
            )


if __name__ == "__main__":
    run_single_user(MyUser)
