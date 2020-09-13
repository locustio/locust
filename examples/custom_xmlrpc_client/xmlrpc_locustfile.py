import time
from xmlrpc.client import ServerProxy, Fault

from locust import User, task, between


class XmlRpcClient(ServerProxy):
    """
    Simple, sample XML RPC client implementation that wraps xmlrpclib.ServerProxy and
    fires locust events on request_success and request_failure, so that all requests
    gets tracked in locust's statistics.
    """

    _locust_environment = None

    def __getattr__(self, name):
        func = ServerProxy.__getattr__(self, name)

        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except Fault as e:
                total_time = int((time.time() - start_time) * 1000)
                self._locust_environment.events.request_failure.fire(
                    request_type="xmlrpc", name=name, response_time=total_time, exception=e
                )
            else:
                total_time = int((time.time() - start_time) * 1000)
                self._locust_environment.events.request_success.fire(
                    request_type="xmlrpc", name=name, response_time=total_time, response_length=0
                )
                # In this example, I've hardcoded response_length=0. If we would want the response length to be
                # reported correctly in the statistics, we would probably need to hook in at a lower level

        return wrapper


class XmlRpcUser(User):
    """
    This is the abstract User class which should be subclassed. It provides an XML-RPC client
    that can be used to make XML-RPC requests that will be tracked in Locust's statistics.
    """

    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = XmlRpcClient(self.host)
        self.client._locust_environment = self.environment


class ApiUser(XmlRpcUser):
    host = "http://127.0.0.1:8877/"
    wait_time = between(0.1, 1)

    @task(10)
    def get_time(self):
        self.client.get_time()

    @task(5)
    def get_random_number(self):
        self.client.get_random_number(0, 100)
