=============
Quick start
=============

Example locustfile.py
=====================

When using Locust you define the behaviour of users in Python code, and then you have the ability to 
simulate any number of those users while gathering request statistic. The entrypoint for defining the 
user behaviour is the `locustfile.py`.

.. note::

    The ``locustfile.py`` is a normal Python file that will get imported by Locust. Within it you 
    can import modules just as you would in any python code.
    
    The file can be named something else and specified with the `-f` flag to the ``locust`` command.

Below is a quick little example of a simple **locustfile.py**:

.. code-block:: python
    
    import random
    from locust import HttpUser, task, between
    
    class WebsiteUser(HttpUser):
        wait_time = between(5, 9)
        
        @task(2)
        def index(self):
            self.client.get("/")
            self.client.get("/ajax-notifications/")
        
        @task(1)
        def view_post(self):
            post_id = random.randint(1, 10000)
            self.client.get("/post?id=%i" % post_id, name="/post?id=[post-id]")
        
        def on_start(self):
            """ on_start is called when a User starts before any task is scheduled """
            self.login()
        
        def login(self):
            self.client.post("/login", {"username":"ellen_key", "password":"education"})


Let's break it down:
--------------------

.. code-block:: python

    class WebsiteUser(HttpUser):

Here we define a class for the users that we will be simulating. It inherits from 
:py:class:`HttpUser <locust.core.HttpUser>` which gives each user a ``client`` attribute,
which is an instance of :py:class:`HttpSession <locust.clients.HttpSession>`, that 
can be used to make HTTP requests to the target system that we want to load test. When a test starts, 
locust will create an instance of this class for every user that it simulates, and each of these 
users will start running within their own green gevent thread.

.. code-block:: python

    wait_time = between(5, 9)

Our class defines a ``wait_time`` function that will make the simulated users wait between 5 and 9 seconds after each task 
is executed. 

.. code-block:: python

    @task(2)
    def index(self):
        self.client.get("/")
        self.client.get("/ajax-notifications/")
    
    @task(1)
    def view_post(self):
        ...

We've also declared two tasks by decorating two methods with ``@task`` and given them 
different weights (2 and 1). When a simulated user of this type runs it'll pick one of either ``index`` 
or ``view_post`` - with twice the chance of picking ``index`` - call that method and then pick a duration 
uniformly between 5 and 9 and just sleep for that duration. After it's wait time it'll pick a new task 
and keep repeating that.

.. code-block:: python
    :emphasize-lines: 3,3

    def view_post(self):
        post_id = random.randint(1, 10000)
        self.client.get("/post?id=%i" % post_id, name="/post?id=[post-id]")

In the ``view_post`` task we load a dynamic URL by using a query parameter that is a number picked at random between 
1 and 10000. In order to not get 10k entries in Locust's statistics - since the stats is grouped on the URL - we use 
the :ref:`name parameter <name-parameter>` to group all those requests under an entry named ``"/post?id=[post-id]"`` instead.

.. code-block:: python

    def on_start(self):

Additionally we've declared a `on_start` method. A method with this name will be called for each simulated 
user when they start. For more info see :ref:`on-start-on-stop`.


Start Locust
============

To run Locust with the above Locust file, if it was named *locustfile.py* and located in the current working
directory, we could run:

.. code-block:: console

    $ locust


If the Locust file is located under a subdirectory and/or named different than *locustfile.py*, specify
it using ``-f``:

.. code-block:: console

    $ locust -f locust_files/my_locust_file.py


To run Locust distributed across multiple processes we would start a master process by specifying
``--master``:

.. code-block:: console

    $ locust -f locust_files/my_locust_file.py --master


and then we would start an arbitrary number of worker processes:

.. code-block:: console

    $ locust -f locust_files/my_locust_file.py --worker


If we want to run Locust distributed on multiple machines we would also have to specify the master host when
starting the workers (this is not needed when running Locust distributed on a single machine, since the master
host defaults to 127.0.0.1):

.. code-block:: console

    $ locust -f locust_files/my_locust_file.py --worker --master-host=192.168.0.100


Parameters can also be set in a `config file <https://github.com/bw2/ConfigArgParse#config-file-syntax>`_ (locust.conf or ~/.locust.conf) or in env vars, prefixed by LOCUST\_

For example: (this will do the same thing as the previous command)

.. code-block::

    # locust.conf in current directory
    locustfile locust_files/my_locust_file.py
    worker


.. code-block:: console

    $ LOCUST_MASTER_HOST=192.168.0.100 locust


.. note::

    To see all available options type: ``locust --help``


Open up Locust's web interface
==============================

Once you've started Locust using one of the above command lines, you should open up a browser
and point it to http://127.0.0.1:8089 (if you are running Locust locally). Then you should be
greeted with something like this:

.. image:: images/webui-splash-screenshot.png


Locust Command Line Interface
=============================

.. code-block:: console

    $ locust --help

.. literalinclude:: cli-help-output.txt
    :language: console