.. _writing-a-locustfile:

======================
Writing a locustfile
======================

Now, lets look at a more complete/realistic example of what your tests might look like:

.. code-block:: python

    import time
    from locust import HttpUser, task, between

    class QuickstartUser(HttpUser):
        wait_time = between(1, 5)

        @task
        def hello_world(self):
            self.client.get("/hello")
            self.client.get("/world")

        @task(3)
        def view_items(self):
            for item_id in range(10):
                self.client.get(f"/item?id={item_id}", name="/item")
                time.sleep(1)

        def on_start(self):
            self.client.post("/login", json={"username":"foo", "password":"bar"})


.. rubric:: Let's break it down

.. code-block:: python

    import time
    from locust import HttpUser, task, between

A locust file is just a normal Python module, it can import code from other files or packages.

.. code-block:: python

    class QuickstartUser(HttpUser):

Here we define a class for the users that we will be simulating. It inherits from
:py:class:`HttpUser <locust.HttpUser>` which gives each user a ``client`` attribute,
which is an instance of :py:class:`HttpSession <locust.clients.HttpSession>`, that
can be used to make HTTP requests to the target system that we want to load test. When a test starts,
locust will create an instance of this class for every user that it simulates, and each of these
users will start running within their own green gevent thread.

For a file to be a valid locustfile it must contain at least one class inheriting from :py:class:`User <locust.User>`.

.. code-block:: python

    wait_time = between(1, 5)

Our class defines a ``wait_time`` that will make the simulated users wait between 1 and 5 seconds after each task (see below)
is executed. For more info see :ref:`wait-time`.

.. code-block:: python

    @task
    def hello_world(self):
        ...

Methods decorated with ``@task`` are the core of your locust file. For every running user,
Locust creates a greenlet (micro-thread), that will call those methods.

.. code-block:: python

    @task
    def hello_world(self):
        self.client.get("/hello")
        self.client.get("/world")

    @task(3)
    def view_items(self):
    ...

We've declared two tasks by decorating two methods with ``@task``, one of which has been given a higher weight (3).
When our ``QuickstartUser`` runs it'll pick one of the declared tasks - in this case either ``hello_world`` or
``view_items`` - and execute it. Tasks are picked at random, but you can give them different weighting. The above
configuration will make Locust three times more likely to pick ``view_items`` than ``hello_world``. When a task has
finished executing, the User will then sleep during its wait time (in this case between 1 and 5 seconds).
After its wait time it'll pick a new task and keep repeating that.

Note that only methods decorated with ``@task`` will be picked, so you can define your own internal helper methods any way you like.

.. code-block:: python

    self.client.get("/hello")

The ``self.client`` attribute makes it possible to make HTTP calls that will be logged by Locust. For information on how
to make other kinds of requests, validate the response, etc, see
`Using the HTTP Client <writing-a-locustfile.html#client-attribute-httpsession>`_.

.. note::

    HttpUser is not a real browser, and thus will not parse an HTML response to load resources or render the page. It will keep track of cookies though.

.. code-block:: python

    @task(3)
    def view_items(self):
        for item_id in range(10)
            self.client.get(f"/item?id={item_id}", name="/item")
            time.sleep(1)

In the ``view_items`` task we load 10 different URLs by using a variable query parameter.
In order to not get 10 separate entries in Locust's statistics - since the stats is grouped on the URL - we use
the :ref:`name parameter <name-parameter>` to group all those requests under an entry named ``"/item"`` instead.

.. code-block:: python

    def on_start(self):
        self.client.post("/login", json={"username":"foo", "password":"bar"})

Additionally we've declared an `on_start` method. A method with this name will be called for each simulated
user when they start. For more info see :ref:`on-start-on-stop`.

User class
==========

A user class represents one user (or a swarming locust if you will). Locust will spawn one
instance of the User class for each user that is being simulated. There are some common attributes that
a User class may define.

.. _wait-time:

wait_time attribute
-------------------

A User's :py:attr:`wait_time <locust.User.wait_time>` method makes it easy to introduce delays after
each task execution. If no `wait_time` is specified, the next task will be executed as soon as one finishes.

* :py:attr:`constant <locust.wait_time.constant>` for a fixed amount of time

* :py:attr:`between <locust.wait_time.between>` for a random time between a min and max value

For example, to make each user wait between 0.5 and 10 seconds between every task execution:

.. code-block:: python

    from locust import User, task, between

    class MyUser(User):
        @task
        def my_task(self):
            print("executing my_task")

        wait_time = between(0.5, 10)

* :py:attr:`constant_throughput <locust.wait_time.constant_throughput>` for an adaptive time that ensures the task runs (at most) X times per second.

* :py:attr:`constant_pacing <locust.wait_time.constant_pacing>` for an adaptive time that ensures the task runs (at most) once every X seconds  (it is the mathematical inverse of `constant_throughput`)

.. note::

    For example, if you want Locust to run 500 task iterations per second at peak load, you could use `wait_time = constant_throughput(0.1)` and a user count of 5000.

    Wait time can only constrain the throughput, not launch new Users to reach the target. So, in our example, the throughput will be less than 500 if the time for the task iteration exceeds 10 seconds.

    Wait time is applied *after* task execution, so if you have a high spawn rate/ramp up you may end up exceeding your target during rampup.

    Wait times apply to *tasks*, not requests.  If you, for example, specify `wait_time = constant_throughput(2)` and do two requests in your tasks your request rate/RPS will be 4 per User.

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

Other events
------------

See :ref:`extending locust using event hooks <extending_locust>` for other events and more examples of how to use them.

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
    :caption: Make a POST request, look at the response and implicitly reuse any session cookie we got for a second request

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

.. _rest:

REST/JSON APIs
--------------

Here's an example of how to call a REST API and validate the response:

.. code-block:: python

    from json import JSONDecodeError
    ...
    with self.client.post("/", json={"foo": 42, "bar": None}, catch_response=True) as response:
        try:
            if response.json()["greeting"] != "hello":
                response.failure("Did not get expected value in greeting")
        except JSONDecodeError:
            response.failure("Response could not be decoded as JSON")
        except KeyError:
            response.failure("Response did not contain expected key 'greeting'")

locust-plugins has a ready-made class for testing REST API:s called `RestUser <https://github.com/SvenskaSpel/locust-plugins/blob/master/examples/rest_ex.py>`_

.. _name-parameter:

Grouping requests
-----------------

It's very common for websites to have pages whose URLs contain some kind of dynamic parameter(s).
Often it makes sense to group these URLs together in User's statistics. This can be done
by passing a *name* argument to the :py:class:`HttpSession's <locust.clients.HttpSession>`
different request methods.

Example:

.. code-block:: python

    # Statistics for these requests will be grouped under: /blog/?id=[id]
    for i in range(10):
        self.client.get("/blog?id=%i" % i, name="/blog?id=[id]")

There may be situations where passing in a parameter into request function is not possible, such as when interacting with libraries/SDK's that
wrap a Requests session. An alternative say of grouping requests is provided By setting the ``client.request_name`` attribute

.. code-block:: python

    # Statistics for these requests will be grouped under: /blog/?id=[id]
    self.client.request_name="/blog?id=[id]"
    for i in range(10):
        self.client.get("/blog?id=%i" % i)
    self.client.request_name=None

If You want to chain multiple groupings with minimal boilerplate, you can use the ``client.rename_request()`` context manager.

.. code-block:: python

    @task
    def multiple_groupings_example(self):

        # Statistics for these requests will be grouped under: /blog/?id=[id]
        with self.client.rename_request("/blog?id=[id]"):
            for i in range(10):
                self.client.get("/blog?id=%i" % i)

        # Statistics for these requests will be grouped under: /article/?id=[id]
        with self.client.rename_request("/article?id=[id]"):
            for i in range(10):
                self.client.get("/article?id=%i" % i)



HTTP Proxy settings
-------------------
To improve performance, we configure requests to not look for HTTP proxy settings in the environment by setting
requests.Session's trust_env attribute to ``False``. If you don't want this you can manually set
``locust_instance.client.trust_env`` to ``True``. For further details, refer to the
`documentation of requests <https://requests.readthedocs.io/en/master/api/#requests.Session.trust_env>`_.

TaskSets
================================
TaskSets is a way to structure tests of hierarchical web sites/systems. You can :ref:`read more about it here <tasksets>`


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
  * ``my_locustfiles/``

    * ``api.py``
    * ``website.py``
  * ``requirements.txt``


With any of the above project structure, your locustfile can import common libraries using:

.. code-block:: python

    import common.auth
