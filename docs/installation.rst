Installation
============

Locust is available on PyPI and can be installed through pip or easy_install

::

    pip install locustio


When Locust is installed, a **locust** command should be available in your shell (if you're not using 
virtualenv—which you should—make sure your python script directory is on your path).

To see available options, run::

    locust --help


Supported Python Versions
-------------------------

Locust supports Python 2.7, 3.3, 3.4, 3.5, and 3.6.


Installing Locust on Windows
----------------------------

On Windows, running ``pip install locustio`` *should* work. 

However, if it doesn't, chances are that it can be fixed by first installing
the pre built binary packages for pyzmq, gevent and greenlet. 

You can find an unofficial collection of pre built python packages for windows here: 
`http://www.lfd.uci.edu/~gohlke/pythonlibs/ <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_

When you've downloaded a pre-built ``.whl`` file, you can install it with::

    pip install name-of-file.whl

Once you've done that you should be able to just ``pip install locustio``. 

.. note::

    Running Locust on Windows should work fine for developing and testing your load testing 
    scripts. However, when running large scale tests, it's recommended that you do that on 
    Linux machines, since gevent's performance under Windows is poor.


Installing Locust on OS X
-------------------------

The following is currently the shortest path to installing gevent on OS X using Homebrew.

#. Install `Homebrew <http://mxcl.github.com/homebrew/>`_.
#. Install libev (dependency for gevent)::

    brew install libev

#. Then follow the above instructions.

Increasing Maximum Number of Open Files Limit
---------------------------------------------

Every HTTP connection on a machine opens a new file (technically a file descriptor).
Operating systems may set a low limit for the maximum number of files
that can be open. If the limit is less than the number of simulated users in a test,
failures will occur.

Increase the operating system's default maximum number of files limit to a number
higher than the number of simulated users you'll want to run. How to do this depends
on the operating system in use.
