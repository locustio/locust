.. _writing-a-locustfile:

======================
Writing a locustfile
======================

A locustfile is a normal python file. The only requirement is that it declares at least one class that inherits from the class :py:class:`User <locust.User>`. 

User class
==========

A user class represents one user (or a swarming locust if you will). Locust will spawn one 
instance of the User class for each user that is being simulated. There are some common attributes that 
a User class may define. 

.. _wait-time:

wait_time attribute
-------------------

A User's :py:attr:`wait_time <locust.User.wait_time>` method is an optional attribute used to determine
how long a simulated user should wait between executing tasks. If no :py:attr:`wait_time <locust.User.wait_time>` 
is specified, a new task will be executed as soon as one finishes.

There are three built in wait time functions: 

* :py:attr:`constant <locust.wait_time.constant>` for a fixed amount of time

* :py:attr:`between <locust.wait_time.between>` for a random time between a min and max value

* :py:attr:`constant_pacing <locust.wait_time.constant_pacing>` for an adaptive time that ensures the task runs (at most) once every X seconds

For example, to make each user wait between 0.5 and 10 seconds between every task execution:

.. code-block:: python

    from locust import User, task, between
        
    class MyUser(User):
        @task
        def my_task(self):
            print("executing my_task")

        wait_time = between(0.5, 10)

It's also possible to declare your own wait_time method directly on your class. 
For example, the following User class would sleep for one second, then two, then three, etc.

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

.. _on-start-on-stop:

on_start and on_stop methods
----------------------------

Users (and :ref:`TaskSets <tasksets>`) can declare an :py:meth:`on_start <locust.User.on_start>` method and/or
:py:meth:`on_stop <locust.User.on_stop>` method. A User will call its
:py:meth:`on_start <locust.User.on_start>` method when it starts running, and its
:py:meth:`on_stop <locust.User.on_stop>` method when it stops running. For a TaskSet, the
:py:meth:`on_start <locust.TaskSet.on_start>` method is called when a simulated user starts executing 
that TaskSet, and :py:meth:`on_stop <locust.TaskSet.on_stop>` is called when the simulated user stops 
executing that TaskSet (when :py:meth:`interrupt() <locust.TaskSet.interrupt>` is called, or the
user is killed).

Tasks
=====

When a load test is started, an instance of a User class will be created for each simulated user
and they will start running within their own green thread. When these users run they pick tasks that 
they execute, sleep for awhile, and then pick a new task and so on.

The tasks are normal python callables and - if we were load-testing an auction website - they could do 
stuff like "loading the start page", "searching for some product", "making a bid", etc. 

@task decorator
---------------

The easiest way to add a task for a User is by using the :py:meth:`task <locust.task>` decorator.

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

Another way to define the tasks of a User is by setting the :py:attr:`tasks <locust.User.tasks>` attribute.

The *tasks* attribute is either a list of Tasks, or a *<Task : int>* dict, where Task is either a 
python callable or a :ref:`TaskSet <tasksets>` class. If the task is a normal python function they 
receive a single argument which is the User instance that is executing the task.

Here is an example of a User task declared as a normal python function:

.. code-block:: python

    from locust import User, constant
    
    def my_task(user):
        pass
    
    class MyUser(User):
        tasks = [my_task]
        wait_time = constant(1)


If the tasks attribute is specified as a list, each time a task is to be performed, it will be randomly 
chosen from the *tasks* attribute. If however, *tasks* is a dict - with callables as keys and ints 
as values - the task that is to be executed will be chosen at random but with the int as ratio. So 
with a task that looks like this::

    {my_task: 3, another_task: 1}

*my_task* would be 3 times more likely to be executed than *another_task*. 

Internally the above dict will actually be expanded into a list (and the ``tasks`` attribute is updated) 
that looks like this::

    [my_task, my_task, my_task, another_task]

and then Python's ``random.choice()`` is used pick tasks from the list.


.. _tagging-tasks:

@tag decorator
--------------

By tagging tasks using the :py:func:`@tag <locust.tag>` decorator, you can be picky about what tasks are
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

Events
======

If you want to run some setup code as part of your test, it is often enough to put it at the module
level of your locustfile, but sometimes you need to do things at particular times in the run. For 
this need, Locust provides event hooks.

test_start and test_stop
------------------------

If you need to run some code at the start or stop of a load test, you should use the 
:py:attr:`test_start <locust.event.Events.test_start>` and :py:attr:`test_stop <locust.event.Events.test_stop>` 
events. You can set up listeners for these events at the module level of your locustfile:

.. code-block:: python

    from locust import events
    
    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        print("A new test is starting")
    
    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        print("A new test is ending")

When running Locust distributed the ``test_start`` and ``test_stop`` events will only be fired in the master node.

init
----

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

other events
------------

see :ref:`extending locust using event hooks <extending_locust>` for other events and more examples of how to use them.

HttpUser class
==============

:py:class:`HttpUser <locust.HttpUser>` is the most commonly used :py:class:`User <locust.User>`. It adds a :py:attr:`client <locust.HttpUser.client>` attribute which is used to make HTTP requests.

.. code-block:: python

    from locust import HttpUser, task, between
    
    class MyUser(HttpUser):
        wait_time = between(5, 15)
        
        @task(4)
        def index(self):
            self.client.get("/")
        
        @task(1)
        def about(self):
            self.client.get("/about/")


client attribute / HttpSession
------------------------------

:py:attr:`client <locust.HttpUser.client>` is an instance of :py:class:`HttpSession <locust.clients.HttpSession>`. HttpSession is a subclass/wrapper for 
:py:class:`requests.Session`, so its features are well documented and should be familiar to many. What HttpSession adds is mainly reporting of the request results into Locust (success/fail, response time, response length, name). 


It contains methods for all HTTP methods: :py:meth:`get <locust.clients.HttpSession.get>`, 
:py:meth:`post <locust.clients.HttpSession.post>`, :py:meth:`put <locust.clients.HttpSession.put>`, 
... 


Just like :py:class:`requests.Session`, it preserves cookies between requests so it can easily be used to log in to websites.

.. code-block:: python
    :caption: Make a POST request, look at the response and implicitly reuse any session cookies we got for a second request

    response = self.client.post("/login", {"username":"testuser", "password":"secret"})
    print("Response status code:", response.status_code)
    print("Response text:", response.text)
    response = self.client.get("/my-profile")

HttpSession catches any :py:class:`requests.RequestException` thrown by Session (caused by connection errors, timeouts or similar), instead returning a dummy 
Response object with *status_code* set to 0 and *content* set to None.


.. _catch-response:

Validating responses
--------------------

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

You can even avoid logging a request at all by throwing an exception and then catching it outside the with-block. Or you can throw a :ref:`locust exception <exceptions>`, like in the example below, and let Locust catch it.

.. code-block:: python

    from locust.exception import RescheduleTask
    ...
    with self.client.get("/does_not_exist/", catch_response=True) as response:
        if response.status_code == 404:
            raise RescheduleTask()


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

TaskSets
================================
TaskSets is a way to structure tests of hierarchial web sites/systems. You can :ref:`read more about it here <tasksets>`


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
