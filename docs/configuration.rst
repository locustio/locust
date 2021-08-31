.. _configuration:

Configuration
=============


Command Line Options
-----------------------------

Locust is configured mainly through command line arguments.

.. code-block:: console

    $ locust --help

.. literalinclude:: cli-help-output.txt
    :language: console



.. _environment-variables:

Environment Variables
---------------------

Most of the options that can be set through command line arguments can also be set through 
environment variables. Example:

.. code-block::

    $ LOCUST_LOCUSTFILE=custom_locustfile.py locust


.. _configuration-file:

Configuration File
------------------

Any of the options that can be set through command line arguments can also be set by a
configuration file in the `config file <https://github.com/bw2/ConfigArgParse#config-file-syntax>`_
format. 

Locust will look for ``~/.locust.conf`` and ``./locust.conf`` by default, and you can specify an 
additional file using the ``--config`` flag.

Example:

.. code-block::

    # master.conf in current directory
    locustfile = locust_files/my_locust_file.py
    headless = true
    master = true
    expect-workers = 5
    host = http://target-system
    users = 100
    spawn-rate = 10
    run-time = 10m
    

.. code-block:: console

    $ locust --config=master.conf

.. note::

    Configuration values are read (overridden) in the following order:
    
    .. code-block:: console
        
        ~/locust.conf -> ./locust.conf -> (file specified using --conf) -> env vars -> cmd args

All available configuration options
-----------------------------------

Here's a table of all the available configuration options, and their corresponding Environment and config file keys:

.. include:: config-options.rst

Custom arguments
----------------

See :ref:`parametrizing-locustfiles`

Customization of statistics settings
------------------------------------

Default configuration for Locust statistics is set in constants of stats.py file.
It can be tuned to specific requirements by overriding these values.
To do this, import locust.stats module and override required settings

.. code-block:: python

    import locust.stats
    locust.stats.CONSOLE_STATS_INTERVAL_SEC = 15

It can be done directly in Locust file or extracted to separate file for common usage by all Locust files.

The list of statistics parameters that can be modified is:

+-------------------------------------------+--------------------------------------------------------------------------------------+
| Parameter name                            | Purpose                                                                              |
+-------------------------------------------+--------------------------------------------------------------------------------------+
| STATS_NAME_WIDTH                          | Width of column for request name in console output                                   |
+-------------------------------------------+--------------------------------------------------------------------------------------+
| STATS_TYPE_WIDTH                          | Width of column for request type in console output                                   |
+-------------------------------------------+--------------------------------------------------------------------------------------+
| CSV_STATS_INTERVAL_SEC                    | Interval for how frequently the CSV file is written if this option is configured     |
+-------------------------------------------+--------------------------------------------------------------------------------------+
| CONSOLE_STATS_INTERVAL_SEC                | Interval for how frequently results are written to console                           |
+-------------------------------------------+--------------------------------------------------------------------------------------+
| CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW   | Window size/resolution - in seconds - when calculating the current response          |
|                                           | time percentile                                                                      |
+-------------------------------------------+--------------------------------------------------------------------------------------+
| PERCENTILES_TO_REPORT                     | The list of response time percentiles to be calculated & reported                    |
+-------------------------------------------+--------------------------------------------------------------------------------------+

