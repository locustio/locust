======================
Writing a locustfile
======================

A locustfile is a normal python file. The only requirement is that it declares at least one class—
let's call it the locust class—that inherits from the class Locust. 

The Locust class
================

A locust class represents one user (or a swarming locust if you will). Locust will spawn (hatch) one 
instance of the locust class for each user that is being simulated. There are a few attributes that 
a locust class should typically define. 

The *task_set* attribute
------------------------

The :py:attr:`task_set <locust.core.Locust.task_set>` attribute should point to a 
:py:class:`TaskSet <locust.core.TaskSet>` class which defines the behaviour of the user and 
is described in more detail below.

The *wait_time* attribute
-------------------------

In addition to the *task_set* attribute, one should also declare a 
:py:attr:`wait_time <locust.core.Locust.wait_time>` method. It's used to determine 
for how long a simulated user will wait between executing tasks. Locust comes with a few built in 
functions that return a few common wait_time methods.

The most common one is :py:attr:`between <locust.wait_time.between>`. It's used to make the simulated
users wait a random time between a min and max value after each task execution. Other built in 
wait time functions are :py:attr:`constant <locust.wait_time.constant>` and 
:py:attr:`constant_pacing <locust.wait_time.constant_pacing>`.

With the following locustfile, each user would wait between 5 and 15 seconds between tasks:

.. code-block:: python

    from locust import Locust, TaskSet, task, between
    
    class MyTaskSet(TaskSet):
        @task
        def my_task(self):
            print("executing my_task")
    
    class User(Locust):
        task_set = MyTaskSet
        wait_time = between(5, 15)

The wait_time method should return a number of seconds (or fraction of a second) and can also 
be declared on a TaskSet class, in which case it will only be used for that TaskSet.

It's also possible to declare your own wait_time method directly on a Locust or TaskSet class. The 
following locust class would start sleeping for one second and then one, two, three, etc.

.. code-block:: python

    class MyLocust(Locust):
        task_set = MyTaskSet
        last_wait_time = 0
        
        def wait_time(self):
            self.last_wait_time += 1
            return self.last_wait_time
    


The *weight* attribute
----------------------

If more than one locust class exists in the file, and no locusts are specified on the command line,
each new spawn will choose randomly from the existing locusts. Otherwise, you can specify which locusts
to use from the same file like so:

.. code-block:: console

    $ locust -f locust_file.py WebUserLocust MobileUserLocust

If you wish to make one of these locusts execute more often you can set a weight attribute on those
classes. Say for example, web users are three times more likely than mobile users:

.. code-block:: python

    class WebUserLocust(Locust):
        weight = 3
        ...

    class MobileUserLocust(Locust):
        weight = 1
        ...


The *host* attribute
--------------------

The host attribute is a URL prefix (i.e. "http://google.com") to the host that is to be loaded. 
Usually, this is specified in Locust's web UI or on the command line, using the 
:code:`--host` option, when locust is started. 

If one declares a host attribute in the locust class, it will be used in the case when no :code:`--host` 
is specified on the command line or in the web request.


TaskSet class
=============

If the Locust class represents a swarming locust, you could say that the TaskSet class represents 
the brain of the locust. Each Locust class must have a *task_set* attribute set, that points to 
a TaskSet.

A TaskSet is, like its name suggests, a collection of tasks. These tasks are normal python callables 
and—if we were load-testing an auction website—could do stuff like "loading the start page", 
"searching for some product" and "making a bid". 

When a load test is started, each instance of the spawned Locust classes will start executing their 
TaskSet. What happens then is that each TaskSet will pick one of its tasks and call it. It will then 
wait a number of seconds, specified by the Locust class' *wait_time* method (unless a *wait_time* 
method has been declared directly on the TaskSet, in which case it will use its own method instead). 
Then it will again pick a new task to be called, wait again, and so on.

Declaring tasks
---------------

The typical way of declaring tasks for a TaskSet it to use the :py:meth:`task <locust.core.task>` decorator.

Here is an example:

.. code-block:: python

    from locust import Locust, TaskSet, task
    
    class MyTaskSet(TaskSet):
        @task
        def my_task(self):
            print("Locust instance (%r) executing my_task" % (self.locust))
    
    class MyLocust(Locust):
        task_set = MyTaskSet

**@task** takes an optional weight argument that can be used to specify the task's execution ratio. In 
the following example *task2* will be executed twice as much as *task1*:

.. code-block:: python
    
    from locust import Locust, TaskSet, task
    from locust.wait_time import between
    
    class MyTaskSet(TaskSet):
        wait_time = between(5, 15)
        
        @task(3)
        def task1(self):
            pass
        
        @task(6)
        def task2(self):
            pass
    
    class MyLocust(Locust):
        task_set = MyTaskSet


tasks attribute
---------------

Using the @task decorator to declare tasks is a convenience, and usually the best way to do 
it. However, it's also possible to define the tasks of a TaskSet by setting the 
:py:attr:`tasks <locust.core.TaskSet.tasks>` attribute (using the @task decorator will actually 
just populate the *tasks* attribute).

The *tasks* attribute is either a list of python callables, or a *<callable : int>* dict. 
The tasks are python callables that receive one argument—the TaskSet class instance that is executing 
the task. Here is an extremely simple example of a locustfile (this locustfile won't actually load test anything):

.. code-block:: python

    from locust import Locust, TaskSet
    
    def my_task(l):
        pass
    
    class MyTaskSet(TaskSet):
        tasks = [my_task]
    
    class MyLocust(Locust):
        task_set = MyTaskSet


If the tasks attribute is specified as a list, each time a task is to be performed, it will be randomly 
chosen from the *tasks* attribute. If however, *tasks* is a dict—with callables as keys and ints 
as values—the task that is to be executed will be chosen at random but with the int as ratio. So 
with a tasks that looks like this::

    {my_task: 3, another_task: 1}

*my_task* would be 3 times more likely to be executed than *another_task*.

TaskSets can be nested
----------------------

A very important property of TaskSets is that they can be nested, because real websites are usually 
built up in an hierarchical way, with multiple sub-sections. Nesting TaskSets will therefore allow 
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
instead of referring to a python function, you refer to another TaskSet:

.. code-block:: python

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

So in the above example, if the ForumPage would get selected for execution when the UserBehaviour 
TaskSet is executing, then the ForumPage TaskSet would start executing. The ForumPage TaskSet 
would then pick one of its own tasks, execute it, wait, and so on. 

There is one important thing to note about the above example, and that is the call to 
self.interrupt() in the ForumPage's stop method. What this does is essentially to 
stop executing the ForumPage task set and the execution will continue in the UserBehaviour instance. 
If we didn't have a call to the :py:meth:`interrupt() <locust.core.TaskSet.interrupt>` method 
somewhere in ForumPage, the Locust would never stop running the ForumPage task once it has started. 
But by having the interrupt function, we can—together with task weighting—define how likely it 
is that a simulated user leaves the forum.

It's also possible to declare a nested TaskSet, inline in a class, using the 
:py:meth:`@task <locust.core.task>` decorator, just like when declaring normal tasks:

.. code-block:: python

    class MyTaskSet(TaskSet):
        @task
        class SubTaskSet(TaskSet):
            @task
            def my_task(self):
                pass

Referencing the Locust instance, or the parent TaskSet instance
---------------------------------------------------------------

A TaskSet instance will have the attribute :py:attr:`locust <locust.core.TaskSet.locust>` point to 
its Locust instance, and the attribute :py:attr:`parent <locust.core.TaskSet.parent>` point to its 
parent TaskSet (it will point to the Locust instance, in the base TaskSet).


TaskSequence class
==================

TaskSequence class is a TaskSet but its tasks will be executed in order.
To define this order you should do the following:

.. code-block:: python

    class MyTaskSequence(TaskSequence):
        @seq_task(1)
        def first_task(self):
            pass

        @seq_task(2)
        def second_task(self):
            pass

        @seq_task(3)
        @task(10)
        def third_task(self):
            pass

In the above example, the order is defined to execute first_task, then second_task and lastly the third_task for 10 times.
As you can see, you can compose :py:meth:`@seq_task <locust.core.seq_task>` with :py:meth:`@task <locust.core.task>` decorator, and of course you can also nest TaskSets within TaskSequences and vice versa.

Setups, Teardowns, on_start, and on_stop
========================================

Locust optionally supports :py:class:`Locust <locust.core.Locust>` level :py:meth:`setup <locust.core.Locust.setup>` and :py:meth:`teardown <locust.core.Locust.teardown>`,
:py:class:`TaskSet <locust.core.TaskSet>` level :py:meth:`setup <locust.core.Locust.setup>` and :py:meth:`teardown <locust.core.Locust.teardown>`,
and :py:class:`TaskSet <locust.core.TaskSet>` :py:meth:`on_start <locust.core.TaskSet.on_start>` and :py:meth:`on_stop <locust.core.TaskSet.on_stop>`

Setups and Teardowns
--------------------

:py:meth:`setup <locust.core.Locust.setup>` and :py:meth:`teardown <locust.core.Locust.teardown>`, whether it's run on :py:class:`Locust <locust.core.Locust>` or :py:class:`TaskSet <locust.core.TaskSet>`, are methods that are run only once.
:py:meth:`setup <locust.core.Locust.setup>` is run before tasks start running, while :py:meth:`teardown <locust.core.Locust.teardown>` is run after all tasks have finished and Locust is exiting.
This enables you to perform some preparation before tasks start running (like creating a database) and to clean up before the Locust quits (like deleting the database).

To use, simply declare a :py:meth:`setup <locust.core.Locust.setup>` and/or :py:meth:`teardown <locust.core.Locust.teardown>` on the :py:class:`Locust <locust.core.Locust>` or :py:class:`TaskSet <locust.core.TaskSet>` class.
These methods will be run for you.

The on_start and on_stop methods
----------------------------------

A TaskSet class can declare an :py:meth:`on_start <locust.core.TaskSet.on_start>` method or an :py:meth:`on_stop <locust.core.TaskSet.on_stop>` method.
The :py:meth:`on_start <locust.core.TaskSet.on_start>` method is called when a simulated user starts executing that TaskSet class,
while the :py:meth:`on_stop <locust.core.TaskSet.on_stop` method is called when the TaskSet is stopped.

Order of events
---------------

Since many setup and cleanup operations are dependent on each other, here is the order which they are run:

1. Locust setup (once)
2. TaskSet setup (once)
3. TaskSet on_start (once per locust)
4. TaskSet tasks...
5. TaskSet on_stop (once per locust)
6. TaskSet teardown (once)
7. Locust teardown (once)

In general, the setup and teardown methods should be complementary.


Making HTTP requests
=====================

So far, we've only covered the task scheduling part of a Locust user. In order to actually load test 
a system we need to make HTTP requests. To help us do this, the :py:class:`HttpLocust <locust.core.HttpLocust>`
class exists. When using this class, each instance gets a 
:py:attr:`client <locust.core.Locust.client>` attribute which will be an instance of 
:py:attr:`HttpSession <locust.core.client.HttpSession>` which can be used to make HTTP requests.

.. autoclass:: locust.core.HttpLocust
    :members: client
    :noindex:

When inheriting from the HttpLocust class, we can use its client attribute to make HTTP requests 
against the server. Here is an example of a locust file that can be used to load test a site 
with two URLs; **/** and **/about/**:

.. code-block:: python

    from locust import HttpLocust, TaskSet, task, between
    
    class MyTaskSet(TaskSet):
        @task(2)
        def index(self):
            self.client.get("/")
        
        @task(1)
        def about(self):
            self.client.get("/about/")
    
    class MyLocust(HttpLocust):
        task_set = MyTaskSet
        wait_time = between(5, 15)

Using the above Locust class, each simulated user will wait between 5 and 15 seconds 
between the requests, and **/** will be requested twice as much as **/about/**.

The attentive reader will find it odd that we can reference the HttpSession instance 
using *self.client* inside the TaskSet, and not *self.locust.client*. We can do this 
because the :py:class:`TaskSet <locust.core.TaskSet>` class has a convenience property 
called client that simply returns self.locust.client.


Using the HTTP client
----------------------

Each instance of HttpLocust has an instance of :py:class:`HttpSession <locust.clients.HttpSession>` 
in the *client* attribute. The HttpSession class is actually a subclass of 
:py:class:`requests.Session` and can be used to  make HTTP requests, that will be reported to Locust's
statistics, using the :py:meth:`get <locust.clients.HttpSession.get>`, 
:py:meth:`post <locust.clients.HttpSession.post>`, :py:meth:`put <locust.clients.HttpSession.put>`, 
:py:meth:`delete <locust.clients.HttpSession.delete>`, :py:meth:`head <locust.clients.HttpSession.head>`, 
:py:meth:`patch <locust.clients.HttpSession.patch>` and :py:meth:`options <locust.clients.HttpSession.options>` 
methods. The HttpSession instance will preserve cookies between requests so that it can be used to log in 
to websites and keep a session between requests. The client attribute can also be referenced from the Locust 
instance's TaskSet instances so that it's easy to retrieve the client and make HTTP requests from within your 
tasks.

Here's a simple example that makes a GET request to the */about* path (in this case we assume *self* 
is an instance of a :py:class:`TaskSet <locust.core.TaskSet>` or :py:class:`HttpLocust <locust.core.Locust>` 
class:

.. code-block:: python

    response = self.client.get("/about")
    print("Response status code:", response.status_code)
    print("Response content:", response.text)

And here's an example making a POST request:

.. code-block:: python

    response = self.client.post("/login", {"username":"testuser", "password":"secret"})

Safe mode
---------
The HTTP client is configured to run in safe_mode. What this does is that any request that fails due to 
a connection error, timeout, or similar will not raise an exception, but rather return an empty dummy 
Response object. The request will be reported as a failure in Locust's statistics. The returned dummy 
Response's *content* attribute will be set to None, and its *status_code* will be 0.


.. _catch-response:

Manually controlling if a request should be considered successful or a failure
------------------------------------------------------------------------------

By default, requests are marked as failed requests unless the HTTP response code is OK (<400). 
Most of the time, this default is what you want. Sometimes however—for example when testing 
a URL endpoint that you expect to return 404, or testing a badly designed system that might 
return *200 OK* even though an error occurred—there's a need for manually controlling if 
locust should consider a request as a success or a failure.

One can mark requests as failed, even when the response code is OK, by using the 
*catch_response* argument and a with statement:

.. code-block:: python

    with self.client.get("/", catch_response=True) as response:
        if response.content != b"Success":
            response.failure("Got wrong response")

Just as one can mark requests with OK response codes as failures, one can also use **catch_response** 
argument together with a *with* statement to make requests that resulted in an HTTP error code still 
be reported as a success in the statistics:

.. code-block:: python

    with self.client.get("/does_not_exist/", catch_response=True) as response:
        if response.status_code == 404:
            response.success()


Grouping requests to URLs with dynamic parameters
-------------------------------------------------

It's very common for websites to have pages whose URLs contain some kind of dynamic parameter(s). 
Often it makes sense to group these URLs together in Locust's statistics. This can be done 
by passing a *name* argument to the :py:class:`HttpSession's <locust.clients.HttpSession>` 
different request methods. 

Example:

.. code-block:: python

    # Statistics for these requests will be grouped under: /blog/?id=[id]
    for i in range(10):
        self.client.get("/blog?id=%i" % i, name="/blog?id=[id]")


How to structure your test code
================================

It's important to remember that the locustfile.py is just an ordinary Python module that is imported 
by Locust. From this module you're free to import other python code just as you normally would 
in any Python program. The current working directory is automatically added to python's ``sys.path``, 
so any python file/module/packages that resides in the working directory can be imported using the 
python ``import`` statement.

For small tests, keeping all of the test code in a single ``locustfile.py`` should work fine, but for 
larger test suites, you'll probably want to split the code into multiple files and directories. 

How you structure the test source code is ofcourse entirely up to you, but we recommend that you 
follow Python best practices. Here's an example file structure of an imaginary Locust project:

* Project root

  * ``common/``
  
    * ``__init__.py``
    * ``auth.py``
    * ``config.py``
  * ``locustfile.py``
  * ``requirements.txt`` (External Python dependencies is often kept in a requirements.txt)

A project with multiple different locustfiles could also keep them in a separate subdirectory:

* Project root

  * ``common/``
  
    * ``__init__.py``
    * ``auth.py``
    * ``config.py``
  * ``locustfiles/``
  
    * ``api.py``
    * ``website.py``
  * ``requirements.txt``


With any ofthe above project structure, your locustfile can import common libraries using:

.. code-block:: python

    import common.auth
