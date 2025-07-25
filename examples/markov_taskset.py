from locust import MarkovTaskSet, User, constant, transition, transitions

"""
This example demonstrates the different ways to specify transitions in a MarkovTaskSet.

The MarkovTaskSet class supports several ways to define transitions between tasks:
1. Using @transition decorator for a single transition
2. Stacking multiple @transition decorators
3. Using @transitions with a dictionary of task names and weights
4. Using @transitions with a list of task names (default weight 1)
5. Using @transitions with a list of tuples (task_name, weight)
6. Using @transitions with a mixed list of strings and tuples
"""


class TransitionsExample(MarkovTaskSet):
    """
    This MarkovTaskSet demonstrates all the different ways to specify transitions.
    """

    @transition("method2")
    def method1(self):
        print("Method 1: Using a single @transition decorator")
        print("  Next: Will transition to method2")

    @transition("method3", weight=2)
    @transition("method1")
    def method2(self):
        print("Method 2: Using multiple stacked @transition decorators")
        print("  Next: Will transition to method3 (weight 2) or method1 (weight 1)")

    @transitions({"method4": 3, "method2": 1, "method1": 1})
    def method3(self):
        print("Method 3: Using @transitions with a dictionary")
        print("  Next: Will transition to method4 (weight 3), method2 (weight 1), or method1 (weight 1)")

    @transitions(["method5", "method3"])
    def method4(self):
        print("Method 4: Using @transitions with a list of task names")
        print("  Next: Will transition to method5 or method3 with equal probability (weight 1 each)")

    @transitions([("method6", 4), ("method4", 1)])
    def method5(self):
        print("Method 5: Using @transitions with a list of tuples")
        print("  Next: Will transition to method6 (weight 4) or method4 (weight 1)")

    @transitions([("method1", 2), "method5"])
    def method6(self):
        print("Method 6: Using @transitions with a mixed list")
        print("  Next: Will transition to method1 (weight 2) or method5 (weight 1)")


class TransitionsUser(User):
    tasks = [TransitionsExample]
    wait_time = constant(1)


if __name__ == "__main__":
    from locust import run_single_user

    run_single_user(TransitionsUser)
