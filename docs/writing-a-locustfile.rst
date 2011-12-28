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

Each instance of Locust has an instance of HttpBrowser in the *client* attribute. 

.. autoclass:: locust.clients.HttpBrowser
    :members: __init__, get, post
    :noindex:

By default, requests are marked as failed requests unless the HTTP response code is ok (2xx). 
However, one can mark requests as failed, even when the response code is okay, by using the 
*catch_response* argument with a with statement::

    from locust import ResponseError
    
    client = HttpBrowser("http://example.com")
    with client.get("/", catch_response=True) as response:
        if response.data != "Success":
            raise ResponseError("Got wrong response")

Just as one can mark requests with OK response codes as failures, one can also make requests that 
results in an HTTP error code still result in a success in the statistics::

    client = HttpBrowser("http://example.com")
    response = client.get("/does_not_exist/", allow_http_error=True)
    if response.exception:
        print "We got an HTTPError exception, but the request will still be marked as OK"
    
Also, *catch_response* and *allow_http_error* can be used together.


The @required_once decorator
============================

The @required_once decorator is used to make sure that a task is run once, and only once, for each 
user, before another task is executed. 

.. autofunction:: locust.core.require_once
    :noindex:

For example, this can be useful when you have a locust task that shouldn't be executed before a user 
has logged in, let's call it inbox. If you have a task called login that makes the appropriate login 
HTTP request(s), then you can decorate the inbox task with::

    @required_once(login)
    def inbox(l):
        ...

The difference from just calling the login function in the beginning of the inbox task is that the 
@required_once decorator respects the Locust class's scheduling mechanism (the *min_wait* and 
*max_wait* attributes). So when inbox is to be executed for a locust user that hasn't yet executed 
the login task, the login task will be executed first, and the inbox task will be scheduled to run 
as the next task (after the wait time). The next time the same locust user is to execute the inbox 
task, login will not be run, since it has already been executed for that locust user.


Using SubLocusts
================

Real websites are usually built up in an hierarchical way, with multiple sub sections. To allow the 
load testing scripts to more realistically simulate real user behaviour, Locust provides the 
SubLocust class. A SubLocust class contains normal locust tasks, just like normal Locust classes. 
However, a SubLocust class can be used as a **task** under any Locust - or SubLocust - class. This
allows us to build tests that simulates users that browses the website in a more hierarchical, and 
thus more realistic, way.
