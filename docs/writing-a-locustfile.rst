======================
Writing a locustfile
======================

A locustfile is a normal python file. The only requirement is that it declares at least one class -
let's call it the user class - that inherits from the class :py:class:`User <locust.User>`. 

User class
==========

A user class represents one user (or a swarming locust if you will). Locust will spawn (hatch) one 
instance of the User class for each user that is being simulated. There are a few attributes that 
a User class should typically define. 

.. _wait-time:

wait_time attribute
-------------------

In addition to the *tasks* attribute, one should also declare a 
:py:attr:`wait_time <locust.User.wait_time>` method. It's used to determine
for how long a simulated user will wait between executing tasks. Locust comes with a few built in 
functions that return a few common wait_time methods.

The most common one is :py:attr:`between <locust.wait_time.between>`. It's used to make the simulated
users wait a random time between a min and max value after each task execution. Other built in 
wait time functions are :py:attr:`constant <locust.wait_time.constant>` and 
:py:attr:`constant_pacing <locust.wait_time.constant_pacing>`.

With the following locustfile, each user would wait between 5 and 15 seconds between tasks:

.. code-block:: python

    from locust import User, task, between
        
    class MyUser(User):
        @task
        def my_task(self):
            print("executing my_task")

        wait_time = between(5, 15)

The wait_time method should return a number of seconds (or fraction of a second) and can also 
be declared on a TaskSet class, in which case it will only be used for that TaskSet.

It's also possible to declare your own wait_time method directly on a User or TaskSet class. The
following User class would start sleeping for one second and then one, two, three, etc.

.. code-block:: python

    class MyUser(User):
        last_wait_time = 0
        
        def wait_time(self):
            self.last_wait_time += 1
            return self.last_wait_time

        ...
    


weight attribute
----------------

If more than one user class exists in the file, and no user classes are specified on the command line,
Locust will spawn an equal number of each of the user classes. You can also specify which of the 
user classes to use from the same locustfile by passing them as command line arguments:

.. code-block:: console

    $ locust -f locust_file.py WebUser MobileUser

If you wish to simulate more users of a certain type you can set a weight attribute on those
classes. Say for example, web users are three times more likely than mobile users:

.. code-block:: python

    class WebUser(User):
        weight = 3
        ...

    class MobileUser(User):
        weight = 1
        ...


host attribute
--------------

The host attribute is a URL prefix (i.e. "http://google.com") to the host that is to be loaded. 
Usually, this is specified in Locust's web UI or on the command line, using the 
:code:`--host` option, when locust is started. 

If one declares a host attribute in the user class, it will be used in the case when no :code:`--host` 
is specified on the command line or in the web request.

tasks attribute
---------------

A User class can have tasks declared as methods under it using the :py:func:`@task <locust.task>` decorator, but one can also
specify tasks using the *tasks* attribute which is described in more details :ref:`below <tasks-attribute>`.

environment attribute
---------------------

A reference to the :py:attr:`environment <locust.env.Environment>` in which the user is running. Use this to interact with 
the environment, or the :py:attr:`runner <locust.runners.Runner>` which it contains. E.g. to stop the runner from a task method:

.. code-block:: python
    
    self.environment.runner.quit()

If run on a standalone locust instance, this will stop the entire run. If run on worker node, it will stop that particular node.

Tasks
=====

When a load test is started, an instance of a User class will be created for each simulated user
and they will start running within their own green thread. When these users run they pick tasks that 
they execute, sleeps for awhile, and then picks a new task and so on. 

The tasks are normal python callables and - if we were load-testing an auction website - they could do 
stuff like "loading the start page", "searching for some product", "making a bid", etc. 

Declaring tasks
---------------

The typical way of declaring tasks for a User class (or a TaskSet) it to use the
:py:meth:`task <locust.task>` decorator.

Here is an example:

.. code-block:: python

    from locust import User, task, constant

    class MyUser(User):
        wait_time = constant(1)
        
        @task
        def my_task(self):
            print("User instance (%r) executing my_task" % self)

**@task** takes an optional weight argument that can be used to specify the task's execution ratio. In 
the following example *task2* will have twice the chance of being picked as *task1*:

.. code-block:: python
    
    from locust import User, task, between
    
    class MyUser(User):
        wait_time = between(5, 15)
        
        @task(3)
        def task1(self):
            pass
        
        @task(6)
        def task2(self):
            pass


.. _tasks-attribute:

tasks attribute
---------------

Using the @task decorator to declare tasks is a convenience, and usually the best way to do 
it. However, it's also possible to define the tasks of a User or TaskSet by setting the
:py:attr:`tasks <locust.User.tasks>` attribute (using the @task decorator will actually
just populate the *tasks* attribute).

The *tasks* attribute is either a list of Task, or a *<Task : int>* dict, where Task is either a 
python callable or a TaskSet class (more on that below). If the task is a normal python function they 
receive a single argument which is the User instance that is executing the task.

Here is an example of a User task declared as a normal python function:

.. code-block:: python

    from locust import User, constant
    
    def my_task(l):
        pass
    
    class MyUser(User):
        tasks = [my_task]
        wait_time = constant(1)


If the tasks attribute is specified as a list, each time a task is to be performed, it will be randomly 
chosen from the *tasks* attribute. If however, *tasks* is a dict - with callables as keys and ints 
as values - the task that is to be executed will be chosen at random but with the int as ratio. So 
with a tasks that looks like this::

    {my_task: 3, another_task: 1}

*my_task* would be 3 times more likely to be executed than *another_task*. 

Internally the above dict will actually be expanded into a list (and the ``tasks`` attribute is updated) 
that looks like this::

    [my_task, my_task, my_task, another_task]

and then Python's ``random.choice()`` is used pick tasks from the list.


.. _tagging-tasks:

Tagging tasks
-------------

By tagging tasks using the `tag <locust.tag>` decorator, you can be picky about what tasks are
executed during the test using the :code:`--tags` and :code:`--exclude-tags` arguments.  Consider
the following example:

.. code-block:: python

    from locust import User, constant, task, tag

    class MyUser(User):
        wait_time = constant(1)

        @tag('tag1')
        @task
        def task1(self):
            pass

        @tag('tag1', 'tag2')
        @task
        def task2(self):
            pass

        @tag('tag3')
        @task
        def task3(self):
            pass

        @task
        def task4(self):
            pass

If you started this test with :code:`--tags tag1`, only *task1* and *task2* would be executed
during the test. If you started it with :code:`--tags tag2 tag3`, only *task2* and *task3* would be
executed.

:code:`--exclude-tags` will behave in the exact opposite way. So, if you start the test with
:code:`--exclude-tags tag3`, only *task1*, *task2*, and *task4* will be executed. Exclusion always
wins over inclusion, so if a task has a tag you've included and a tag you've excluded, it will not
be executed.



TaskSet class
=============

Since real websites are usually built up in an hierarchical way, with multiple sub-sections, 
locust has the TaskSet class. A locust task can not only be a Python callable, but also a 
TaskSet class. A TaskSet is a collection of locust tasks that will be executed much like the 
tasks declared directly on a User class, with the user sleeping in between task executions.
Here's a short example of a locustfile that has a TaskSet:

.. code-block:: python

    from locust import User, TaskSet, between
    
    class ForumSection(TaskSet):
        @task(10)
        def view_thread(self):
            pass
        
        @task(1)
        def create_thread(self):
            pass
        
        @task(1)
        def stop(self):
            self.interrupt()
    
    class LoggedInUser(User):
        wait_time = between(5, 120)
        tasks = {ForumSection:2}
        
        @task
        def index_page(self):
            pass

A TaskSet can also be inlined directly under a User/TaskSet class using the @task decorator:

.. code-block:: python

    class MyUser(User):
        @task(1)
        class MyTaskSet(TaskSet):
            ...

The tasks of a TaskSet class can be other TaskSet classes, allowing them to be nested any number 
of levels. This allows us to define a behaviour that simulates users in a more realistic way. 

For example we could define TaskSets with the following structure::

    - Main user behaviour
      - Index page
      - Forum page
        - Read thread
          - Reply
        - New thread
        - View next page
      - Browse categories
        - Watch movie
        - Filter movies
      - About page

When a running User thread picks a TaskSet class for execution an instance of this class will
be created and execution will then go into this TaskSet. What happens then is that one of the 
TaskSet's tasks will be picked and executed, and then the thread will sleep for a duration specified 
by the User's wait_time function (unless a ``wait_time`` function has been declared directly on
the TaskSet class, in which case it'll use that function instead), then pick a new task from the 
TaskSet's tasks, wait again, and so on.



Interrupting a TaskSet
----------------------

One important thing to know about TaskSets is that they will never stop executing their tasks, and 
hand over execution back to their parent User/TaskSet, by themselves. This has to be done by the
developer by calling the :py:meth:`TaskSet.interrupt() <locust.TaskSet.interrupt>` method. 

.. autofunction:: locust.TaskSet.interrupt
    :noindex:

In the following example, if we didn't have the stop task that calls ``self.interrupt()``, the 
simulated user would never stop running tasks from the Forum taskset once it has went into it:

.. code-block:: python

    class RegisteredUser(User):
        @task
        class Forum(TaskSet):
            @task(5)
            def view_thread(self):
                pass
            
            @task(1)
            def stop(self):
                self.interrupt()
        
        @task
        def frontpage(self):
            pass

Using the interrupt function, we can - together with task weighting - define how likely it 
is that a simulated user leaves the forum.


Differences between tasks in TaskSet and User classes
-------------------------------------------------------

One difference for tasks residing under a TaskSet, compared to tasks residing directly under a User,
is that the argument that they are passed when executed (``self`` for tasks declared as methods with 
the :py:func:`@task <locust.task>` decorator) is a reference to the TaskSet instance, instead of 
the User instance. The User instance can be accessed from within a TaskSet instance through the
:py:attr:`TaskSet.user <locust.TaskSet.user>`. TaskSets also contains a convenience 
:py:attr:`client <locust.TaskSet.client>` attribute that refers to the client attribute on the 
User instance.


Referencing the User instance, or the parent TaskSet instance
---------------------------------------------------------------

A TaskSet instance will have the attribute :py:attr:`user <locust.TaskSet.user>` point to
its User instance, and the attribute :py:attr:`parent <locust.TaskSet.parent>` point to its
parent TaskSet instance.


Tags and TaskSets
------------------
You can tag TaskSets using the `tag <locust.tag>` decorator in a similar way to normal tasks, as
described `above <tagging-tasks>`, but there are some nuances worth mentioning. Tagging a TaskSet
will automatically apply the tag(s) to all of the TaskSet's tasks. Furthermore, if you tag a task
within a nested TaskSet, locust will execute that task even if the TaskSet isn't tagged.


.. _sequential-taskset:

SequentialTaskSet class
=======================

:py:class:`SequentialTaskSet <locust.SequentialTaskSet>` is a TaskSet but its 
tasks will be executed in the order that they are declared. Weights are ignored for tasks on a 
SequentialTaskSet class. It is possible to nest SequentialTaskSets within a TaskSet and vice versa.

.. code-block:: python
    
    def function_task(taskset):
        pass
    
    class SequenceOfTasks(SequentialTaskSet):
        @task
        def first_task(self):
            pass
        
        tasks = [function_task]
        
        @task
        def second_task(self):
            pass

        @task
        def third_task(self):
            pass

In the above example, the tasks are executed in the order of declaration: 

1. ``first_task``
2. ``function_task``
3. ``second_task``
4. ``third_task``

and then it will start over at ``first_task`` again.


.. _on-start-on-stop:


on_start and on_stop methods
============================

User and TaskSet classes can declare an :py:meth:`on_start <locust.User.on_start>` method and/or
:py:meth:`on_stop <locust.TaskSet.on_stop>` method. A User will call it's
:py:meth:`on_start <locust.User.on_start>` method when it starts running, and it's
:py:meth:`on_stop <locust.User.on_stop>` method when it stops running. For a TaskSet, the
:py:meth:`on_start <locust.TaskSet.on_start>` method is called when a simulated user starts executing 
that TaskSet, and :py:meth:`on_stop <locust.TaskSet.on_stop>` is called when the simulated user stops 
executing that TaskSet (when :py:meth:`interrupt() <locust.TaskSet.interrupt>` is called, or the
user is killed).

test_start and test_stop events
===============================

If you need to run some code at the start or stop of a load test, you should use the 
:py:attr:`test_start <locust.event.Events.test_start>` and :py:attr:`test_stop <locust.event.Events.test_stop>` 
events. You can set up listeners for these events at the module level of your locustfile:

.. code-block:: python

    from locust import events
    
    @events.test_start.add_listener
    def on_test_start(**kwargs):
        print("A new test is starting")
    
    @events.test_stop.add_listener
    def on_test_stop(**kwargs):
        print("A new test is ending")

When running Locust distributed the ``test_start`` and ``test_stop`` events will only be fired in the master node.

init event
==========

The ``init`` event is triggered at the beginning of each Locust process. This is especially useful in distributed mode
where each worker process (not each user) needs a chance to do some initialization. For example, let's say you have some
global state that all users spawned from this process will need:

.. code-block:: python

    from locust import events
    from locust.runners import MasterRunner

    @events.init.add_listener
    def on_locust_init(environment, **kwargs):
        if isinstance(environment.runner, MasterRunner):
            print("I'm on master node")
        else:
            print("I'm on a worker or standalone node")


Making HTTP requests
=====================

So far, we've only covered the task scheduling part of a User. In order to actually load test
a system we need to make HTTP requests. To help us do this, the :py:class:`HttpLocust <locust.HttpUser>`
class exists. When using this class, each instance gets a 
:py:attr:`client <locust.User.client>` attribute which will be an instance of
:py:attr:`HttpSession <locust.clients.HttpSession>` which can be used to make HTTP requests.

.. autoclass:: locust.HttpUser
    :members: client
    :noindex:

When inheriting from the HttpUser class, we can use its client attribute to make HTTP requests
against the server. Here is an example of a locust file that can be used to load test a site 
with two URLs; **/** and **/about/**:

.. code-block:: python

    from locust import HttpUser, task, between
    
    class MyUser(HttpUser):
        wait_time = between(5, 15)
        
        @task(2)
        def index(self):
            self.client.get("/")
        
        @task(1)
        def about(self):
            self.client.get("/about/")

Using the above User class, each simulated user will wait between 5 and 15 seconds
between the requests, and **/** will be requested twice as much as **/about/**.


Using the HTTP client
----------------------

Each instance of HttpUser has an instance of :py:class:`HttpSession <locust.clients.HttpSession>`
in the *client* attribute. The HttpSession class is actually a subclass of 
:py:class:`requests.Session` and can be used to  make HTTP requests, that will be reported to User's
statistics, using the :py:meth:`get <locust.clients.HttpSession.get>`, 
:py:meth:`post <locust.clients.HttpSession.post>`, :py:meth:`put <locust.clients.HttpSession.put>`, 
:py:meth:`delete <locust.clients.HttpSession.delete>`, :py:meth:`head <locust.clients.HttpSession.head>`, 
:py:meth:`patch <locust.clients.HttpSession.patch>` and :py:meth:`options <locust.clients.HttpSession.options>` 
methods. The HttpSession instance will preserve cookies between requests so that it can be used to log in 
to websites and keep a session between requests. The client attribute can also be referenced from the User
instance's TaskSet instances so that it's easy to retrieve the client and make HTTP requests from within your 
tasks.

Here's a simple example that makes a GET request to the */about* path (in this case we assume *self* 
is an instance of a :py:class:`TaskSet <locust.TaskSet>` or :py:class:`HttpUser <locust.HttpUser>`
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
Response object. The request will be reported as a failure in User's statistics. The returned dummy
Response's *content* attribute will be set to None, and its *status_code* will be 0.


.. _catch-response:

Manually controlling if a request should be considered successful or a failure
------------------------------------------------------------------------------

Requests are considered successful if the HTTP response code is OK (<400), but it is often useful to 
do some additional validation of the response.

You can mark a request as failed by using the *catch_response* argument, a *with*-statement and 
a call to *response.failure()*

.. code-block:: python

    with self.client.get("/", catch_response=True) as response:
        if response.text != "Success":
            response.failure("Got wrong response")
        elif response.elapsed.total_seconds() > 0.5:
            response.failure("Request took too long")


You can also mark a request as successful, even if the response code was bad:

.. code-block:: python

    with self.client.get("/does_not_exist/", catch_response=True) as response:
        if response.status_code == 404:
            response.success()


.. _name-parameter:

Grouping requests to URLs with dynamic parameters
-------------------------------------------------

It's very common for websites to have pages whose URLs contain some kind of dynamic parameter(s). 
Often it makes sense to group these URLs together in User's statistics. This can be done
by passing a *name* argument to the :py:class:`HttpSession's <locust.clients.HttpSession>` 
different request methods. 

Example:

.. code-block:: python

    # Statistics for these requests will be grouped under: /blog/?id=[id]
    for i in range(10):
        self.client.get("/blog?id=%i" % i, name="/blog?id=[id]")


HTTP Proxy settings
-------------------
To improve performance, we configure requests to not look for HTTP proxy settings in the environment by setting 
requests.Session's trust_env attribute to ``False``. If you don't want this you can manually set 
``locust_instance.client.trust_env`` to ``True``. For further details, refer to the 
`documentation of requests <https://requests.readthedocs.io/en/master/api/#requests.Session.trust_env>`_.


How to structure your test code
================================

It's important to remember that the locustfile.py is just an ordinary Python module that is imported 
by Locust. From this module you're free to import other python code just as you normally would 
in any Python program. The current working directory is automatically added to python's ``sys.path``, 
so any python file/module/packages that resides in the working directory can be imported using the 
python ``import`` statement.

For small tests, keeping all of the test code in a single ``locustfile.py`` should work fine, but for 
larger test suites, you'll probably want to split the code into multiple files and directories. 

How you structure the test source code is of course entirely up to you, but we recommend that you 
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


With any of the above project structure, your locustfile can import common libraries using:

.. code-block:: python

    import common.auth
