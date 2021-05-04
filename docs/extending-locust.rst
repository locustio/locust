.. _extending_locust:

==================================
Extending Locust using event hooks
==================================

Locust comes with a number of event hooks that can be used to extend Locust in different ways.

Event hooks are registered on the Environment under its :py:attr:`events <locust.env.Environment.events>` 
attribute, but they are more conveniently accessed via the :py:obj:`locust.events` variable (because the Environment 
is instantiated *after* importing the locustfile)

Here's an example on how to set up an event listener::

    from locust import events
    
    @events.request.add_listener
    def my_request_handler(request_type, name, response_time, response_length, response,
                           context, exception, **kwargs):
        if exception:
            print(f"Request to {name} failed with exception {exception}")
        else:
            print(f"Successfully made a request to: {name})
            print(f"The response was {response.text}")

.. note::

    To see all available events, please see :ref:`events`.

    In the above example the wildcard keyword argument (\**kwargs) will be empty but it 
    is prevents the code from breaking if new arguments are added in some future version of Locust.

    It is entirely possible to implement a client that does not support all parameters 
    (some non-HTTP protocols might not have a concept of `response_length` or `response` object).

.. _request_context:

Request context
==================

The :py:attr:`request event <locust.event.Events.request>` has a context parameter that enable you to pass data `about` the request (things like username, tags etc). It can be set directly in the call to the request method or at the User level, by overriding the User.context() method. 

Context from request method::

    class MyUser(HttpUser):
        @task
        def t(self):
            self.client.post("/login", json={"username": "foo"}, context={"username": "foo"})

        @events.request.add_listener
        def on_request(context, **kwargs):
            print(context["username"])
    
Context from User class::

    class MyUser(HttpUser):
        def context(self):
            return {"username": self.username}

        @task
        def t(self):
            self.username = "foo"
            self.client.post("/login", json={"username": self.username})

        @events.request.add_listener
        def on_request(context, **kwargs):
            print(context["username"])


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



Extending Web UI
================

As an alternative to adding simple web routes, you can use `Flask Blueprints 
<https://flask.palletsprojects.com/en/1.1.x/blueprints/>`_ and `templates 
<https://flask.palletsprojects.com/en/1.1.x/tutorial/templates/>`_ to not only add routes but also extend 
the web UI to allow you to show custom data along side the built-in Locust stats. This is more advanced 
as it involves also writing and including HTML and Javascript files to be served by routes but can 
greatly enhance the utility and customizability of the web UI.

A working example of extending the web UI, complete with HTML and Javascript example files, can be found 
in the `examples directory <https://github.com/locustio/locust/tree/master/examples>`_ of the Locust 
source code.



Run a background greenlet
=========================

Because a locust file is "just code", there is nothing preventing you from spawning your own greenlet to
run in parallel with your actual load/Users.

For example, you can monitor the fail ratio of your test and stop the run if it goes above some threshold:

.. code-block:: python

    from locust import events
    from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, WorkerRunner

    def checker(environment):
        while not environment.runner.state in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
            time.sleep(1)
            if environment.runner.stats.total.fail_ratio > 0.2:
                print(f"fail ratio was {environment.runner.stats.total.fail_ratio}, quitting")
                environment.runner.quit()
                return


    @events.init.add_listener
    def on_locust_init(environment, **_kwargs):
        # only run this on master & standalone
        if not isinstance(environment.runner, WorkerRunner):
            gevent.spawn(checker, environment)


More examples
=============

See `locust-plugins <https://github.com/SvenskaSpel/locust-plugins#listeners>`_
