from locust import events, task

import gevent
import grpc_user
import hello_pb2
import hello_pb2_grpc
from hello_server import start_server


# Start the dummy server. This is not something you would do in a real test.
@events.init.add_listener
def run_grpc_server(environment, **_kwargs):
    gevent.spawn(start_server)


class HelloGrpcUser(grpc_user.GrpcUser):
    host = "localhost:50051"
    stub_class = hello_pb2_grpc.HelloServiceStub

    @task
    def sayHello(self):
        self.stub.SayHello(hello_pb2.HelloRequest(name="Test"))
