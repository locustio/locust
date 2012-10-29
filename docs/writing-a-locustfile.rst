======================
Writing a locustfile
======================

A locustfile is a normal python file. The only requirement is that it declares at least one class -
let's call it the locust class - that inherits from the class Locust. 

The Locust class
================

A locust class represents one website user. Locust will spawn one instance of the locust class for 
each user that is being simulated. The locust class has to declare a *tasks* attribute which is 
either a list of python callables or a *<callable : int>* dict. The task attribute defines the 
different tasks that a website user might do. The tasks are python callables, that recieves one 
argument - the locust class instance representing the user that is performing the task. Here is an 
extremely simple example of a locustfile (this locsutfile won't actually load test anything)::

    from locust import Locust
    
    def my_task(l):
        pass
    
    class MyLocust(Locust):
        tasks = [my_task]

The *min_wait* and *max_wait* attributes
----------------------------------------

Additionally to the tasks attribute, one usually want to declare the *min_wait* and *max_wait* 
attributes. These are the minimum and maximum time, in milliseconds, that a simulated user will wait 
between executing each task. *min_wait* and *max_wait* defaults to 1000, and therefore a locust will 
always wait 1 second between each task if *min_wait* and *max_wait* is not declared.

With the following locustfile, each user would wait between 5 and 15 seconds between tasks::

    from locust import Locust
    
    def my_task(l):
        print "executing my_task"
    
    class MyLocust(Locust):
        tasks = [my_task]
        min_wait = 5000
        max_wait = 15000

The *tasks* attribute
---------------------

As stated above, the tasks attribute defines the different tasks a locust user will perform. If the 
tasks attribute is specified as a list, each time a task is to be performed, it will be randomly 
chosen from the *tasks* attribute. If however, *tasks* is a dict - with callables as keys and ints 
as values - the task that is to be executed will be chosen at random but with the int as ratio. So 
with a tasks that looks like this::

    {my_task: 3, another_task:1}

*my_task* would be 3 times more likely to be executed than *another_task*.

The *host* attribute
--------------------

The host attribute is an adress to the host that is to be loaded. Usually, this is specified on the 
command line, using the --host option, when locust is started. If one declares a host attribute in 
the locust class, it will be used in the case when no --host is specified on the command line.


Declaring tasks using the @task decorator
-----------------------------------------

Additionally to specifying a Locust's tasks using the **tasks** attribute, one can automatically add
class methods to the **tasks** list using the **@task** decorator.

Here is an example::

    from locust import Locust, task
    
    class MyLocust(Locust):
        min_wait = 5000
        max_wait = 15000
        
        @task
        def my_task(self):
            print "executing task"

**@task** takes an optional weight argument that can be used to specify the task execution ratio. In 
the following example *task2* will be executed twice as much as *task1*::
    
    from locust import Locust, task
    
    class MyLocust(Locust):
        min_wait = 5000
        max_wait = 15000
        
        @task(3)
        def task1(self):
            pass
        
        @task(6)
        def task2(self):
            pass


Making HTTP requests 
=====================

So far, we've only covered the task scheduling part of a Locust user. In order to actually load test 
a system we need to make HTTP requests.

.. autoclass:: locust.core.Locust
    :members: client
    :noindex:

When inheriting from the Locust class, we can use it's client attribute to make HTTP requests 
against the server. Here is an example of a locust file that can be used to load test a site 
with two urls; **/** and **/about/**::

    from locust import Locust
    
    class MyLocust(Locust):
        min_wait = 5000
        max_wait = 15000
        
        def index(self):
            self.client.get("/")
        
        def about(self):
            self.client.get("/about/")

Using the above locust class, each user will wait between 5 and 15 seconds between the requests,
and **/** will be requested twice the amount of times than **/about/**.

Using the HTTP client
======================

Each instance of Locust has an instance of :py:class:`HttpSession <locust.clients.HttpSession>` 
in the *client* attribute. The HttpSession class is actually a subclass of 
:py:class:`requests.Session` and can be used to  make HTTP requests, that will be reported to Locust's
statistics, using the :py:meth:`get <locust.clients.HttpSession.get>`, 
:py:meth:`post <locust.clients.HttpSession.post>`, :py:meth:`put <locust.clients.HttpSession.put>`, 
:py:meth:`delete <locust.clients.HttpSession.delete>`, :py:meth:`head <locust.clients.HttpSession.head>`, 
:py:meth:`patch <locust.clients.HttpSession.patch>` and :py:meth:`options <locust.clients.HttpSession.options>` 
methods. The HttpInstance will preserve cookies between requests so that it can be used to log in to websites 
and keep a session between requests.

Here's a simple example that makes a GET request to the */about* path (in this case we assume *self* 
is an instance of a :py:class:`Locust <locust.core.Locust>` class::

    response = self.client.get("/about")
    print "Response status code:", response.status_code
    print "Response content:", response.content

And here's an example making a POST request::

    response = self.client.post("/login", {"username":"testuser", "password":"secret"})

Manually controlling if a request should be considered successful or a failure
------------------------------------------------------------------------------

By default, requests are marked as failed requests unless the HTTP response code is ok (2xx). 
Most of the time, this default is what you want. Sometimes however - for example when testing 
a URL endpoint that you expect to return 404, or testing a badly designed system that might 
return *200 OK* even though an error occurred - there's a need for manually controlling if 
locust should consider a request as a success or a failure.

One can mark requests as failed, even when the response code is okay, by using the 
*catch_response* argument and a with statement::

    with client.get("/", catch_response=True) as response:
        if response.content != "Success":
            response.failure("Got wrong response")

Just as one can mark requests with OK response codes as failures, one can also use **catch_response** 
argument together with a *with* statement to make requests that resulted in an HTTP error code still 
be reported as a success in the statistics::

    with client.get("/does_not_exist/", catch_response=True) as response:
        if response.status_code == 404:
            response.success()


The on_start function
============================

A locust class can optionally have an **on_start** function declared. If so, that function is 
called when a simulated user starts executing that locust class.


Using SubLocusts
================

Real websites are usually built up in an hierarchical way, with multiple sub sections. To allow the 
load testing scripts to more realistically simulate real user behaviour, Locust provides the 
SubLocust class. A SubLocust class contains normal locust tasks, just like normal Locust classes. 
However, a SubLocust class can be used as a **task** under any Locust - or SubLocust - class. This
allows us to build tests that simulates users that browses the website in a more hierarchical, and 
thus more realistic, way.
