======================
Writing a locustfile
======================

A locustfile is a normal python file. The only requirement is that it declares at least one class -
let's call it the locust class - that inherits from the class Locust. 

The Locust class
================

A locust class represents one user (or a swarming locust if you will). Locust will spawn (hatch) one 
instance of the locust class for each user that is being simulated. There are a few attributes that 
a locust class should typically define. 

The :py:attr:`task_set <locust.core.Locust.task_set>` attribute
---------------------------------------------------------------

The :py:attr:`task_set <locust.core.Locust.task_set>` attribute should point to a 
:py:class:`TaskSet <locust.core.TaskSet>` class which defines the behaviour of the user and 
is described in more details below.

The *min_wait* and *max_wait* attributes
----------------------------------------

Additionally to the task_set attribute, one usually want to declare the *min_wait* and *max_wait* 
attributes. These are the minimum and maximum time, in milliseconds, that a simulated user will wait 
between executing each task. *min_wait* and *max_wait* defaults to 1000, and therefore a locust will 
always wait 1 second between each task if *min_wait* and *max_wait* is not declared.

With the following locustfile, each user would wait between 5 and 15 seconds between tasks::

    from locust import Locust, TaskSet, task
    
    class MyTaskSet(TaskSet):
        @task
        def my_task(l):
            print "executing my_task"
    
    class MyLocust(Locust):
        task_set = MyTaskSet
        min_wait = 5000
        max_wait = 15000

The *min_wait* and *max_wait* attributes can also be overrided in a TaskSet class.

The *host* attribute
--------------------

The host attribute is a URL prefix (i.e. "http://google.com") to the host that is to be loaded. 
Usually, this is specified on the command line, using the --host option, when locust is started. 
If one declares a host attribute in the locust class, it will be used in the case when no --host 
is specified on the command line.


TaskSet class
=============

If the Locust class represents a swarming locust, you could say that the TaskSet class represents 
the brain of the locust. Each Locust class must have a *task_set* attribute set, that points to 
a TaskSet.

A TaskSet is, like it's name suggests, a collection of tasks. These tasks are normal python callables 
and - if we were loadtesting an auction website - could do stuff like "loading the start page", 
"searching for some product" and "making a bid". 

When a load test is started, each instance of the spawned Locust classes will start executing their 
TaskSet. What happens then is that each TaskSet will pick one of it's tasks and call it. It will then 
wait a number of milliseconds, choosed at random between the Locust class' *min_wait* and *max_wait* attributes 
(unless min_wait/max_wait has been defined directly under the TaskSet, in which case it will use 
it's own values instead). Then it will again pick a new task which will be called, then wait again, 
and so on.

Declaring tasks
---------------

The typical way of declaring tasks for a TaskSet it to use the :py:meth:`task <locust.core.task>` decorator.

Here is an example::

    from locust import Locust, TaskSet, task
    
    class MyTaskSet(TaskSet):
        @task
        def my_task(self):
            print "Locust instance (%r) executing my_task" % (self.locust)
    
    class MyLocust(Locust):
        task_set = MyTaskSet

**@task** takes an optional weight argument that can be used to specify the tasks' execution ratio. In 
the following example *task2* will be executed twice as much as *task1*::
    
    from locust import Locust, TaskSet, task
    
    class MyTaskSet(TaskSet):
        min_wait = 5000
        max_wait = 15000
        
        @task(3)
        def task1(self):
            pass
        
        @task(6)
        def task2(self):
            pass
    
    class MyLocust(Locust):
        task_set = MyTaskSet


task attribute
--------------

Using the @task decorator to declare tasks is a convenience, and usually that's the best way to do 
it. However, it's also possible to define the tasks of a TaskSet by setting the 
:py:attr:`tasks <locust.core.TaskSet.tasks>` attribute (actually using the @task decorator will actually 
just populate the *tasks* attribute).

The *tasks* attribute which is either a list of python callables, or a *<callable : int>* dict. 
The tasks are python callables, that recieves one argument - the TaskSet class instance that is executing 
the task. Here is an extremely simple example of a locustfile (this locsutfile won't actually load test anything)::

    from locust import Locust, TaskSet
    
    def my_task(l):
        pass
    
    class MyTaskSet(TaskSet):
        tasks = [my_task]
    
    class MyLocust(Locust):
        task_set = MyTaskSet


If the 
tasks attribute is specified as a list, each time a task is to be performed, it will be randomly 
chosen from the *tasks* attribute. If however, *tasks* is a dict - with callables as keys and ints 
as values - the task that is to be executed will be chosen at random but with the int as ratio. So 
with a tasks that looks like this::

    {my_task: 3, another_task:1}

*my_task* would be 3 times more likely to be executed than *another_task*.

TaskSets can be nested
----------------------

A very important property of TaskSets are that they can be nested, because real websites are usually 
built up in an hierarchical way, with multiple sub sections. Nesting TaskSets will therefore allow 
us to define a behaviour that simulates users in a more realistic way. For example 
we could define TaskSets with the following structure:

* Main user behaviour

 * Index page
 * Forum page
 
  * Read thread
  
   * Reply
   
  * New thread
  * View next page
  
 * Browse categories
 
  * Watch movie
  * Filter movies
  
 * About page

The way you nest TaskSets is just like when you specify a task using the **tasks** attribute, but 
instead of refering to a python function, you point it to another TaskSet::

    class ForumPage(TaskSet):
        @task(20)
        def read_thread(self):
            pass
        
        @task(1)
        def new_thread(self):
            pass
        
        @task(5)
        def stop(self):
            self.interrupt()
    
    class UserBehaviour(TaskSet):
        tasks = {ForumPage:10}
        
        @task
        def index(self):
            pass

So in above example, if the ForumPage would get selected for execution when the UserBehaviour 
TaskSet is executing, is. that the ForumPage TaskSet would start executing. The ForumPage TaskSet 
would then pick one of it's own task, execute it, then wait, and so on. 

There is one important thing to note about the above example, and that is the call to 
self.interrupt() in the ForumPage's stop method. What this does is essentially that it will 
stop executing the ForumPage task set and the execution will continue in the UserBehaviour instance. 
If we wouldn't have had a call to the :py:meth:`interrupt() <locust.core.TaskSet.interrupt>` method 
somewhere in ForumPage, the Locust would never stop running the ForumPage task once it has started. 
But by having the interrupt function, we can - together with task weighting - define how likely it 
is that a simulated user leaves the forum.

It's also possible to declare a nested TaskSet, inline in a class, using the 
:py:meth:`@task <locust.core.task>` decorator, just like when declaring normal tasks::

    class MyTaskSet(TaskSet):
        @task
        class SubTaskSet(TaskSet):
            @task
            def my_task(self):
                pass


The on_start function
---------------------

A TaskSet class can optionally declare an :py:meth:`on_start <locust.core.TaskSet.on_start>` function. 
If so, that function is called when a simulated user starts executing that TaskSet class.

Making HTTP requests 
=====================

So far, we've only covered the task scheduling part of a Locust user. In order to actually load test 
a system we need to make HTTP requests. To help us do this, each Locust instance gets a 
:py:attr:`client <locust.core.Locust.client>` attribute which will be an instance of 
:py:attr:`HttpSession <locust.core.client.HttpSession>` which can be used to make HTTP requests.

.. autoclass:: locust.core.Locust
    :members: client
    :noindex:

When inheriting from the Locust class, we can use it's client attribute to make HTTP requests 
against the server. Here is an example of a locust file that can be used to load test a site 
with two urls; **/** and **/about/**::

    from locust import Locust, TaskSet, task
    
    class MyTaskSet(TaskSet):
        @task(2)
        def index(self):
            self.client.get("/")
        
        @task(1)
        def about(self):
            self.client.get("/about/")
    
    class MyLocust(Locust):
        task_set = MyTaskSet
        min_wait = 5000
        max_wait = 15000

Using the above Locust class, each simulated user will wait between 5 and 15 seconds 
between the requests, and **/** will be requested twice as much as **/about/**.

Using the HTTP client
======================

Each instance of Locust has an instance of :py:class:`HttpSession <locust.clients.HttpSession>` 
in the *client* attribute. The HttpSession class is actually a subclass of 
:py:class:`requests.Session` and can be used to  make HTTP requests, that will be reported to Locust's
statistics, using the :py:meth:`get <locust.clients.HttpSession.get>`, 
:py:meth:`post <locust.clients.HttpSession.post>`, :py:meth:`put <locust.clients.HttpSession.put>`, 
:py:meth:`delete <locust.clients.HttpSession.delete>`, :py:meth:`head <locust.clients.HttpSession.head>`, 
:py:meth:`patch <locust.clients.HttpSession.patch>` and :py:meth:`options <locust.clients.HttpSession.options>` 
methods. The HttpSession instance will preserve cookies between requests so that it can be used to log in 
to websites and keep a session between requests. The client attribute is also copied to the Locust isntance's
TaskSet instances so that it's easy to retrieve the client and make HTTP requests from within your tasks.

Here's a simple example that makes a GET request to the */about* path (in this case we assume *self* 
is an instance of a :py:class:`TaskSet <locust.core.TaskSet>` or :py:class:`Locust <locust.core.Locust>` class::

    response = self.client.get("/about")
    print "Response status code:", response.status_code
    print "Response content:", response.content

And here's an example making a POST request::

    response = self.client.post("/login", {"username":"testuser", "password":"secret"})

Safe mode
---------
The HTTP client is configured to run in safe_mode. What this does is that any request that fails due to 
a connection error, timeout, or similar will not raise an exception, but rather return an empty dummy 
Response object. The request will be reported as a failure in Locust's statistics. The returned dummy 
Response's *content* attribute will be set to None, and it's *status_code* will be 0.


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
