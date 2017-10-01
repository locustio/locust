======================================
Retrieve test statistics in CSV format
======================================

You may wish to consume your Locust results via a CSV file. In this case, there are two ways to do this.

First, when running Locust with the web UI, you can retrieve CSV files under the Download Data tab. 

Secondly, you can run Locust with a flag which will periodically save the CSV file. This is particularly useful
if you plan on running Locust in an automated way with the ``--no-web`` flag::

    locust -f locust_files/my_locust_file.py --csv=foobar --no-web -n10 -t10m

or for v0.8 (where the ``-t`` option isn't available)::

    locust -f locust_files/my_locust_file.py --csv=foobar --no-web -n10 -c10

You can also customize how frequently this is written if you desire faster (or slower) writing::

    import locust.stats
    locust.stats.CSV_STATS_INTERVAL_SEC = 5 # default is 2 seconds
