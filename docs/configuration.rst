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
environment variables.

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
    hatch-rate = 10
    run-time = 10m
    

.. code-block:: console

    $ locust --config=master.conf

.. note::

    Configuration values are read (overridden) in the following order:
    
    .. code-block::
        
        ~/locust.conf -> ./locust.conf -> (file specified using --conf) -> env vars -> cmd args

All available configuration options
-----------------------------------

Here's a table of all the available configuration options, and their corresponding Environment and config file keys:

.. include:: config-options.rst
