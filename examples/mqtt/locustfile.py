from locust import task
from locust.contrib.mqtt import MqttUser
from locust.user.wait_time import between

import time


class MyUser(MqttUser):
    host = "localhost"
    port = 1883

    # We could uncomment below to use the WebSockets transport
    # transport = "websockets"

    # ws_path = "/mqtt/custom/path"

    # We'll probably want to throttle our publishing a bit: let's limit it to
    # 10-100 messages per second.
    wait_time = between(0.01, 0.1)

    # Uncomment below if you need to set MQTTv5
    # protocol = paho.mqtt.client.MQTTv5

    # Sleep for a while to allow the client time to connect.
    # This is probably not the most "correct" way to do this: a better method
    # might be to add a gevent.event.Event to the MqttClient's on_connect
    # callback and wait for that (with a timeout) here.
    # However, this works well enough for the sake of an example.
    def on_start(self):
        time.sleep(5)

    @task
    def say_hello(self):
        self.client.publish("hello/locust", b"hello world")
