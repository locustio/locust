:orphan:
.. _tasksets:

TaskSet class
=============

If you are performance testing a website that is structured in a hierarchical way, with 
sections and sub-sections, it may be useful to structure your load test the same way. 
For this purpose, Locust provides the TaskSet class. It is a collection of tasks that will 
be executed much like the ones declared directly on a User class. 

.. note::

    TaskSets are an advanced feature and only rarely useful. Most of the time, you're better off
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
in the order that they are declared. If the  *<Task : int>* dictionary is used, each task will be repeated by the amount
given by the integer at the point of declaration. It is possible to nest SequentialTaskSets
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
        
        # you can still use the tasks attribute to specify a list or dict of tasks
        tasks = [function_task]
        # tasks = {function_task: 1}
        
        @task
        def last_task(self):
            self.client.get("/4")

Note that you dont need SequentialTaskSets to just do some requests in order. It is often easier to 
just do a whole user flow in a single task.

.. _markov-taskset:

MarkovTaskSet class
===================

:py:class:`MarkovTaskSet <locust.MarkovTaskSet>` is a TaskSet that defines a probabilistic sequence of tasks 
using a Markov chain. Unlike regular TaskSets where tasks are chosen randomly based on weight, MarkovTaskSets 
allow you to define specific transitions between tasks with associated probabilities.

This is useful for modeling user behavior where the next action depends on the current state, creating more 
realistic user flows. For example, after viewing a product, a user might be more likely to add it to cart than 
to log out.

.. note::

    MarkovTaskSets require at least one task with transitions defined. All tasks must eventually be reachable from the
    first task, and tags are not supported with MarkovTaskSets as they could make the Markov chain invalid.

.. code-block:: python

    from locust import User, constant
    from locust.user.markov_taskset import MarkovTaskSet, transition, transitions

    class ShoppingBehavior(MarkovTaskSet):
        wait_time = constant(1)
        
        @transition("view_product")
        def browse_catalog(self):
            self.client.get("/catalog")
        
        @transitions({
            "add_to_cart": 3,  # Higher probability
            "browse_catalog": 1,
            "checkout": 1
        })
        def view_product(self):
            self.client.get("/product/1")
        
        @transitions(["view_product", "checkout"])
        def add_to_cart(self):
            self.client.post("/cart/add", json={"product_id": 1})
        
        @transition("browse_catalog")
        def checkout(self):
            self.client.post("/checkout")
    
    class ShopperUser(HttpUser):
        host = "http://localhost"
        tasks = {ShoppingBehavior: 1}

In this example, after browsing the catalog, the user will always view a product. After viewing a product, 
the user has a 60% chance (3/5) of adding it to cart, a 20% chance (1/5) of returning to browsing, and a 
20% chance (1/5) of going directly to checkout.

Defining Transitions
--------------------

MarkovTaskSet provides two decorators for defining transitions between tasks:

1. ``@transition(task_name, weight=1)``: Defines a single transition to another task.

   .. code-block:: python
   
       @transition("next_task")
       def current_task(self):
           pass

2. ``@transitions(weights)``: Defines multiple transitions at once. The ``weights`` parameter can be:
   
   - A dictionary mapping task names to weights:
   
     .. code-block:: python
     
         @transitions({
             "task_a": 3,
             "task_b": 1
         })
         def current_task(self):
             pass
   
   - A list of task names or (task_name, weight) tuples:
   
     .. code-block:: python
     
         @transitions(["task_a", ("task_b", 2)])
         def current_task(self):
             pass
   
