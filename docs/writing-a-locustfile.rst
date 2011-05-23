======================
Writing a locustfile
======================

A locustfile is a normal python file. The only requirement is that it declares at least one class, let's call it the locust class, that inherits from the Locust class
(or, when load testing a web application, the WebLocust class). 

The Locust class
================

A locust class represents one website user. Locust will spawn one instance of the locust class for each user that is being simulated. 
The locust class has to declare a *tasks* attribute which is either a list of python callables or a *<callable : int>* dict. The task 
attribute defines the different tasks that a website user might do. The tasks are python callables, that recieves one argument - the locust class instance representing 
the user that is performing the task. Here is an extremely simple example of a locustfile (this locsutfile won't actually load test anything)::

    from locust import Locust
    
    def my_task(l):
        pass
    
    class MyLocust(Locust):
        tasks = [my_task]

The *min_wait* and *max_wait* attributes
----------------------------------------

Additionally to the tasks attribute, one usually want to declare the *min_wait* and *max_wait* attributes. These are the minimum and maximum time, in milliseconds, that
a user will wait between executing each task. *min_wait* and *max_wait* defaults to 1000, and therefore a locust will always wait 1 second between each task if *min_wait*
and *max_wait* is not declared.

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

As stated above, the tasks attribute defines the different tasks a locust user will perform. If the tasks attribute is specified as a list, each time a task is to be performed,
it will be randomly chosen from the *tasks* attribute. If however, *tasks* is a dict - with callables as keys and ints as values - the task that is to be executed will be
chosen at random but with the int as ratio. So with a tasks that looks like this::

    {my_task: 3, another_task:1}

*my_task* would be 3 times more likely to be executed than *another_task*.

The *host* attribute
--------------------

The host attribute is an adress to the host that is to be loaded. Usually, this is specified on the command line, using the --host option, when locust is started. If one declares a
host attribute in the locust class, it will be used in the case when no --host is specified on the command line.


Declaring tasks using the @task decorator
-----------------------------------------

Additionally to specifying a Locust's tasks using the **tasks** attribute, one can automatically add class methods to the **tasks** list using the **@task** decorator.

Here is an example::

    from locust import Locust, task
    
    class MyLocust(Locust):
        min_wait = 5000
        max_wait = 15000
        
        @task
        def my_task(self):
            print "executing task"

**@task** takes an optional weight argument that can be used to specify the task execution ratio. In the following example *task2* will be executed twice as much as *task1*::
    
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


Making HTTP requests using the WebLocust class
==============================================

So far, we've only covered the task scheduling part of a Locust user. In order to actually load test a system we need to make HTTP requests.

In the above example we let our locust class inherit from Locust. How ever, when writing a locust file for loading a website, you probably want to use the WebLocust class.
The difference between the Locust base class and the WebLocust class is that WebLocust creates an HTTP client, that is stored in the *client* attribute, upon instantiation. 

.. autoclass:: locust.core.WebLocust
    :members: client
    :noindex:

When inheriting from the WebLocust class, we can use it's client attribute to make HTTP requests against the server. Here is an example of a locust file that can be used
to load test a site with two urls; **/** and **/about/**::

    from locust import WebLocust
    
    def index(l):
        l.client.get("/")
    
    def about(l):
        l.client.get("/about/")
    
    class MyLocust(WebLocust):
        tasks = {index:2, about:1}
        min_wait = 5000
        max_wait = 15000

Using the above locust class, each user will wait between 5 and 15 seconds between the requests, and **/** will be requested twice the amount of times than **/about/**.


The @required_once decorator
============================

The @required_once decorator is used to make sure that a task is run once, and only once, for each user, before another task is executed. 

.. autofunction:: locust.core.require_once
    :noindex:

For example, this can be useful when you have a locust task that shouldn't be executed before a user has logged in, let's call it inbox. If you have a task called login that
makes the appropriate login HTTP request(s), then you can decorate the inbox task with::

    @required_once(login)
    def inbox(l):
        ...

The difference from just calling the login function in the beginning of the inbox task is that the @required_once decorator respects the Locust class's scheduling mechanism
(the *min_wait* and *max_wait* attributes). So when inbox is to be executed for a locust user that hasn't yet executed the login task, the login task will be executed first,
and the inbox task will be scheduled to run as the next task (after the wait time). The next time the same locust user is to execute the inbox task, login will not be run, 
since it has already been executed for that locust user.


Using SubLocusts
================

Real websites are usually built up in an hierarchical way, with multiple sub sections. To allow the load testing scripts to more realistically simulate real user behaviour, 
Locust provides the SubLocust class. A sub class of the SubLocust class contains normal locust tasks, just like sub classes of the Locust or WebLocust classes. 

