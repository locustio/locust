from locust import User
from locust.exception import LocustError

import time
from collections.abc import Callable

import dns.query
from dns.exception import DNSException
from dns.message import Message


class DNSClient:
    def __init__(self, request_event):
        self.request_event = request_event

    def __getattr__(self, function_name) -> Callable[..., Message]:
        func = getattr(dns.query, function_name)

        def wrapper(message: Message, *args, name=None, **kwargs) -> Message:
            response = None
            request_meta = {
                "request_type": "DNS",
                "name": name or function_name,
                "start_time": time.time(),
                "response_length": 0,
                "context": {},
                "exception": None,
            }
            start_perf_counter = time.perf_counter()
            try:
                response = func(message, *args, **kwargs)
            except DNSException as e:
                request_meta["exception"] = e
            else:
                if not response.answer:
                    request_meta["exception"] = LocustError("No answer in DNS response")
            request_meta["response_time"] = (time.perf_counter() - start_perf_counter) * 1000
            request_meta["response"] = response
            self.request_event.fire(**request_meta)
            return response

        return wrapper  # for some reason, pyright still wont infer the return type to be Message


class DNSUser(User):
    """
    DNSUser provides a locust client class for dnspython's :py:mod:`dns.query` methods.
    See example in :gh:`examples/dns_ex.py`.
    """

    abstract = True

    def __init__(self, environment):
        super().__init__(environment)
        self.client = DNSClient(environment.events.request)
        """
        Example (inside task method)::

            message = dns.message.make_query("example.com", dns.rdatatype.A)
            self.client.udp(message, "1.1.1.1")
            self.client.https(message, "1.1.1.1")
        """
