=================
Extending Locust
=================

Locust comes with a number of events hooks that can be used to extend Locust in different ways.

Most event hooks live on the Environment instance under the :py:attr:`events <locust.env.Environment.events>` 
attribute. However the Environment instance is not available at the module level of your test 
file, so in order to utilize the :py:attr:`events <locust.env.Environment.events>` on the 
:py:class:`Environment <locust.env.Environment>` class, you can utilize the :py:attr:`locust.events.init` 
event which is triggered when Locust is started.

Adding the following code at the module level of you locustfile.py will print a message when Locust starts::

    from locust.events import init
    
    @init.add_listener
    def on_locust_init(environment, **kw):
        print("Locust is starting")


We can use this event listener to setup listeners for other events::

    from locust.events import init
    
    @init.add_listener
    def on_locust_init(environment, **kw):
        @environment.events.request_success
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
From the Environment instance, we can access the Flask app and set up a new route::

    from locust.events import init
    
    @init.add_listener
    def on_locust_init(environment, **kw):
        @environment.web_ui.app.route("/added_page")
        def my_added_page():
            return "Another page"

You should now be able to start locust and browse to http://127.0.0.1:8089/added_page

