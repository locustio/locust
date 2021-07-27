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
If you want to contribute to the Locust project, fork it on `Github <https://github.com/locustio/locust/>`_, clone the repo and then install it in editable mode:

.. code-block:: console

    $ git clone git://github.com/<your name>/locust.git
    $ pip3 install -e locust/

Now the ``locust`` command will run *your* code with no need for reinstalling after making changes.
