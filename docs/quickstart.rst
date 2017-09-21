=============
Quick start
=============

Example locustfile.py
=====================

Below is a quick little example of a simple **locustfile.py**::

    from locust import WebLocust, TaskSet
    
    def login(l):
        l.client.http.post("/login", {"username":"ellen_key", "password":"education"})
    
    def index(l):
        l.client.http.get("/")
    
    def profile(l):
        l.client.http.get("/profile")
    
    class UserBehavior(TaskSet):
        tasks = {index: 2, profile: 1}
        
        def on_start(self):
            self.context['credentioals'] = {"username":"ellen_key", "password":"education"}
            pass
        
        def on_task_start(self):
            login(self)
    
    class WebsiteUser(WebLocust):
        task_set = UserBehavior
        min_wait = 5000
        max_wait = 9000
    

Here we define a number of Locust tasks, which are normal Python callables that take one argument
(a :py:class:`Locust <locust.core.Locust>` class instance). These tasks are gathered under a
:py:class:`TaskSet <locust.core.TaskSet>` class in the *tasks* attribute. Then we have a
:py:class:`WebLocust <locust.core.WebLocust>` class which represents a user, where we define how
long a simulated user should wait between executing tasks, as well as what
:py:class:`TaskSet <locust.core.TaskSet>` class should define the user's "behaviour".
:py:class:`TaskSet <locust.core.TaskSet>`s can be nested.

The :py:class:`WebLocust <locust.core.WebLocust>` class inherits from the
:py:class:`Locust <locust.core.Locust>` class, and it adds a client attribute which is an instance of
LocustWebClient :py:class:`Locust <locust.core.LocustWebClient>` whish incapsulates:
* :py:class:`HttpSession <locust.clients.http.WebSocketClient>` that can be used to make HTTP requests
* :py:class:`HttpSession <locust.clients.websocket.Websocket>` that can be used to make websocket related actions
* :py:class:`HttpSession <locust.clients.zmq.ZMQClient>` that can be used to make zmq pub fires

Another way we could declare tasks, which is usually more convenient, is to use the
``@task`` decorator. The following code is equivalent to the above::

    from locust import WebLocust, TaskSet, task
    
    class UserBehavior(TaskSet):

        def on_start(self):
            context['username'] = 'ellen_key'
            context['password'] = 'education'

        def on_task_start(self):
            """ on_start is called when a Locust start before any task is scheduled """
            self.login()
        
        def login(self):
            payload = {"username": self.context['username'], "password": self.context['password']}
            self.client.post("/login", payload)
        
        @task(2)
        def index(self):
            self.client.http.get("/")
        
        @task(1)
        def profile(self):
            self.client.http.get("/profile")
    
    class WebsiteUser(WebLocust):
        task_set = UserBehavior
        min_wait = 5000
        max_wait = 9000

The :py:class:`Locust <locust.core.Locust>` class (as well as :py:class:`WebLocust <locust.core.WebLocust>`
since it's a subclass) also allows one to specify minimum and maximum wait time—per simulated
user—between the execution of tasks (*min_wait* and *max_wait*) as well as other user behaviours.


Start Locust
============

To run Locust with the above Locust file, if it was named *locustfile.py* and located in the current working
directory, we could run::

    locust --host=http://example.com

If the Locust file is located under a subdirectory and/or named different than *locustfile.py*, specify
it using ``-f``::

    locust -f locust_files/my_locust_file.py --host=http://example.com

By default Locust run as destributed system so you can add node anytime before actual testrun started::

    locust -f locust_files/my_locust_file.py --slave

but more meaning to add node from separate machine. If we want to run Locust distributed on multiple machines 
we would also have to specify the master host when starting the slaves (this is not needed when running Locust 
distributed on a single machine, since the master host defaults to 127.0.0.1)::

    locust -f locust_files/my_locust_file.py --slave --master-host=192.168.0.100

You may wish to consume your Locust results via a csv file. In this case, there are two ways to do this.

First, when running the webserver, you can retrieve a csv from ``localhost:8089/stats/requests/csv`` and ``localhost:8089/stats/distribution/csv``.
Second you can run Locust with a flag which will periodically save the csv file. This is particularly useful
if you plan on running Locust in an automated way with the ``--no-web`` flag::

    locust -f locust_files/my_locust_file.py --csv=foobar --no-web -n10 -c1

You can also customize how frequently this is written if you desire faster (or slower) writing::


    import locust.stats
    locust.stats.CSV_STATS_INTERVAL_SEC = 5 # default is 2 seconds

.. note::

To see all available options type::

    locust --help


Open up Locust's web interface
==============================

Once you've started Locust using one of the above command lines, you should open up a browser
and point it to http://127.0.0.1:8089 (if you are running Locust locally). Then you should be
greeted with something like this:

.. image:: images/webui-splash-screenshot.png
