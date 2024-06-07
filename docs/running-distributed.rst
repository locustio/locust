.. _running-distributed:

===========================
Distributed load generation
===========================

A single process running Locust can simulate a reasonably high throughput. For a simple test plan and small payloads it can make more than a thousand requests per second, possibly over ten thousand if you use :ref:`FastHttpUser <increase-performance>`.

But if your test plan is complex or you want to run even more load, you'll need to scale out to multiple processes, maybe even multiple machines. Fortunately, Locust supports distributed runs out of the box.

To do this, you start one instance of Locust with the ``--master`` flag and one or more using the ``--worker`` flag. The master instance runs Locust's web interface, and tells the workers when to spawn/stop Users. The worker instances run your Users and send statistics back to the master. The master instance doesn't run any Users itself.

To simplify startup, you can use the ``--processes`` flag. It will launch a master process and the specified number of worker processes. It can also be used in combination with ``--worker``, then it will only launch workers. This feature relies on `fork() <https://linux.die.net/man/3/fork>`_ so it doesn't work on Windows.

.. note::
    Because Python cannot fully utilize more than one core per process (see `GIL <https://realpython.com/python-gil/>`_), you need to run one worker instance per processor core in order to have access to all your computing power.

.. note::
    There is almost no limit to how many Users you can run per worker. Locust/gevent can run thousands or even tens of thousands of Users per process just fine, as long as their total request rate (RPS) is not too high.

    If Locust *is* getting close to running out of CPU resources, it will log a warning. If there is no warning but you are still unable to generate the expected load, then the problem must be :ref:`increaserr`.

Single machine
==============

It is really simple to launch a master and 4 worker processes::

    locust --processes 4

You can even auto-detect the number of logical cores in your machine and launch one worker for each of them::

    locust --processes -1

Multiple machines
=================

Start locust in master mode on one machine::

    locust -f my_locustfile.py --master

And then on each worker machine:

.. code-block:: bash

    locust -f - --worker --master-host <your master> --processes 4

.. note::
    The ``-f -`` argument tells Locust to get the locustfile from master instead of from its local filesystem. This feature was introduced in Locust 2.23.0.

Multiple machines, using locust-swarm
=====================================

When you make changes to the locustfile you'll need to restart all Locust processes. `locust-swarm <https://github.com/SvenskaSpel/locust-swarm>`_ automates this for you. It also solves the issue of firewall/network access from workers to master using SSH tunnels (this is often a problem if the master is running on your workstation and workers are running in some datacenter).

.. code-block:: bash

    pip install locust-swarm

    swarm -f my_locustfile.py --loadgen-list worker-server1,worker-server2 <any other regular locust parameters>

See `locust-swarm <https://github.com/SvenskaSpel/locust-swarm>`_ for more details.

Options for distributed load generation
=======================================

``--master-host <hostname or ip>``
----------------------------------

Optionally used together with ``--worker`` to set the hostname/IP of the master node (defaults
to localhost)

``--master-port <port number>``
-------------------------------

Optionally used together with ``--worker`` to set the port number of the master node (defaults to 5557).

``--master-bind-host <ip>``
---------------------------

Optionally used together with ``--master``. Determines which network interface the master node
will bind to. Defaults to * (all available interfaces).

``--master-bind-port <port number>``
------------------------------------

Optionally used together with ``--master``. Determines what network ports that the master node will
listen to. Defaults to 5557.

``--expect-workers <number of workers>``
----------------------------------------

Used when starting the master node with ``--headless``. The master node will then wait until X worker
nodes has connected before the test is started.

Communicating across nodes
=============================================

When running Locust in distributed mode, you may want to communicate between master and worker nodes in 
order to coordinate the test. This can be easily accomplished with custom messages using the built in messaging hooks:

.. code-block:: python

    from locust import events
    from locust.runners import MasterRunner, WorkerRunner

    # Fired when the worker receives a message of type 'test_users'
    def setup_test_users(environment, msg, **kwargs):
        for user in msg.data:
            print(f"User {user['name']} received")
        environment.runner.send_message('acknowledge_users', f"Thanks for the {len(msg.data)} users!")

    # Fired when the master receives a message of type 'acknowledge_users'
    def on_acknowledge(msg, **kwargs):
        print(msg.data)

    @events.init.add_listener
    def on_locust_init(environment, **_kwargs):
        if not isinstance(environment.runner, MasterRunner):
            environment.runner.register_message('test_users', setup_test_users)
        if not isinstance(environment.runner, WorkerRunner):
            environment.runner.register_message('acknowledge_users', on_acknowledge)

    @events.test_start.add_listener
    def on_test_start(environment, **_kwargs):
        if not isinstance(environment.runner, WorkerRunner):
            users = [
                {"name": "User1"},
                {"name": "User2"},
                {"name": "User3"},
            ]
            environment.runner.send_message('test_users', users)  

Note that when running locally (i.e. non-distributed), this functionality will be preserved; 
the messages will simply be handled by the runner that sends them.

.. note::
    Using the default options while registering a message handler will run the listener function
    in a **blocking** way, resulting in the heartbeat and other messages being delayed for the amount
    of the execution.
    If you think that your message handler will need to run for more than a second then you can register it
    as **concurrent**. Locust will then make it run in its own greenlet. Note that these greenlets will never 
    be join():ed.

    .. code-block::

        environment.runner.register_message('test_users', setup_test_users, concurrent=True)

For more details, see the `complete example <https://github.com/locustio/locust/tree/master/examples/custom_messages.py>`_.


Running distributed with Docker
=============================================

See :ref:`running-in-docker`


Running Locust distributed without the web UI
=============================================

See :ref:`running-distributed-without-web-ui`


Increase Locust's performance
=============================

If you're planning to run large-scale load tests, you might be interested to use the alternative
HTTP client that's shipped with Locust. You can read more about it here: :ref:`increase-performance`.
