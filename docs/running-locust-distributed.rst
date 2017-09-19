.. _running-locust-distributed:

===========================
Running Locust distributed
===========================

Once a single machine isn't enough to simulate the number of users that you need, Locust supports 
running load tests distributed across multiple machines. 

To do this, you start one instance of Locust in master mode using the ``--master`` flag. This is 
the instance that will be running Locust's web interface where you start the test and see live 
statistics. The master node doesn't simulate any users itself. Instead you have to start one or 
—most likely—multiple slave Locust nodes using the ``--slave`` flag, together with the 
``--master-host`` (to specify the IP/hostname of the master node).

A common set up is to run a single master on one machine, and then run one slave instance per 
processor core, on the slave machines.

.. note::
    Both the master and each slave machine, must have a copy of the locust test scripts 
    when running Locust distributed.


Example
=======

To start locust in master mode::

    locust -f my_locustfile.py --master

And then on each slave (replace ``192.168.0.14`` with IP of the master machine)::

    locust -f my_locustfile.py --slave --master-host=192.168.0.14


Options
=======

``--master``
------------

Sets locust in master mode. The web interface will run on this node.


``--slave``
-----------

Sets locust in slave mode.


``--master-host=X.X.X.X``
-------------------------

Optionally used together with ``--slave`` to set the hostname/IP of the master node (defaults 
to 127.0.0.1)

``--master-port=5557``
----------------------

Optionally used together with ``--slave`` to set the port number of the master node (defaults to 5557). 
Note that locust will use the port specified, as well as the port number +1. So if 5557 is used, locust 
will use both port 5557 and 5558.

``--master-bind-host=X.X.X.X``
------------------------------

Optionally used together with ``--master``. Determines what network interface that the master node 
will bind to. Defaults to * (all available interfaces).

``--master-bind-port=5557``
------------------------------

Optionally used together with ``--master``. Determines what network ports that the master node will
listen to. Defaults to 5557. Note that locust will use the port specified, as well as the port 
number +1. So if 5557 is used, locust will use both port 5557 and 5558.

``--expect-slaves=X``
---------------------

Used when starting the master node with ``--no-web``. The master node will then wait until X slave 
nodes has connected before the test is started.


Running Locust distributed without the web UI
=============================================

See :ref:`running-locust-distributed-without-web-ui`
