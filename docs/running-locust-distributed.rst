.. _running-locust-distributed:

===========================
Distributed load generation
===========================

Once a single machine isn't enough to simulate the number of users that you need, Locust supports
running load tests distributed across multiple machines.

To do this, you start one instance of Locust in master mode using the ``--master`` flag. This is
the instance that will be running Locust's web interface where you start the test and see live
statistics. The master node doesn't simulate any users itself. Instead you have to start one or
-most likely-multiple worker Locust nodes using the ``--worker`` flag, together with the
``--master-host`` (to specify the IP/hostname of the master node).

A common set up is to run a single master on one machine, and then run **one worker instance per
processor core** on the worker machines.

.. note::
    Both the master and each worker machine, must have a copy of the locust test scripts
    when running Locust distributed.

.. note::
    It's recommended that you start a number of simulated users that are greater  than
    ``number of user classes * number of workers`` when running Locust distributed.

    Otherwise - due to the current implementation -
    you might end up with a distribution of the  User classes that doesn't correspond to the
    User classes' ``weight`` attribute. And if the spawn rate is lower than the number of worker
    nodes, the spawning would occur in "bursts" where all worker nodes would spawn a single user and
    then sleep for multiple seconds, spawn another user, sleep and repeat.


Example
=======

To start locust in master mode::

    locust -f my_locustfile.py --master

And then on each worker (replace ``192.168.0.14`` with the IP of the master machine, or leave out the parameter altogether if your workers are on the same machine as the master)::

    locust -f my_locustfile.py --worker --master-host=192.168.0.14


Options
=======

``--master``
------------

Sets locust in master mode. The web interface will run on this node.


``--worker``
------------

Sets locust in worker mode.


``--master-host=X.X.X.X``
-------------------------

Optionally used together with ``--worker`` to set the hostname/IP of the master node (defaults
to 127.0.0.1)

``--master-port=5557``
----------------------

Optionally used together with ``--worker`` to set the port number of the master node (defaults to 5557).

``--master-bind-host=X.X.X.X``
------------------------------

Optionally used together with ``--master``. Determines what network interface that the master node
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

    # Fired when the worker recieves a message of type 'test_users'
    def setup_test_users(environment, msg, **kwargs):
        for user in msg.data:
            print(f"User {user['name']} recieved")
        environment.runner.send_message('acknowledge_users', f"Thanks for the {len(msg.data)} users!")

    # Fired when the master recieves a message of type 'acknowledge_users'
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
        if not isinstance(environment.runner, MasterRunner):
            users = [
                {"name": "User1"},
                {"name": "User2"},
                {"name": "User3"},
            ]
            environment.runner.send_message('test_users', users)  

Note that when running locally (i.e. non-distributed), this functionality will be preserved; 
the messages will simply be handled by the same runner that sends them.  

A more complete example can be found in the `examples directory <https://github.com/locustio/locust/tree/master/examples>`_ of the Locust 
source code.


Running distributed with Docker
=============================================

See :ref:`running-locust-docker`


Running Locust distributed without the web UI
=============================================

See :ref:`running-locust-distributed-without-web-ui`


Increase Locust's performance
=============================

If you're planning to run large-scale load tests you might be interested to use the alternative
HTTP client that's shipped with Locust. You can read more about it here: :ref:`increase-performance`
