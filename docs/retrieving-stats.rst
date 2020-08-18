======================================
Retrieve test statistics in CSV format
======================================

You may wish to consume your Locust results via a CSV file. In this case, there are two ways to do this.

First, when running Locust with the web UI, you can retrieve CSV files under the Download Data tab. 

Secondly, you can run Locust with a flag which will periodically save three CSV files. This is particularly useful
if you plan on running Locust in an automated way with the ``--headless`` flag:

.. code-block:: console

    $ locust -f examples/basic.py --csv=example --headless -t10m

The files will be named ``example_stats.csv``, ``example_failures.csv`` and ``example_history.csv``
(when using ``--csv=example``). The first two files will contain the stats and failures for the whole 
test run, with a row for every stats entry (URL endpoint) and an aggregated row. The ``example_history.csv`` 
will get new rows with the *current* (10 seconds sliding window) stats appended during the whole test run. 
By default only the Aggregate row is appended regularly to the history stats, but if Locust is started with 
the ``--csv-full-history`` flag, a row for each stats entry (and the Aggregate) is appended every time 
the stats are written (once every 2 seconds by default).

You can also customize how frequently this is written if you desire faster (or slower) writing:

.. code-block:: python

    import locust.stats
    locust.stats.CSV_STATS_INTERVAL_SEC = 5 # default is 1 second
    locust.stats.CSV_STATS_FLUSH_INTERVAL_SEC = 60 # Determines how often the data is flushed to disk, default is 10 seconds
