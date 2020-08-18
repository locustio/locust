.. _installation:

Installation
============

`Install Python <https://docs.python-guide.org/starting/installation/>`_ 3.6 or later.

Install Locust using pip.

.. code-block:: console

    $ pip3 install locust

Validate your installation and show the Locust version number:

.. code-block:: console

    $ locust -V

If everything worked, move on to :ref:`quickstart`. If it did not, check out `the wiki <https://github.com/locustio/locust/wiki/Installation>`_ for some solutions.

Bleeding edge version
---------------------
If you need some feature or fix not yet part of a release:

.. code-block:: console

    $ pip3 install -e git://github.com/locustio/locust.git@master#egg=locust