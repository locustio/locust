.. _logging:

=======
Logging
=======

Locust uses Python's `built in logging framework <https://docs.python.org/3/library/logging.html>`_ for 
handling logging.

The default logging configuration that Locust applies, writes log messages directly to stderr. ``--loglevel`` 
and ``--logfile`` can be used to change the verbosity and/or make the log go to a file instead. 

The default logging configuration installs handlers for the ``root`` logger as well as the ``locust.*`` loggers, 
so using the root logger in your own test scripts will put the message into the log file if ``--logfile`` is used:

.. code-block:: python
    
    import logging
    logging.info("this log message will go wherever the other locust log messages go")


It's also possible to control the whole logging configuration in your own test scripts by using the 
``--skip-log-setup`` option. You will then have to 
`configure the logging <https://docs.python.org/3/library/logging.config.html>`_ yourself.


Options
=======

``--skip-log-setup``
--------------------

Disable Locust's logging setup. Instead, the configuration is provided by the Locust test or Python defaults.


``--loglevel``
--------------

Choose between DEBUG/INFO/WARNING/ERROR/CRITICAL. Default is INFO. The short-hand version is ``-L``.


``--logfile``
-------------

Path to log file. If not set, log will go to stdout/stderr.


Locust loggers
==============

Here's a table of the loggers used within Locust (for reference when configuring logging settings manually):

+------------------------+--------------------------------------------------------------------------------------+
| Logger name            | Purpose                                                                              |
+------------------------+--------------------------------------------------------------------------------------+
| locust                 | The locust namespace is used for all loggers such as ``locust.main``,                |
|                        | ``locust.runners``, etc.                                                             |
+------------------------+--------------------------------------------------------------------------------------+
| locust.stats_logger    | This logger is used to periodically print the current stats to the console. The      |
|                        | stats does *not* go into the log file when ``--logfile`` is used by default.         |
+------------------------+--------------------------------------------------------------------------------------+
