###
API
###


Locust class
============

.. autoclass:: locust.core.Locust
	:members: tasks, min_wait, max_wait, schedule_task, client
	
	.. autoattribute:: locust.core.LocustBase.min_wait
	.. autoattribute:: locust.core.LocustBase.max_wait
	.. autoattribute:: locust.core.LocustBase.tasks

TaskSet class
=============

.. autoclass:: locust.core.TaskSet
	:members: tasks, client, interrupt
	
	.. autoattribute:: locust.core.LocustBase.tasks


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


InterruptLocust Exception
=========================
.. autoexception:: locust.exception.InterruptLocust


.. _events:

Event hooks
===========

The event hooks are instances of the **locust.events.EventHook** class:

.. autoclass:: locust.events.EventHook

Available hooks
---------------

The wollowing event hooks are available under the **locust.events** module:

.. automodule:: locust.events
	:members: request_success, request_failure, locust_error, report_to_master, slave_report, hatch_complete, quitting

