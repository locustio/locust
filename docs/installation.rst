.. _installation:

Installation
============

`Install Python <https://docs.python-guide.org/starting/installation/>`_ 3.6 or later, if you dont already have it.

Install Locust:

.. code-block:: console

    $ pip3 install locust

Validate your installation. If this doesnt work, `check the wiki <https://github.com/locustio/locust/wiki/Installation>`_ for some possible solutions.

.. code-block:: console
    :substitutions:

    $ locust -V
    locust |version|

Great! Now we're ready to create our first test: :ref:`quickstart`

Dev builds
----------
If you need the latest and greatest version of Locust and cannot wait for the next proper release, you can install a dev build like this:

.. code-block:: console

    $ pip3 install -U --pre locust

Dev builds are published every time a branch is merged into master.

Install for development
-----------------------

If you want to modify Locust or contribute to the project, see :ref:`developing-locust`.
