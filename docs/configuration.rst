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
