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

Bleeding edge version
---------------------
If you need some feature or fix not yet part of a release:

.. code-block:: console

    $ pip3 install -e git://github.com/locustio/locust.git@master#egg=locust

Install for development
-----------------------

If you want to modify Locust or contribute to the project, see :ref:`developing-locust`.
