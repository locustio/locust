class LocustError(Exception):
    pass

class ResponseError(Exception):
    pass

class CatchResponseError(Exception):
    pass

class InterruptTaskSet(Exception):
    """
    Exception that will interrupt a Locust when thrown inside a task
    """
    
    def __init__(self, reschedule=True, totaskset=None):
        """
        If *reschedule* is True and the InterruptTaskSet is raised inside a nested TaskSet,
        the parent TaskSet whould immediately reschedule another task.
        """
        self.reschedule = reschedule
        self.totaskset = totaskset

class StopLocust(Exception):
    pass

class RescheduleTask(Exception):
    """
    When raised in a task it's equivalent of a return statement.
    
    Used internally by TaskSet. When raised within the task control flow of a TaskSet, 
    but not inside a task, the execution should be handed over to the parent TaskSet.
    """
    def __init__(self, totaskset=None):
        self.totaskset=totaskset

class RescheduleTaskImmediately(Exception):
    """
    When raised in a Locust task, another locust task will be rescheduled immediately
    """
    def __init__(self, totaskset=None):
        self.totaskset=totaskset
