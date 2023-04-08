import random
import time
from xmlrpc.server import SimpleXMLRPCServer


def get_time():
    time.sleep(random.random())
    return time.time()


def get_random_number(low, high):
    time.sleep(random.random())
    return random.randint(low, high)


server = SimpleXMLRPCServer(("localhost", 8877))
print("Listening on port 8877...")
server.register_function(get_time, "get_time")
server.register_function(get_random_number, "get_random_number")
server.serve_forever()
