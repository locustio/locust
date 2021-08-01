.. _running-without-web-ui:

=================================
Running without the web UI
=================================

You can run locust without the web UI - for example if you want to run it in some automated flow, 
like a CI server - by using the ``--headless`` flag together with ``-u`` and ``-r``:

.. code-block:: console

    $ locust -f locust_files/my_locust_file.py --headless -u 1000 -r 100

``-u`` specifies the number of Users to spawn, and ``-r`` specifies the spawn rate
(number of users to start per second).

While the test is running you can change the user count manually, even after ramp up has finished. Pressing w to add 1 user or W to add 10. Press s to remove 1 or S to remove 10.

Setting a time limit for the test
---------------------------------

If you want to specify the run time for a test, you can do that with ``--run-time`` or ``-t``:

.. code-block:: console

    $ locust -f --headless -u 1000 -r 100 --run-time 1h30m

Locust will shutdown once the time is up.


Allow tasks to finish their iteration on shutdown
-------------------------------------------------

By default, locust will stop your tasks immediately (without even waiting for requests to finish). 
If you want to allow your tasks to finish their iteration, you can use ``--stop-timeout <seconds>``.

.. code-block:: console

    $ locust -f --headless -u 1000 -r 100 --run-time 1h30m --stop-timeout 99

.. _running-locust-distributed-without-web-ui:


Running Locust distributed without the web UI
---------------------------------------------

If you want to :ref:`run Locust distributed <running-locust-distributed>` without the web UI, 
you should specify the ``--expect-workers`` option when starting the master node, to specify
the number of worker nodes that are expected to connect. It will then wait until that many worker
nodes have connected before starting the test.


Controlling the exit code of the Locust process
-----------------------------------------------

When running Locust in a CI environment, you might want to control the exit code of the Locust 
process. You can do that in your test scripts by setting the 
:py:attr:`process_exit_code <locust.env.Environment.process_exit_code>` of the 
:py:class:`Environment <locust.env.Environment>` instance.

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

(this code could go into the locustfile.py or in any other file that is imported in the locustfile)
