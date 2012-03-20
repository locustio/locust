=================
Extending Locust
=================

Locust comes with a number of events that provides hooks for extending locust in different ways.

Event listeners can be registered at the module level in a locust file. Here's an example::

    from locust import events
    
    def my_success_handler(method, path, response_time, response):
        print "Successfully fetched: %s" % (path)
    
    events.request_success += my_success_handler

.. seealso::

    To see all available event, please see :ref:`events`.



Adding Web Routes
==================

Locust uses Flask to serve the web UI and therefor it is easy to add web end-points to the web UI. 
Just import the Flask app in your locustfile and set up a new route::

    from locust import web
    
    @web.app.route("/added_page")
    def my_added_page():
        return "Another page"

You should now be able to start locust and browse to http://127.0.0.1:8089/added_page
