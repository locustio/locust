.. _running-locust-without-web-ui:

=================================
Running Locust without the web UI
=================================

You can run locust without the web UI - for example if you want to run it in some automated flow, 
like a CI server - by using the ``--no-web`` flag together with ``-c`` and ``-r``::

    locust -f locust_files/my_locust_file.py --no-web -c 1000 -r 100
    
``-c`` specifies the number of Locust users to spawn, and ``-r`` specifies the hatch rate 
(number of users to spawn per second).


Setting a time limit for the test
---------------------------------

.. note::

    This is a new feature in v0.9. For 0.8 use ``-n`` to specify the number of requests

If you want to specify the run time for a test, you can do that with ``--run-time`` or ``-t``::

    locust -f --no-web -c 1000 -r 100 --run-time 1h30m

Locust will shutdown once the time is up.


.. _running-locust-distributed-without-web-ui:

Running Locust distributed without the web UI
---------------------------------------------

If you want to :ref:`run Locust distributed <running-locust-distributed>` without the web UI, 
you should specify the ``--expect-slaves`` option when starting the master node, to specify 
the number of slave nodes that are expected to connect. It will then wait until that many slave 
nodes have connected before starting the test.

