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


HttpSession class
=================

.. autoclass:: locust.clients.HttpSession
	:members: __init__, request, get, post, delete, put, head, options, patch

HttpResponse class
==================

.. autoclass:: locust.clients.HttpResponse
	:members: code, data, url, info


@require_once decorator
=======================

.. autofunction:: locust.core.require_once

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

