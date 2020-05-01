.. _configuration:

Configuration
=============


Command Line Options
-----------------------------

The most straight forward way to Configure how Locust is run is through command line options. 

.. code-block:: console

    $ locust --help

.. literalinclude:: cli-help-output.txt
    :language: console



.. _environment-variables:

Environment variables
---------------------

Most of the configuration that can be set through command line arguments can also be set through 
environment variables. Here's a table of all the available environment variables:

.. include:: env-options.rst



.. _configuration-files:

Configuration files
-------------------

Any of the configuration that can be set through command line arguments can also be set by a
configuration file in the `config file <https://github.com/bw2/ConfigArgParse#config-file-syntax>`_
format.
Locust will look for ``locust.conf`` or ``~/.locust.conf`` by default, or a file may be specified
with the ``--config`` flag. Parameters passed as command line arguments will override the settings
from the config file.


.. code-block::

    # step_mode.conf in current directory
    locustfile locust_files/my_locust_file.py
    host localhost
    users 100
    hatch-rate 10
    step-load
    step-users 20
    step-time 60

.. code-block:: console

    $ locust --config=step_mode.conf
