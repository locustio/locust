.. _running-locust-without-web-ui:

=================================
Running Locust without the web UI
=================================

You can run locust without the web UI - for example if you want to run it in some automated flow, 
like a CI server - by using the ``--headless`` flag together with ``-c`` and ``-r``:

.. code-block:: console

    $ locust -f locust_files/my_locust_file.py --headless -c 1000 -r 100

``-c`` specifies the number of Locust users to spawn, and ``-r`` specifies the hatch rate 
(number of users to spawn per second).


Setting a time limit for the test
---------------------------------

If you want to specify the run time for a test, you can do that with ``--run-time`` or ``-t``:

.. code-block:: console

    $ locust -f --headless -c 1000 -r 100 --run-time 1h30m

Locust will shutdown once the time is up.

Allow tasks to finish their iteration on shutdown
-------------------------------------------------

By default, locust will stop your tasks immediately. If you want to allow your tasks to finish their iteration, you can use ``--stop-timeout <seconds>``.

.. code-block:: console

    $ locust -f --headless -c 1000 -r 100 --run-time 1h30m --stop-timeout 99

.. _running-locust-distributed-without-web-ui:

Running Locust distributed without the web UI
---------------------------------------------

If you want to :ref:`run Locust distributed <running-locust-distributed>` without the web UI, 
you should specify the ``--expect-workers`` option when starting the master node, to specify
the number of worker nodes that are expected to connect. It will then wait until that many worker
nodes have connected before starting the test.

