=================
Extending Locust
=================

Locust comes with a number of events hooks that can be used to extend Locust in different ways.

Event hooks live on the Environment instance under the :py:attr:`events <locust.env.Environment.events>` 
attribute. However, since the Environment instance hasn't been created when locustfiles are imported,  
the events object can also be accessed at the module level of the locustfile through the 
:py:obj:`locust.events` variable.

Here's an example on how to set up an event listener::

    from locust import events
    
    @events.request_success.add_listener
    def my_success_handler(request_type, name, response_time, response_length, **kw):
        print("Successfully made a request to: %s" % name)


.. note::

    It's highly recommended that you add a wildcard keyword argument in your listeners
    (the \**kw in the code above), to prevent your code from breaking if new arguments are
    added in a future version.

.. seealso::

    To see all available event, please see :ref:`events`.



Adding Web Routes
==================

Locust uses Flask to serve the web UI and therefore it is easy to add web end-points to the web UI.
By listening to the :py:attr:`init <locust.event.Events.init>` event, we can retrieve a reference 
to the Flask app instance and use that to set up a new route::

    from locust import events
    
    @events.init.add_listener
    def on_locust_init(web_ui, **kw):
        @web_ui.app.route("/added_page")
        def my_added_page():
            return "Another page"

You should now be able to start locust and browse to http://127.0.0.1:8089/added_page

