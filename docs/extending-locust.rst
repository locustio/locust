.. _extending_locust:

===========
Event hooks
===========

Locust comes with a number of event hooks that can be used to extend Locust in different ways.

For example, here's how to set up an event listener that will trigger after a request is completed::

    from locust import events

    @events.request.add_listener
    def my_request_handler(request_type, name, response_time, response_length, response,
                           context, exception, start_time, url, **kwargs):
        if exception:
            print(f"Request to {name} failed with exception {exception}")
        else:
            print(f"Successfully made a request to: {name}")
            print(f"The response was {response.text}")

.. note::

    In the above example the wildcard keyword argument (\**kwargs) will be empty, because we're handling all arguments, but it prevents the code from breaking if new arguments are added in some future version of Locust.

    Also, it is entirely possible to implement a client that does not supply all parameters for this event.
    For example, non-HTTP protocols might not even have the a concept of `url` or `response` object.
    Remove any such missing field from your listener function definition or use default arguments.

When running locust in distributed mode, it may be useful to do some setup on worker nodes before running your tests.
You can check to ensure you aren't running on the master node by checking the type of the node's :py:attr:`runner <locust.env.Environment.runner>`::

    from locust import events
    from locust.runners import MasterRunner

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        if not isinstance(environment.runner, MasterRunner):
            print("Beginning test setup")
        else:
            print("Started test from Master node")

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        if not isinstance(environment.runner, MasterRunner):
            print("Cleaning up test data")
        else:
            print("Stopped test from Master node")

You can also use events `to add custom command line arguments <https://github.com/locustio/locust/tree/master/examples/add_command_line_argument.py>`_.

To see a full list of available events see :ref:`events`.

.. _request_context:


Request context
===============

The :py:attr:`request event <locust.event.Events.request>` has a context parameter that enable you to pass data `about` the request (things like username, tags etc). It can be set directly in the call to the request method or at the User level, by overriding the User.context() method.

Context from request method::

    class MyUser(HttpUser):
        @task
        def t(self):
            self.client.post("/login", json={"username": "foo"})
            self.client.get("/other_request", context={"username": "foo"})

        @events.request.add_listener
        def on_request(context, **kwargs):
            if context:
                print(context["username"])

Context from User instance::

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


Context from a value in the response, using :ref:`catch_response <catch-response>`::

    with self.client.get("/", catch_response=True) as resp:
        resp.request_meta["context"]["requestId"] = resp.json()["requestId"]


Adding Web Routes
==================

Locust uses Flask to serve the web UI and therefore it is easy to add web end-points to the web UI.
By listening to the :py:attr:`init <locust.event.Events.init>` event, we can retrieve a reference
to the Flask app instance and use that to set up a new route::

    from locust import events

    @events.init.add_listener
    def on_locust_init(environment, **kw):
        @environment.web_ui.app.route("/added_page")
        def my_added_page():
            return "Another page"

You should now be able to start locust and browse to http://127.0.0.1:8089/added_page. Note that it doesn't get automatically added as a new tab - you'll need to enter the URL directly.

Extending Web UI
================

As an alternative to adding simple web routes, you can use `Flask Blueprints
<https://flask.palletsprojects.com/en/1.1.x/blueprints/>`_ and `templates
<https://flask.palletsprojects.com/en/1.1.x/tutorial/templates/>`_ to not only add routes but also extend
the web UI to allow you to show custom data along side the built-in Locust stats. This is more advanced
as it involves also writing and including HTML and Javascript files to be served by routes but can
greatly enhance the utility and customizability of the web UI.

A working example of extending the web UI, complete with HTML and Javascript example files, can be found
in the `examples directory <https://github.com/locustio/locust/tree/master/examples/>`_ of the Locust
source code.

*  ``extend_modern_web_ui.py``: Display a table with content-length for each call.

* ``web_ui_cache_stats.py``: Display Varnish Hit/Miss stats for each call. This could easily be extended to other CDN or cache proxies and gather other cache statistics such as cache age, control, ...

 .. image:: images/extend_modern_web_ui_cache_stats.png


Adding Authentication to the Web UI
===================================

Locust uses `Flask-Login <https://pypi.org/project/Flask-Login/>`_ to handle authentication. The ``login_manager`` is
exposed on ``environment.web_ui.app``, allowing the flexibility for you to implement any kind of auth that you would like!

To use username / password authentication, simply provide a ``username_password_callback`` to the ``environment.web_ui.auth_args``.
You are responsible for defining the route for the callback and implementing the authentication.

Authentication providers can additionally be configured to allow authentication from 3rd parties such as GitHub or an SSO.
Simply provide a list of desired ``auth_providers``. You may specify the ``label`` and ``icon`` for display on the button.
The ``callback_url`` will be the url that the button directs to. You will be responsible for defining the callback route as
well as the authentication with the 3rd party.

Whether you are using username / password authentication, an auth provider, or both, a ``user_loader`` needs to be proivded
to the ``login_manager``. The ``user_loader`` should return ``None`` to deny authentication or return a User object when
authentication to the app should be granted.

A full example can be seen `in the auth example <https://github.com/locustio/locust/tree/master/examples/web_ui_auth.py>`_.


Run a background greenlet
=========================

Because a locust file is "just code", there is nothing preventing you from spawning your own greenlet to
run in parallel with your actual load/Users.

For example, you can monitor the fail ratio of your test and stop the run if it goes above some threshold:

.. code-block:: python

    import gevent
    from locust import events
    from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, MasterRunner, LocalRunner

    def checker(environment):
        while not environment.runner.state in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
            time.sleep(1)
            if environment.runner.stats.total.fail_ratio > 0.2:
                print(f"fail ratio was {environment.runner.stats.total.fail_ratio}, quitting")
                environment.runner.quit()
                return


    @events.init.add_listener
    def on_locust_init(environment, **_kwargs):
        # dont run this on workers, we only care about the aggregated numbers
        if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, LocalRunner):
            gevent.spawn(checker, environment)

.. _parametrizing-locustfiles:


Parametrizing locustfiles
=========================

There are two main ways to parametrize your locustfile.

Basic environment variables
---------------------------

Like with any program, you can use environment variables:

On linux/mac:

.. code-block:: bash

    MY_FUNKY_VAR=42 locust ...

On windows:

.. code-block:: bash

    SET MY_FUNKY_VAR=42
    locust ...

... and then access them in your locustfile.

.. code-block:: python

    import os
    print(os.environ['MY_FUNKY_VAR'])

.. _custom-arguments:

Custom arguments
----------------

You can add your own command line arguments to Locust, using the :py:attr:`init_command_line_parser <locust.event.Events.init_command_line_parser>` Event. Custom arguments are also presented and editable in the web UI. If `choices` are specified for the argument, they will be presented as a dropdown in the web UI.

.. literalinclude:: ../examples/add_command_line_argument.py
    :language: python

When running Locust :ref:`distributed <running-distributed>`, custom arguments are automatically forwarded to workers when the run is started (but not before then, so you cannot rely on forwarded arguments *before* the test has actually started).


Test data management
====================

There are a number of ways to get test data into your tests (after all, your test is just a Python program and it can do whatever Python can). Locust's events give you fine-grained control over *when* to fetch/release test data. You can find a `detailed example here <https://github.com/locustio/locust/tree/master/examples/test_data_management.py>`_.


More examples
=============

See `locust-plugins <https://github.com/SvenskaSpel/locust-plugins#listeners>`_
