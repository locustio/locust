Installation
============

`Install Python <https://docs.python-guide.org/starting/installation/>`_ 3.6 or later.

Install Locust using pip.

.. code-block:: console

    $ pip3 install locust

To validate your installation and see available options, run:

.. code-block:: console

    $ locust --help

If you get an error saying the command *locust* is not available, make sure your Python script directory is in your PATH variable. If everything worked, move on to :ref:`quickstart`.

Windows
-------
If you have issues installing, check https://stackoverflow.com/questions/61592069/locust-is-not-installing-on-my-windows-10-for-load-testing

Running Locust on Windows should work fine for developing and testing your
scripts. However, when running large scale tests, it's recommended that you do that on
Linux machines, as gevent's performance under Windows is not very good.

Bleeding edge version
---------------------
For those who absolutely need some feature not yet part of a release:

.. code-block:: console

    $ pip3 install -e git://github.com/locustio/locust.git@master#egg=locust

Increasing Maximum Number of Open Files Limit
---------------------------------------------

Every User/HTTP connection from Locust opens a new file (technically a file descriptor).
Many operating systems by default set a low limit for the maximum number of files that 
can be open at the same time.

Locust will try to adjust this automatically for you, but in a lot of cases your 
operating system will not allow it (in which case you will get a warning in the log), 
so you'll need to do it yourself.

How to do this depends on your operating system, but for Linux you might find some useful information `here <https://www.tecmint.com/increase-set-open-file-limits-in-linux/>`_.
