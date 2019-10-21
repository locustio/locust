======================================
Retrieve test statistics in CSV format
======================================

You may wish to consume your Locust results via a CSV file. In this case, there are two ways to do this.

First, when running Locust with the web UI, you can retrieve CSV files under the Download Data tab. 

Secondly, you can run Locust with a flag which will periodically save two CSV files. This is particularly useful
if you plan on running Locust in an automated way with the ``--no-web`` flag:

.. code-block:: console

    $ locust -f examples/basic.py --csv=example --no-web -t10m

The files will be named ``example_distribution.csv`` and ``example_requests.csv`` (when using ``--csv=example``) and mirror Locust's built in stat pages.

You can also customize how frequently this is written if you desire faster (or slower) writing:

.. code-block:: python

    import locust.stats
    locust.stats.CSV_STATS_INTERVAL_SEC = 5 # default is 2 seconds

This data will write two files with ``_distribution.csv`` and ``_requests.csv`` added to the name you give:

.. code-block:: console

    $ cat example_distribution.csv
    "Name","# requests","50%","66%","75%","80%","90%","95%","98%","99%","100%"
    "GET /",31,4,4,4,4,4,4,4,4,4
    "/does_not_exist",0,"N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"
    "GET /stats/requests",38,3,4,4,4,4,5,5,5,5
    "None Total",69,3,4,4,4,4,4,5,5,5

and:

.. code-block:: console

    $ cat example_requests.csv
    "Method","Name","# requests","# failures","Median response time","Average response time","Min response time","Max response time","Average Content Size","Requests/s"
    "GET","/",51,0,4,3,2,6,12274,0.89
    "GET","/does_not_exist",0,56,0,0,0,0,0,0.00
    "GET","/stats/requests",58,0,3,3,2,5,1214,1.01
    "None","Total",109,56,3,3,2,6,6389,1.89
