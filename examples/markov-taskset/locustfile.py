from locust import HttpUser, run_single_user
from locust.user.markov_taskset import MarkovTaskSet, transition, transitions


class StoreScenario(MarkovTaskSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # weight is optional for @step
    #   first step is assumed to be the initial step
    #   if weights are given, the initial step is chosen from those with weights
    @transition("browse", 1)
    @transition("checkout", 1)
    def home(self):
        print("home")

    # Can pass a dict of transitions
    @transitions({"browse": 7, "checkout": 3})
    def browse(self):
        print("browse")

    # Can omit weight (defaults to 1)
    @transition("home")
    def checkout(self):
        print("checkout")


class MyUser(HttpUser):
    host = "http://localhost"

    tasks = [StoreScenario]


# if launched directly, e.g. "python3 debugging.py", not "locust -f debugging.py"
if __name__ == "__main__":
    run_single_user(MyUser)
