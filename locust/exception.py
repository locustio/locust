class LocustError(Exception):
    pass


class ResponseError(Exception):
    pass


class CatchResponseError(Exception):
    pass


class MissingWaitTimeError(LocustError):
    pass


class InterruptTaskSet(Exception):
    """
    Exception that will interrupt a User when thrown inside a task
    """

    def __init__(self, reschedule=True):
        """
        If *reschedule* is True and the InterruptTaskSet is raised inside a nested TaskSet,
        the parent TaskSet would immediately reschedule another task.
        """
        self.reschedule = reschedule


class StopUser(Exception):
    pass


class RescheduleTask(Exception):
    """
    When raised in a task it's equivalent of a return statement.

    Also used internally by TaskSet. When raised within the task control flow of a TaskSet,
    but not inside a task, the execution should be handed over to the parent TaskSet.
    """


class RescheduleTaskImmediately(Exception):
    """
    When raised in a User task, another User task will be rescheduled immediately (without calling wait_time first)
    """


class RPCError(Exception):
    """
    Exception that shows bad or broken network.

    When raised from zmqrpc, RPC should be reestablished.
    """


class RPCSendError(Exception):
    """
    Exception when sending message to client.

    When raised from zmqrpc, sending can be retried or RPC can be reestablished.
    """


class RPCReceiveError(Exception):
    """
    Exception when receiving message from client is interrupted or message is corrupted.

    When raised from zmqrpc, client connection should be reestablished.
    """

    def __init__(self, *args: object, addr=None) -> None:
        super().__init__(*args)
        self.addr = addr


class AuthCredentialsError(ValueError):
    """
    Exception when the auth credentials provided
    are not in the correct format
    """

    pass


class RunnerAlreadyExistsError(Exception):
    pass
