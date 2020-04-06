###
API
###


Locust class
============

.. autoclass:: locust.core.Locust
    :members: wait_time, tasks, weight, abstract, on_start, on_stop

HttpLocust class
================

.. autoclass:: locust.core.HttpLocust
    :members: wait_time, tasks, client, abstract


TaskSet class
=============

.. autoclass:: locust.core.TaskSet
    :members: locust, parent, wait_time, client, tasks, interrupt, schedule_task, on_start, on_stop

task decorator
==============

.. autofunction:: locust.core.task

SequentialTaskSet class
=======================

.. autoclass:: locust.sequential_taskset.SequentialTaskSet
    :members: locust, parent, wait_time, client, tasks, interrupt, schedule_task, on_start, on_stop


.. _wait_time_functions:

Built in wait_time functions
============================

.. automodule:: locust.wait_time
    :members: between, constant, constant_pacing

HttpSession class
=================

.. autoclass:: locust.clients.HttpSession
    :members: __init__, request, get, post, delete, put, head, options, patch

Response class
==============

This class actually resides in the `python-requests <http://python-requests.org>`_ library, 
since that's what Locust is using to make HTTP requests, but it's included in the API docs 
for locust since it's so central when writing locust load tests. You can also look at the 
:py:class:`Response <requests.Response>` class at the 
`requests documentation <http://python-requests.org>`_.

.. autoclass:: requests.Response
    :inherited-members:
    :noindex:

ResponseContextManager class
============================

.. autoclass:: locust.clients.ResponseContextManager
    :members: success, failure


InterruptTaskSet Exception
==========================
.. autoexception:: locust.exception.InterruptTaskSet


Environment class
=================
.. autoclass:: locust.env.Environment
    :members:


.. _events:

Event hooks
===========

Locust provide event hooks that can be used to extend Locus in various ways. 

The following event hooks are available under :py:attr:`Environment.events <locust.env.Environment.events>`, 
and there's also a reference to these events under ``locust.events`` that can be used at the module level 
of locust scripts (since the Environment instance hasn't been created when the locustfile is imported).

.. autoclass:: locust.event.Events
    :members:


EventHook class
---------------

The event hooks are instances of the **locust.events.EventHook** class:

.. autoclass:: locust.event.EventHook

.. note::

    It's highly recommended that you add a wildcard keyword argument in your event listeners
    to prevent your code from breaking if new arguments are added in a future version.
