.. _configuration:

Configuration
=============


Command Line Options
-----------------------------

The most straight forward way to Configure how Locust is run is through command line arguments. 

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

Locust will look for ``locust.conf`` or ``~/.locust.conf`` by default, or a file may be specified
with the ``--config`` flag. Parameters passed as environment variables will override the settings 
from the config file, and command line arguments will override the settings from both environment 
variables and config file.

Example:

.. code-block::

    # master.conf in current directory
    locustfile = locust_files/my_locust_file.py
    headless = true
    master = true
    expect-workers = 5
    host = http://target-system
    users = 100
    hatch-rate = 10
    run-time = 10m
    

.. code-block:: console

    $ locust --config=master.conf


All available configuration options
-----------------------------------

Here's a table of all the available configuration options, and their corresponding Environment and config file keys:

.. include:: config-options.rst
