===
API
===


Locust class
============

.. autoclass:: locust.core.Locust
	:members: tasks, min_wait, max_wait



WebLocust class
===============

.. autoclass:: locust.core.WebLocust
	:members: client


HttpBrowser class
=================

.. autoclass:: locust.clients.HttpBrowser
	:members: __init__, get, post


@require_once decorator
=======================

.. autofunction:: locust.core.require_once

InterruptLocust Exception
=========================
.. autoexception:: locust.exception.InterruptLocust
