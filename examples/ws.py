# encoding: utf-8

"""
This is an example of a locustfile that uses Locust's built in event hooks to
push events on a websocket
"""

### WebSocket Client
if __name__ == "__main__":
    from ws4py.client.threadedclient import WebSocketClient

    class DummyClient(WebSocketClient):
        def received_message(self, m):
            print m

    try:
        ws = DummyClient('ws://127.0.0.1:8089/ws')
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
else:
    from locust import HttpLocust, TaskSet, task, events, web
    from flask_sockets import Sockets
    import gevent
    import json
    import time

    sockets = Sockets(web.app)
    listeners = []

    def message(ls, event):
        """send event to listener"""
        for ws in ls:
            try:
                ws.send(json.dumps(event))
            except:
                pass

    @sockets.route('/ws')
    def websocket(ws):
        listeners.append(ws)
        ws.send("Start:")
        while True:  # hack to keep the greenlet alive
            gevent.sleep(0.5)

    class MyTaskSet(TaskSet):
        @task(2)
        def index(l):
            l.client.get("/")

    class WebsiteUser(HttpLocust):
        host = "http://127.0.0.1:8089"
        min_wait = 2000
        max_wait = 5000
        task_set = MyTaskSet

    def on_request_success(request_type, name, response_time, response_length):
        """
        Event handler that get triggered on every successful request
        """
        evt = {"name" : name, "response_time" : response_time, "timestamp" : time.time()*1000.0}
        gevent.spawn(message, listeners, evt)

    # Hook up the event listeners
    events.request_success += on_request_success
