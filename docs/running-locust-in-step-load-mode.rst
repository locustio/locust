.. _running-locust-in-step-load-mode:

=================================
Running Locust in Step Load Mode
=================================

If you want to monitor your service performance with different user load and probe the max tps that can be achieved, you can run Locust with Step Load enabled with ``--step-load``:

.. code-block:: console

    $ locust -f locust_files/my_locust_file.py --step-load


Options
=======

``--step-load``
----------------

Enable Step Load mode to monitor how performance metrics varies when user load increases.


``--step-users``
-------------------

Client count to increase by step in Step Load mode. Only used together with ``--step-load``.


``--step-time``
-------------------------

Step duration in Step Load mode, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with ``--step-load``.


Running Locust in step load mode without the web UI
----------------------------------------------------

If you want to run Locust in step load mode without the web UI, you can do that with ``--step-users`` and ``--step-time``:

.. code-block:: console

    $ locust -f --headless -u 1000 -r 100 --run-time 1h30m --step-load --step-users 300 --step-time 20m

Locust will swarm the clients by step and shutdown once the time is up.


Running Locust distributed in step load mode
---------------------------------------------

If you want to :ref:`run Locust distributed <running-locust-distributed>` in step load mode, 
you should specify the ``--step-load`` option when starting the master node, to swarm locusts by step. It will then show the ``--step-users`` option and ``--step-time`` option in Locust UI.

