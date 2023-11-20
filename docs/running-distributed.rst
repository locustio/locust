.. _running-distributed:

===========================
Distributed load generation
===========================

A single process running Locust can simulate a reasonably high throughput. For a simple test plan it should be able to make many hundreds of requests per second, thousands if you use :ref:`FastHttpUser <increase-performance>`.

But if your test plan is complex or you want to run even more load, you'll need to scale out to multiple processes, maybe even multiple machines.

To do this, you start one instance of Locust in master mode using the ``--master`` flag and multiple worker instances using the ``--worker`` flag. If the workers are not on the same machine as the master you use ``--master-host`` to point them to the IP/hostname of the machine running the master.

To make this easier, you can use the ``--processes`` flag to launch multiple instances. It will launch a master process and the specified number of worker processes. Used in combination with ``--worker`` it will only launch the workers.

The master instance runs Locust's web interface, and tells the workers when to spawn/stop Users. The workers run your Users and send statistics back to the master. The master instance doesn't run any Users itself.

Both the master and worker machines must have a copy of the locustfile when running Locust distributed.

.. note::
    Because Python cannot fully utilize more than one core per process (see `GIL <https://realpython.com/python-gil/>`_), you will need to run **one worker instance per processor core** in order to have access to all your computing power.

.. note::
    There is almost no limit to how many *Users* you can run per worker. Locust/gevent can run thousands or even tens of thousands of Users per process just fine, as long as their total request rate/RPS is not too high.

.. note::
    If Locust is getting close to running out of CPU resources, it will log a warning. If there is no warning, you can be pretty sure your test is not limited by load generator CPU.

.. note::
    ``--processes`` was introduced in Locust 2.19. Child processes are launched using fork which is not available in Windows.

Example 1: Everything on one machine
====================================

It is really simple to launch a master and 4 worker processes::

    locust --processes 4

You can even auto-detect the number of cores in your machine and launch one worker for each of them::

    locust --processes -1

Example 2: Multiple machines
============================

Start locust in master mode::

    locust -f my_locustfile.py --master

And then on each worker machine (replace ``192.168.0.14`` with the IP of the master machine)::

    locust -f my_locustfile.py --worker --master-host=192.168.0.14 --processes 4

Note that both master and worker nodes need access to the locustfile, it is not sent from master to worker automatically. But you can use `locust-swarm <https://github.com/SvenskaSpel/locust-swarm>`_ for that.

Options
=======

``--master-host=X.X.X.X``
-------------------------

Optionally used together with ``--worker`` to set the hostname/IP of the master node (defaults
to 127.0.0.1)

``--master-port=5557``
----------------------

Optionally used together with ``--worker`` to set the port number of the master node (defaults to 5557).

``--master-bind-host=X.X.X.X``
------------------------------

Optionally used together with ``--master``. Determines which network interface the master node
will bind to. Defaults to * (all available interfaces).

``--master-bind-port=5557``
------------------------------

Optionally used together with ``--master``. Determines what network ports that the master node will
listen to. Defaults to 5557.

``--expect-workers=X``
----------------------

Used when starting the master node with ``--headless``. The master node will then wait until X worker
nodes has connected before the test is started.

Communicating across nodes
=============================================

When running Locust in distributed mode, you may want to communicate between master and worker nodes in 
order to coordinate data. This can be easily accomplished with custom messages using the built in messaging hooks:

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
