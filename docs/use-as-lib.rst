.. _use-as-lib:

==========================
Using Locust as a library
==========================

It is possible to start a load test from your own Python code, instead of running Locust using the ``locust`` command.

Start by creating an :py:class:`Environment <locust.env.Environment>` instance:

.. code-block:: python

    from locust.env import Environment
    
    env = Environment(user_classes=[MyTestUser])

The :py:class:`Environment <locust.env.Environment>` instance's 
:py:meth:`create_local_runner <locust.env.Environment.create_local_runner>`, 
:py:meth:`create_master_runner <locust.env.Environment.create_master_runner>` or 
:py:meth:`create_worker_runner <locust.env.Environment.create_worker_runner>` can then be used to start a 
:py:class:`Runner <locust.runners.Runner>` instance, which can be used to start a load test:

.. code-block:: python

    env.create_local_runner()
    env.runner.start(5000, spawn_rate=20)
    env.runner.greenlet.join()

It is also possible to bypass the dispatch and distribution logic, and manually control the spawned users:

.. code-block:: python

    new_users = env.runner.spawn_users({MyUserClass.__name__: 2})
    new_users[1].my_custom_token = "custom-token-2"
    new_users[0].my_custom_token = "custom-token-1"

The above example only works on standalone mode and is an experimental feature, meaning that it could be
removed in future versions. But it's useful if you want to have fine-grained control on the spawned users. 

.. note::

    Do not attempt to create a master runner and worker(s) in the same Python process. It does not work, and even if it did, it would not give you better performance than running a single LocalRunner. Every worker *must* run in its own process, there is no way around that.

We could also use the :py:class:`Environment <locust.env.Environment>` instance's 
:py:meth:`create_web_ui <locust.env.Environment.create_web_ui>` method to start a Web UI that can be used 
to view the stats, and to control the runner (e.g. start and stop load tests):

.. code-block:: python

    env.create_local_runner()
    env.create_web_ui()
    env.web_ui.greenlet.join()

Full example
============

.. literalinclude:: ../examples/use_as_lib.py
    :language: python
