==========================
Using Locust as a library
==========================

It's possible to use Locust as a library, instead of running Locust using the ``locust`` command.

To run Locust as a library you need to create an :py:class:`Environment <locust.env.Environment>` instance:

.. code-block:: python

    from locust.env import Environment
    
    env = Environment(locust_classes=[MyTestUser])

The :py:class:`Environment <locust.env.Environment>` instance's 
:py:meth:`create_local_runner <locust.env.Environment.create_local_runner>`, 
:py:meth:`create_master_runner <locust.env.Environment.create_master_runner>` or 
:py:meth:`create_worker_runner <locust.env.Environment.create_worker_runner> can then be used to start a 
:py:class:`LocustRunner <locust.runners.LocustRunner>` instance, which can be used to start a load test:

.. code-block:: python

    runner = env.create_local_runner()
    runner.start(5000, hatch_rate=20)
    runner.greenlet.join()

We could also use the :py:class:`Environment <locust.env.Environment>` instance's 
:py:meth:`create_web_ui <locust.env.Environment.create_web_ui>` to start a Web UI that can be used view 
the stats, and to control the runner (e.g. start and stop load tests):

.. code-block:: python

    runner = env.create_local_runner()
    web_ui = Environment.create_web_ui()
    web_ui.greenlet.join()


Full example
============

.. literalinclude:: ../examples/use_as_lib.py
    :language: python
