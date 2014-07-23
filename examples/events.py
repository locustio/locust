# encoding: utf-8

"""
This is an example of a locustfile that uses Locust's built in event hooks to 
track the sum of the content-length header in all successful HTTP responses
"""

from locust import HttpLocust, TaskSet, task, events, web

class MyTaskSet(TaskSet):
    @task(2)
    def index(l):
        l.client.get("/")
    
    @task(1)
    def stats(l):
        l.client.get("/stats/requests")

class WebsiteUser(HttpLocust):
    host = "http://127.0.0.1:8089"
    min_wait = 2000
    max_wait = 5000
    task_set = MyTaskSet
    

"""
We need somewhere to store the stats.

On the master node stats will contain the aggregated sum of all content-lengths,
while on the slave nodes this will be the sum of the content-lengths since the 
last stats report was sent to the master
"""
stats = {"content-length":0}

def on_request_success(request_type, name, response_time, response_length):
    """
    Event handler that get triggered on every successful request
    """
    stats["content-length"] += response_length

def on_report_to_master(client_id, data):
    """
    This event is triggered on the slave instances every time a stats report is
    to be sent to the locust master. It will allow us to add our extra content-length
    data to the dict that is being sent, and then we clear the local stats in the slave.
    """
    data["content-length"] = stats["content-length"]
    stats["content-length"] = 0

def on_slave_report(client_id, data):
    """
    This event is triggered on the master instance when a new stats report arrives
    from a slave. Here we just add the content-length to the master's aggregated
    stats dict.
    """
    stats["content-length"] += data["content-length"]

# Hook up the event listeners
events.request_success += on_request_success
events.report_to_master += on_report_to_master
events.slave_report += on_slave_report

@web.app.route("/content-length")
def total_content_length():
    """
    Add a route to the Locust web app, where we can see the total content-length
    """
    return "Total content-length recieved: %i" % stats["content-length"]
