.. _running-without-web-ui:

=================================
Running without the web UI
=================================

You can run locust without the web UI by using the ``--headless`` flag together with ``-u/--users`` and ``-r/--spawn-rate``:

.. code-block:: console
    :substitutions:

    $ locust -f locust_files/my_locust_file.py --headless -u 100 -r 5
    [2021-07-24 10:41:10,947] .../INFO/locust.main: No run time limit set, use CTRL+C to interrupt.
    [2021-07-24 10:41:10,947] .../INFO/locust.main: Starting Locust |version|
    [2021-07-24 10:41:10,949] .../INFO/locust.runners: Ramping to 100 users using a 5.00 spawn rate
    Name              # reqs      # fails  |     Avg     Min     Max  Median  |   req/s failures/s
    ----------------------------------------------------------------------------------------------
    GET /hello             1     0(0.00%)  |     115     115     115     115  |    0.00    0.00
    GET /world             1     0(0.00%)  |     119     119     119     119  |    0.00    0.00
    ----------------------------------------------------------------------------------------------
    Aggregated             2     0(0.00%)  |     117     115     119     117  |    0.00    0.00
    (...)
    [2021-07-24 10:44:42,484] .../INFO/locust.runners: All users spawned: {"HelloWorldUser": 100} (100 total users)
    (...)

Even in headless mode you can change the user count while the test is running. Press ``w`` to add 1 user or ``W`` to add 10. Press ``s`` to remove 1 or ``S`` to remove 10.

Setting a time limit for the test
---------------------------------

To specify the run time for a test, use ``-t/--run-time``:

.. code-block:: console

    $ locust --headless -u 100 --run-time 1h30m
    $ locust --headless -u 100 --run-time 60 # default unit is seconds

Locust will shut down once the time is up. Time is calculated from the start of the test (not from when ramp up has finished).


Allow tasks to finish their iteration on shutdown
-------------------------------------------------

By default, Locust will stop your tasks immediately (without even waiting for requests to finish). 
To give running tasks some time to finish their iteration, use ``-s/--stop-timeout``:

.. code-block:: console

    $ locust --headless --run-time 1h30m --stop-timeout 10s

.. _running-distributed-without-web-ui:


Running Locust distributed without the web UI
---------------------------------------------

If you want to :ref:`run Locust distributed <running-distributed>` without the web UI, 
you should specify the ``--expect-workers`` option when starting the master node, to specify
the number of worker nodes that are expected to connect. It will then wait until that many worker
nodes have connected before starting the test.


Controlling the exit code of the Locust process
-----------------------------------------------

By default the locust process will give an exit code of 1 if there were any failed samples 
(use the ``--exit-code-on-error`` to change that behaviour).

You can also manually control the exit code in your test scripts by setting the :py:attr:`process_exit_code <locust.env.Environment.process_exit_code>` of the 
:py:class:`Environment <locust.env.Environment>` instance. This is particularly useful when running Locust as an automated/scheduled test, for example as part of a CI pipeline.

Below is an example that'll set the exit code to non zero if any of the following conditions are met:

* More than 1% of the requests failed
* The average response time is longer than 200 ms
* The 95th percentile for response time is larger than 800 ms

.. code-block:: python

    import logging
    from locust import events
    
    @events.quitting.add_listener
    def _(environment, **kw):
        if environment.stats.total.fail_ratio > 0.01:
            logging.error("Test failed due to failure ratio > 1%")
            environment.process_exit_code = 1
        elif environment.stats.total.avg_response_time > 200:
            logging.error("Test failed due to average response time ratio > 200 ms")
            environment.process_exit_code = 1
        elif environment.stats.total.get_response_time_percentile(0.95) > 800:
            logging.error("Test failed due to 95th percentile response time > 800 ms")
            environment.process_exit_code = 1
        else:
            environment.process_exit_code = 0

Note that this code could go into the locustfile.py or in any other file that is imported in the locustfile.
