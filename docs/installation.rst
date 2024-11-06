.. _installation:

Installation
============

.. note::

    Check `Troubleshooting Installation`_ if you encounter issues.

0. `Install Python <https://docs.python-guide.org/starting/installation/>`_ (if you dont already have it)

1. Install Locust

.. code-block:: console

    $ pip3 install locust

2. Validate your installation

.. code-block:: console
    :substitutions:

    $ locust -V
    locust |version| from /usr/local/lib/python3.12/site-packages/locust (Python 3.12.5)


Using uvx (alternative)
-----------------------

0. `Install uv <https://github.com/astral-sh/uv?tab=readme-ov-file#installation>`_

1. Install and run locust in an ephemeral environment

.. code-block:: console
    :substitutions:

    $ uvx locust -V
    locust |version| from /.../uv/.../locust (Python 3.12.5)

Done!
-----

Now you can :ref:`create and run your first test <quickstart>`

-----------------


Pre-release builds
------------------

If you need the latest and greatest version of Locust and cannot wait for the next release, you can install a dev build like this:

.. code-block:: console

    $ pip3 install -U --pre locust

Pre-release builds are published every time a branch/PR is merged into master.

Install for development
-----------------------

If you want to modify Locust, or contribute to the project, see :ref:`developing-locust`.

Troubleshooting installation
----------------------------


.. contents:: Some solutions for common installation issues
    :depth: 1
    :local:
    :backlinks: none


psutil/\_psutil_common.c:9:10: fatal error: Python.h: No such file or directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Answered in Stackoverflow thread 63440765 <https://stackoverflow.com/questions/63440765/locust-installation-error-using-pip3-error-command-errored-out-with-exit-statu>`_

ERROR: Failed building wheel for xxx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While Locust itself is a pure Python package, it has some dependencies
(e.g. gevent and geventhttpclient) that are compiled from C code. Pretty
much all common platforms have binary packages on PyPi, but sometimes
there is a new release that doesn't, or you are running on some exotic
platform. You have two options:

-  (on macos) Install xcode: ``xcode-select --install``
-  Use ``pip install --prefer-binary locust`` to select a pre-compiled
   version of packages even if there is a more recent version available
   as source.
-  Try googling the error message for the specific package that failed
   (not Locust), ensure you have the appropriate build tools installed
   etc.

Windows
~~~~~~~

`Answered in Stackoverflow thread 61592069 <https://stackoverflow.com/questions/61592069/locust-is-not-installing-on-my-windows-10-for-load-testing>`_

Installation works, but the ``locust`` command is not found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running pip, did you get a warning saying ``The script locust is installed in '...' which is not on PATH``?

Add that directory to your PATH environment variable.

Increasing Maximum Number of Open Files Limit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every User/HTTP connection from Locust opens a new file (technically
a file descriptor). Many operating systems by default set a low limit
for the maximum number of files that can be open at the same time.
Locust will try to adjust this automatically for you, but in a lot of
cases your operating system will not allow it (in which case you will
get a warning in the log). Instead you will have to do it manually.

How to do this depends on your operating system, but you might find
some useful information here:
https://www.tecmint.com/increase-set-open-file-limits-in-linux/ and
practical examples
https://www.ibm.com/support/knowledgecenter/SS8NLW_11.0.2/com.ibm.discovery.es.in.doc/iiysiulimits.html

For systemd-based systems (e.g. Debian/Ubuntu) different limits are
used for graphical login sessions. See
https://unix.stackexchange.com/a/443467 for additional settings.
