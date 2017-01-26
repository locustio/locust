=================
Extending Locust
=================

Locust comes with a number of events that provides hooks for extending locust in different ways.

Event listeners can be registered at the module level in a locust file. Here's an example::

    from locust import events

    def my_success_handler(request_type, name, response_time, response_length, **kw):
        print "Successfully fetched: %s" % (name)

    events.request_success += my_success_handler

.. note::

    It's highly recommended that you add a wildcard keyword argument in your listeners
    (the \**kw in the code above), to prevent your code from breaking if new arguments are
    added in a future version.

.. seealso::

    To see all available event, please see :ref:`events`.



Adding Web Routes
==================

Locust uses Flask to serve the web UI and therefore it is easy to add web end-points to the web UI.
Just import the Flask app in your locustfile and set up a new route::

    from locust import web

    @web.app.route("/added_page")
    def my_added_page():
        return "Another page"

You should now be able to start locust and browse to http://127.0.0.1:8089/added_page
