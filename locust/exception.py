class LocustError(Exception):
    pass

class ResponseError(LocustError):
    pass

class InterruptLocust(Exception):
    """
    Exception that will interrupt a Locust when thrown inside a task
    """
    
    def __init__(self, reschedule=True):
        """
        If *reschedule* is True and the InterruptLocust is raised inside a SubLocust,
        the parent Locust whould immediately reschedule another task.
        """
        self.reschedule = reschedule

class RescheduleTaskImmediately(Exception):
    """
    When raised in a Locust task, another locust task will be rescheduled immediately
    """
    