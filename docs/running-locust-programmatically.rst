.. _running-locust-programmatically:

===============================
Running Locust programmatically
===============================

All of the options for running locust from the command-line can be used
programmatically within Python using the `locust.run_locust` function.

`locust.create_options()` will set up an options object with default 
values filled in. See below for API reference.

API Reference
=============

.. automodule:: locust.main
	:members: run_locust, create_options
