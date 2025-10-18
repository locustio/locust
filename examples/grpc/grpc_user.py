from locust import User
from locust.exception import LocustError

import time
from collections.abc import Callable
from typing import Any

import grpc
import grpc.experimental.gevent as grpc_gevent
from grpc_interceptor import ClientInterceptor

# patch grpc so that it uses gevent instead of asyncio
grpc_gevent.init_gevent()


class LocustInterceptor(ClientInterceptor):
    """
    Intercepts gRPC calls to measure and report request metrics to Locust.

    This interceptor measures the response time for each gRPC request and fires
    a request event that Locust uses for statistics collection.
    """

    def __init__(self, environment, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.env = environment

    def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        call_details: grpc.ClientCallDetails,
    ):
        response = None
        exception = None
        start_perf_counter = time.perf_counter()
        response_length = 0
        try:
            response = method(request_or_iterator, call_details)
            # Wait for the response to complete to measure the actual response time
            # This call blocks until the RPC completes, ensuring accurate timing
            result = response.result()
            response_length = result.ByteSize()
            response_time = (time.perf_counter() - start_perf_counter) * 1000
        except grpc.RpcError as e:
            exception = e
            response_time = (time.perf_counter() - start_perf_counter) * 1000

        self.env.events.request.fire(
            request_type="grpc",
            name=call_details.method,
            response_time=response_time,
            response_length=response_length,
            response=response,
            context=None,
            exception=exception,
        )
        return response


class GrpcUser(User):
    """
    A base class for gRPC load testing with Locust.

    Each user instance creates its own gRPC channel. gRPC channels are designed to be long-lived
    and can handle multiple concurrent RPCs. The channel is properly closed when the user stops.

    To use this class, subclass it and specify:
    - host: The gRPC server address (e.g., "localhost:50051")
    - stub_class: The gRPC stub class to use (e.g., generated from .proto file)
    """

    abstract = True
    stub_class = None

    def __init__(self, environment):
        super().__init__(environment)
        for attr_value, attr_name in ((self.host, "host"), (self.stub_class, "stub_class")):
            if attr_value is None:
                raise LocustError(f"You must specify the {attr_name}.")

        # Create a gRPC channel for this user
        # Each user gets its own channel, allowing for realistic connection simulation
        self._channel = grpc.insecure_channel(self.host)
        interceptor = LocustInterceptor(environment=environment)
        self._channel = grpc.intercept_channel(self._channel, interceptor)

        self.stub = self.stub_class(self._channel)

    def on_stop(self):
        """Close the gRPC channel when the user stops."""
        self._channel.close()
