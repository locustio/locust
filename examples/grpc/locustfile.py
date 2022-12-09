# make sure you use grpc version 1.39.0 or later,
# because of https://github.com/grpc/grpc/issues/15880 that affected earlier versions
from typing import Callable, Any
import time

import grpc
import grpc.experimental.gevent as grpc_gevent
import gevent
from locust import events, User, task
from locust.exception import LocustError
from grpc_interceptor import ClientInterceptor

import hello_pb2_grpc
import hello_pb2

from hello_server import start_server

# patch grpc so that it uses gevent instead of asyncio
grpc_gevent.init_gevent()


@events.init.add_listener
def run_grpc_server(environment, **_kwargs):
    # Start the dummy server. This is not something you would do in a real test.
    gevent.spawn(start_server)


class LocustInterceptor(ClientInterceptor):
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
            response_length = response.result().ByteSize()
        except grpc.RpcError as e:
            exception = e

        self.env.events.request.fire(
            request_type="grpc",
            name=call_details.method,
            response_time=(time.perf_counter() - start_perf_counter) * 1000,
            response_length=response_length,
            response=response,
            context=None,
            exception=exception,
        )
        return response


class GrpcUser(User):
    abstract = True

    stub_class = None

    def __init__(self, environment):
        super().__init__(environment)
        for attr_value, attr_name in ((self.host, "host"), (self.stub_class, "stub_class")):
            if attr_value is None:
                raise LocustError(f"You must specify the {attr_name}.")

        self._channel = grpc.insecure_channel(self.host)
        interceptor = LocustInterceptor(environment=environment)
        self._channel = grpc.intercept_channel(self._channel, interceptor)

        self.stub = self.stub_class(self._channel)


class HelloGrpcUser(GrpcUser):
    host = "localhost:50051"
    stub_class = hello_pb2_grpc.HelloServiceStub

    @task
    def sayHello(self):
        self.stub.SayHello(hello_pb2.HelloRequest(name="Test"))
        time.sleep(1)
