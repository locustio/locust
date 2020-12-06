.. _tasksets:

TaskSet class
=============

If you are performance testing a website that is structured in a hierarchical way, with 
sections and sub-sections, it may be useful to structure your load test the same way. 
For this purpose, Locust provides the TaskSet class. It is a collection of tasks that will 
be executed much like the ones declared directly on a User class. 

.. note::

    TaskSets are an advanced feature and only rarely useful. A lot of the time, you're better off
    using regular Python loops and control statements to achieve the same thing. There are a few 
    gotchas as well, the most frequent one being forgetting to call self.interrupt()

.. code-block:: python

    from locust import User, TaskSet, constant
    
    class ForumSection(TaskSet):
        wait_time = constant(1)

        @task(10)
        def view_thread(self):
            pass
        
        @task
        def create_thread(self):
            pass
        
        @task
        def stop(self):
            self.interrupt()
    
    class LoggedInUser(User):
        wait_time = constant(5)
        tasks = {ForumSection:2}
        
        @task
        def my_task(self):
            pass

A TaskSet can also be inlined directly under a User/TaskSet class using the @task decorator:

.. code-block:: python

    class MyUser(User):
        @task
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

The TaskSet instance contains a reference to the User - ``self.user``. It also has a shortcut to its 
User's client attribute. So you can make a request using ``self.client.request()``,
just like if your task was defined directly on an HttpUser.


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
You can tag TaskSets using the :py:func:`@tag <locust.tag>` decorator in a similar way to normal tasks,
but there are some nuances worth mentioning. Tagging a TaskSet will automatically apply the tag(s) to 
all of the TaskSet's tasks. Furthermore, if you tag a task within a nested TaskSet, Locust will execute 
that task even if the TaskSet isn't tagged.


.. _sequential-taskset:

SequentialTaskSet class
=======================

:py:class:`SequentialTaskSet <locust.SequentialTaskSet>` is a TaskSet whose tasks will be executed 
in the order that they are declared. It is possible to nest SequentialTaskSets 
within a TaskSet and vice versa.

For example, the following code will request URLs /1-/4 in order, and then repeat.

.. code-block:: python
    
    def function_task(taskset):
        taskset.client.get("/3")
    
    class SequenceOfTasks(SequentialTaskSet):
        @task
        def first_task(self):
            self.client.get("/1")
            self.client.get("/2")
        
        # you can still use the tasks property to specify a list of tasks
        tasks = [function_task]
        
        @task
        def last_task(self):
            self.client.get("/4")

Note that you dont need SequentialTaskSets to just do some requests in order. It is often easier to 
just do a whole user flow in a single task.
