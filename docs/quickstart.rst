=============
Quick start
=============

Example locustfile.py
=====================

Below is a quick little example of a simple **locustfile.py**::

    from locust import HttpLocust, TaskSet
    
    def login(l):
        l.client.post("/login", {"username":"ellen_key", "password":"education"})
    
    def logout(l):
        l.client.post("/logout", {"username":"ellen_key", "password":"education"})
    
    def index(l):
        l.client.get("/")
    
    def profile(l):
        l.client.get("/profile")
    
    class UserBehavior(TaskSet):
        tasks = {index: 2, profile: 1}
        
        def on_start(self):
            login(self)
        
        def on_stop(self):
            logout(self)
    
    class WebsiteUser(HttpLocust):
        task_set = UserBehavior
        min_wait = 5000
        max_wait = 9000


Here we define a number of Locust tasks, which are normal Python callables that take one argument 
(a :py:class:`Locust <locust.core.Locust>` class instance). These tasks are gathered under a
:py:class:`TaskSet <locust.core.TaskSet>` class in the *tasks* attribute. Then we have a
:py:class:`HttpLocust <locust.core.HttpLocust>` class which represents a user, where we define how
long a simulated user should wait between executing tasks, as well as what
:py:class:`TaskSet <locust.core.TaskSet>` class should define the user's \"behaviour\". 
:py:class:`TaskSet <locust.core.TaskSet>` classes can be nested.

The :py:class:`HttpLocust <locust.core.HttpLocust>` class inherits from the
:py:class:`Locust <locust.core.Locust>` class, and it adds a client attribute which is an instance of
:py:class:`HttpSession <locust.clients.HttpSession>` that can be used to make HTTP requests.

Another way we could declare tasks, which is usually more convenient, is to use the
``@task`` decorator. The following code is equivalent to the above::

    from locust import HttpLocust, TaskSet, task
    
    class UserBehavior(TaskSet):
        def on_start(self):
            """ on_start is called when a Locust start before any task is scheduled """
            self.login()
        
        def on_stop(self):
            """ on_stop is called when the TaskSet is stopping """
            self.logout()
        
        def login(self):
            self.client.post("/login", {"username":"ellen_key", "password":"education"})
        
        def logout(self):
            self.client.post("/logout", {"username":"ellen_key", "password":"education"})
        
        @task(2)
        def index(self):
            self.client.get("/")
        
        @task(1)
        def profile(self):
            self.client.get("/profile")
    
    class WebsiteUser(HttpLocust):
        task_set = UserBehavior
        min_wait = 5000
        max_wait = 9000

The :py:class:`Locust <locust.core.Locust>` class (as well as :py:class:`HttpLocust <locust.core.HttpLocust>`
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

To run Locust distributed across multiple processes we would start a master process by specifying
``--master``::

    locust -f locust_files/my_locust_file.py --master --host=http://example.com

and then we would start an arbitrary number of slave processes::

    locust -f locust_files/my_locust_file.py --slave --host=http://example.com

If we want to run Locust distributed on multiple machines we would also have to specify the master host when
starting the slaves (this is not needed when running Locust distributed on a single machine, since the master
host defaults to 127.0.0.1)::

    locust -f locust_files/my_locust_file.py --slave --master-host=192.168.0.100 --host=http://example.com


.. note::

    To see all available options type: ``locust --help``


Open up Locust's web interface
==============================

Once you've started Locust using one of the above command lines, you should open up a browser
and point it to http://127.0.0.1:8089 (if you are running Locust locally). Then you should be
greeted with something like this:

.. image:: images/webui-splash-screenshot.png
