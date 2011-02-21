class LocustError(Exception):
    pass

class InterruptLocust(Exception):
    """
    Exception that will interrupt a Locust when thrown inside a task
    """
