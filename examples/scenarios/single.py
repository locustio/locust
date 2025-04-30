from locust import HttpUser, run_single_user
from locust.user.scenario import Scenario, step, transition, transitions

from enum import StrEnum, auto


class Pages(StrEnum):
    HOME = auto()
    BROWSE = auto()
    CHECKOUT = auto()


class StoreScenario(Scenario):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # weight is optional for @step, first step is assumed first if no other probabilities
    @step(Pages.HOME, weight=1)
    @transition(Pages.BROWSE, 1)
    @transition(Pages.CHECKOUT, 1)
    def home(self):
        print(Pages.HOME)

    # Can pass a dict of transitions
    @step(Pages.BROWSE)
    @transitions({Pages.BROWSE: 7, Pages.CHECKOUT: 3})
    def browse(self):
        print(Pages.BROWSE)

    # Can omit weight (defaults to 1)
    @step(Pages.CHECKOUT)
    @transition(Pages.HOME)
    def checkout(self):
        print(Pages.CHECKOUT)


class MyUser(HttpUser):
    host = "http://localhost"

    tasks = [StoreScenario]


# if launched directly, e.g. "python3 debugging.py", not "locust -f debugging.py"
if __name__ == "__main__":
    run_single_user(MyUser)
