import logging
import time
from concurrent import futures

import grpc
import hello_pb2
import hello_pb2_grpc

logger = logging.getLogger(__name__)


class HelloServiceServicer(hello_pb2_grpc.HelloServiceServicer):
    def SayHello(self, request, context):
        name = request.name
        time.sleep(1)
        return hello_pb2.HelloResponse(message=f"Hello from Locust, {name}!")


def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hello_pb2_grpc.add_HelloServiceServicer_to_server(HelloServiceServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    logger.info("gRPC server started")
    server.wait_for_termination()


if __name__ == "__main__":
    start_server()
