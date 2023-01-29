.. _increase-performance:

==============================================================
Increase performance with a faster HTTP client
==============================================================

Locust's default HTTP client uses `python-requests <http://www.python-requests.org/>`_. 
It provides a nice API that many python developers are familiar with, and is very well-maintained. But if you're planning to run tests with very high throughput and have limited hardware for running Locust, it is sometimes not efficient enough.

Because of this, Locust also comes with :py:class:`FastHttpUser <locust.contrib.fasthttp.FastHttpUser>` which
uses `geventhttpclient <https://github.com/gwik/geventhttpclient/>`_ instead.
It provides a very similar API and uses significantly less CPU time, sometimes increasing the maximum number of requests per second on a given hardware by as much as 5x-6x.

It is impossible to say how many requests Locust can do on your particular hardware, using your particular test plan, so you'll need to test it out. Check Locust's console output, it will log a warning if it is limited by CPU.

In a *best case* scenario (doing small requests inside a ``while True``-loop) a single Locust process (limited to one CPU core) can do around **16000 requests per second using FastHttpUser, and 4000 using HttpUser** (tested on a 2021 M1 MacBook Pro and Python 3.11)

The relative improvement may be even bigger with bigger request payloads, but it may also be smaller if your test is doing CPU intensive things not related to requests.

Of course, in reality you should run :ref:`one locust process per CPU core <running-distributed>`.

.. note::

    As long as your load generator CPU is not overloaded, FastHttpUser's response times should be almost identical to those of HttpUser. It does not make individual requests faster.

How to use FastHttpUser
===========================

Just subclass FastHttpUser instead of HttpUser::

    from locust import task, FastHttpUser
    
    class MyUser(FastHttpUser):
        @task
        def index(self):
            response = self.client.get("/")

Concurrency
===========

A single FastHttpUser/geventhttpclient session can run concurrent requests, you just have to launch greenlets for each request::

    @task
    def t(self):
        def concurrent_request(url):
            self.client.get(url)

        pool = gevent.pool.Pool()
        urls = ["/url1", "/url2", "/url3"]
        for url in urls:
            pool.spawn(concurrent_request, url)
        pool.join()


.. note::

    FastHttpUser/geventhttpclient is very similar to HttpUser/python-requests, but sometimes there are subtle differences. This is particularly true if you work with the client library's internals, e.g. when manually managing cookies.

.. _rest:

REST
====

FastHttpUser provides a ``rest`` method for testing REST/JSON HTTP interfaces. It is a wrapper for ``self.client.request`` that:
    
* Parses the JSON response to a dict called ``js`` in the response object. Marks the request as failed if the response was not valid JSON.
* Defaults ``Content-Type`` and ``Accept`` headers to ``application/json``
* Sets ``catch_response=True`` (so always use a :ref:`with-block <catch-response>`)
* Catches any unhandled exceptions thrown inside your with-block, marking the sample as failed (instead of exiting the task immediately without even firing the request event)

.. code-block:: python

    from locust import task, FastHttpUser

    class MyUser(FastHttpUser):
        @task
        def t(self):
            with self.rest("POST", "/", json={"foo": 1}) as resp:
                if resp.js is None:
                    pass # no need to do anything, already marked as failed
                elif "bar" not in resp.js:
                    resp.failure(f"'bar' missing from response {resp.text}")
                elif resp.js["bar"] != 42:
                    resp.failure(f"'bar' had an unexpected value: {resp.js['bar']}")

For a complete example, see `rest.py <https://github.com/locustio/locust/blob/master/examples/rest.py>`_. That also shows how you can use inheritance to provide behaviours specific to your REST API that are common to multiple requests/testplans.

.. note::

    This feature is new and details of its interface/implementation may change in new versions of Locust.


API
===


FastHttpUser class
--------------------

.. autoclass:: locust.contrib.fasthttp.FastHttpUser
    :members: network_timeout, connection_timeout, max_redirects, max_retries, insecure, concurrency, client_pool, rest, rest_


FastHttpSession class
---------------------

.. autoclass:: locust.contrib.fasthttp.FastHttpSession
    :members: request, get, post, delete, put, head, options, patch

.. autoclass:: locust.contrib.fasthttp.FastResponse
    :members: content, text, json, headers
