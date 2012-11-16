class LocustError(Exception):
    pass

class ResponseError(LocustError):
    pass

class CatchResponseError(LocustError):
    pass

class InterruptTaskSet(Exception):
    """
    Exception that will interrupt a Locust when thrown inside a task
    """
    
    def __init__(self, reschedule=True):
        """
        If *reschedule* is True and the InterruptTaskSet is raised inside a nested TaskSet,
        the parent TaskSet whould immediately reschedule another task.
        """
        self.reschedule = reschedule

class StopLocust(Exception):
    pass

class RescheduleTaskImmediately(Exception):
    """
    When raised in a Locust task, another locust task will be rescheduled immediately
    """
    