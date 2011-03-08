===
API
===


Locust class
============

.. autoclass:: locust.core.Locust
	:members: tasks, min_wait, max_wait, schedule_task



WebLocust class
===============

.. autoclass:: locust.core.WebLocust
	:members: client


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
