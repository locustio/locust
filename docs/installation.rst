Installation
============

Locust is available on PyPI and can be installed through pip or easy_install

::

    pip install locustio

or::

    easy_install locustio

When Locust is installed, a **locust** command should be available in your shell (if you're not using 
virtualenv - which you should - make sure your python script directory is on your path).

To see available options, run::

    locust --help


Installing ZeroMQ
-----------------

If you intend to run Locust distributed across multiple processes/machines, we recommend you to also 
install **pyzmq**::

    pip install pyzmq

or::

    easy_install pyzmq

Installing Locust on Windows
----------------------------

The easiest way to get Locust running on Windows is to first install pre built binary packages for
gevent (0.13) and greenlet and then follow the above instructions. 

Installing Locust on OS X
----------------------------

The following is currently the shortest path to installing gevent on OS X using Homebrew.

#. Install [Homebrew](http://mxcl.github.com/homebrew/).
#. Install libevent (dependency for gevent)::

    brew install libevent

#. Then follow the above instructions.
