.. _quickstart:

=============
Hello World
=============

A Locust test is essentially a Python program. This makes it very flexible, but it can do simple tests as well, so lets start with that:

.. code-block:: python

    from locust import HttpUser, task

    class HelloWorldUser(HttpUser):
        @task
        def hello_world(self):
            self.client.get("/hello")
            self.client.get("/world")

This user will make HTTP requests to ``/hello``, and then ``/world``, again and again. For a full explanation and a more realistic example, keep reading.

Put the code in a file named *locustfile.py* in your current directory and run ``locust``:

.. code-block:: console
    :substitutions:

    $ locust
    [2021-07-24 09:58:46,215] .../INFO/locust.main: Starting web interface at http://*:8089
    [2021-07-24 09:58:46,285] .../INFO/locust.main: Starting Locust |version|

Locust's web interface
==============================

Once you've started Locust, open up a browser and point it to http://localhost:8089. You will be greeted with something like this:

.. image:: images/webui-splash-screenshot.png
| 
Point the test to your web server and try it out!

These screenshots show what it might look like when running the more complete example further down this page:

.. image:: images/webui-running-statistics.png

You can also view the results as a chart:

.. image:: images/webui-running-charts.png

|

Direct command line usage / headless
====================================

Using the Locust web UI is entirely optional. You can supply the load parameters on command line and get reports on the results in text form:

.. code-block:: console
    :substitutions:

    $ locust --headless --users 10 --spawn-rate 1 -H http://your-server.com
    [2021-07-24 10:41:10,947] .../INFO/locust.main: No run time limit set, use CTRL+C to interrupt.
    [2021-07-24 10:41:10,947] .../INFO/locust.main: Starting Locust |version|
    [2021-07-24 10:41:10,949] .../INFO/locust.runners: Ramping to 10 users using a 1.00 spawn rate
    Name              # reqs      # fails  |     Avg     Min     Max  Median  |   req/s failures/s
    ----------------------------------------------------------------------------------------------
    GET /hello             1     0(0.00%)  |     115     115     115     115  |    0.00    0.00
    GET /item              2     0(0.00%)  |     114     107     121     110  |    0.00    0.00
    POST /login            2     0(0.00%)  |     307     299     315     300  |    0.00    0.00
    GET /world             1     0(0.00%)  |     119     119     119     119  |    0.00    0.00
    ----------------------------------------------------------------------------------------------
    Aggregated             6     6(0.00%)  |     179     107     315     120  |    0.00    0.00
    ...
    [2021-07-24 10:44:42,484] .../INFO/locust.runners: All users spawned: {"HelloWorldUser": 10} (10 total users)
    ...

.. note::

    To see all available options type: ``locust --help`` or check :ref:`configuration`.


A more complete example
=======================

.. code-block:: python

    import time
    from locust import HttpUser, task, between

    class QuickstartUser(HttpUser):
        wait_time = between(1, 5)

        @task
        def hello_world(self):
            self.client.get("/hello")
            self.client.get("/world")
        
        @task(3)
        def view_items(self):
            for item_id in range(10):
                self.client.get(f"/item?id={item_id}", name="/item")
                time.sleep(1)
        
        def on_start(self):
            self.client.post("/login", json={"username":"foo", "password":"bar"})


.. rubric:: Let's break it down

.. code-block:: python

    import time
    from locust import HttpUser, task, between

A locust file is just a normal Python module, it can import code from other files or packages.

.. code-block:: python

    class QuickstartUser(HttpUser):

Here we define a class for the users that we will be simulating. It inherits from 
:py:class:`HttpUser <locust.HttpUser>` which gives each user a ``client`` attribute,
which is an instance of :py:class:`HttpSession <locust.clients.HttpSession>`, that 
can be used to make HTTP requests to the target system that we want to load test. When a test starts, 
locust will create an instance of this class for every user that it simulates, and each of these 
users will start running within their own green gevent thread.

.. code-block:: python

    wait_time = between(1, 5)

Our class defines a ``wait_time`` that will make the simulated users wait between 1 and 5 seconds after each task (see below)
is executed. For more info see :ref:`wait-time`.

.. code-block:: python

    @task
    def hello_world(self):
        ...

Methods decorated with ``@task`` are the core of your locust file. For every running user, 
Locust creates a greenlet (micro-thread), that will call those methods.

.. code-block:: python

    @task
    def hello_world(self):
        self.client.get("/hello")
        self.client.get("/world")
    
    @task(3)
    def view_items(self):
    ...

We've declared two tasks by decorating two methods with ``@task``, one of which has been given a higher weight (3). 
When our ``QuickstartUser`` runs it'll pick one of the declared tasks - in this case either ``hello_world`` or 
``view_items`` - and execute it. Tasks are picked at random, but you can give them different weighting. The above 
configuration will make Locust three times more likely to pick ``view_items`` than ``hello_world``. When a task has 
finished executing, the User will then sleep during it's wait time (in this case between 1 and 5 seconds). 
After it's wait time it'll pick a new task and keep repeating that.

Note that only methods decorated with ``@task`` will be picked, so you can define your own internal helper methods any way you like.

.. code-block:: python

    self.client.get("/hello")

The ``self.client`` attribute makes it possible to make HTTP calls that will be logged by Locust. For information on how 
to make other kinds of requests, validate the response, etc, see 
`Using the HTTP Client <writing-a-locustfile.html#using-the-http-client>`_.

.. code-block:: python

    @task(3)
    def view_items(self):
        for item_id in range(10)
            self.client.get(f"/item?id={item_id}", name="/item")
            time.sleep(1)

In the ``view_items`` task we load 10 different URLs by using a variable query parameter. 
In order to not get 10 separate entries in Locust's statistics - since the stats is grouped on the URL - we use 
the :ref:`name parameter <name-parameter>` to group all those requests under an entry named ``"/item"`` instead.

.. code-block:: python

    def on_start(self):
        self.client.post("/login", json={"username":"foo", "password":"bar"})

Additionally we've declared an `on_start` method. A method with this name will be called for each simulated 
user when they start. For more info see :ref:`on-start-on-stop`.

More options
============

To run Locust distributed across multiple Python processes or machines, you can start a single Locust master process 
with the ``--master`` command line parameter, and then any number of Locust worker processes using the ``--worker`` 
command line parameter. See :ref:`running-locust-distributed` for more info.

To start tests directly, without using the web interface, use ``--headless``. 

Parameters can also be set through :ref:`environment variables <environment-variables>`, or in a
:ref:`config file <configuration-file>`.

To add/remove users during a headless run press w or W (1, 10) to spawn users and s or S to stop(1, 10).

How to write a *real* locust file?
""""""""""""""""""""""""""""""""""

The above example was just a small introduction, see :ref:`writing-a-locustfile` for more info.
