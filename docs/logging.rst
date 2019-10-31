.. _logging:

=======
Logging
=======

Locust comes with a basic logging configuration that optionally takes ``--loglevel`` and/or ``--logfile`` to modify the configuration. If you want to control the logging configuration you can supply the ``--skip-log-setup`` flag, which ignores the other parameters.

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

