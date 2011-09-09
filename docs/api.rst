###
API
###


Locust class
============

.. autoclass:: locust.core.Locust
	:members: tasks, min_wait, max_wait, schedule_task, client


HttpBrowser class
=================

.. autoclass:: locust.clients.HttpBrowser
	:members: __init__, get, post

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


Event hooks
===========

The event hooks are instances of the **locust.events.EventHook** class:

.. autoclass:: locust.events.EventHook

Available hooks
---------------

The wollowing event hooks are available under the **locust.events** module:

.. automodule:: locust.events
	:members: request_success, request_failure, locust_error, report_to_master, slave_report, hatch_complete

