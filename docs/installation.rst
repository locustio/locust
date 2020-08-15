Installation
============

`Install Python <https://docs.python-guide.org/starting/installation/>`_ 3.6 or later.

Install Locust using pip.

.. code-block:: console

    $ pip3 install locust

Validate your installation and show the Locust version number:

.. code-block:: console

    $ locust -V

If everything worked, move on to :ref:`quickstart`, otherwise continue reading.

Windows
-------
If you have issues installing, check https://stackoverflow.com/questions/61592069/locust-is-not-installing-on-my-windows-10-for-load-testing

Running Locust on Windows should work fine for developing and testing your
scripts. But when running large scale tests you should use a Linux machine, as Locust's performance is better there.


Increasing Maximum Number of Open Files Limit
---------------------------------------------

Every User/HTTP connection from Locust opens a new file (technically a file descriptor).
Many operating systems by default set a low limit for the maximum number of files that 
can be open at the same time.

Locust will try to adjust this automatically for you, but in a lot of cases your 
operating system will not allow it (in which case you will get a warning in the log), 
so you need to do it manually. How to do this depends on your operating system you might find some useful information `here <https://www.tecmint.com/increase-set-open-file-limits-in-linux/>`_.

Bleeding edge version
---------------------
If you need some feature/fix not yet part of a release:

.. code-block:: console

    $ pip3 install -e git://github.com/locustio/locust.git@master#egg=locust