.. _increase-performance:

==============================================================
Increase performance with a faster HTTP client
==============================================================

Locust's default HTTP client uses `python-requests <http://www.python-requests.org/>`_. 
It provides a nice API that many python developers are familiar with, and is very well-maintained. But if you're planning to run tests with very high throughput and have limited hardware for running Locust, it is sometimes not efficient enough.

Because of this, Locust also comes with :py:class:`FastHttpUser <locust.contrib.fasthttp.FastHttpUser>` which
uses `geventhttpclient <https://github.com/gwik/geventhttpclient/>`_ instead.
It provides a very similar API and uses significantly less CPU time, sometimes increasing the maximum number of requests per second on a given hardware by as much as 5x-6x.

It is impossible to say what your particular hardware can handle, but in a best case scenario
a test using FastHttpUsers will be able to do close to 5000 requests per second per core, instead of around 850 for HttpUser (tested on a 2018 MacBook Pro i7 2.6GHz). In reality your results may vary, and you'll see smaller gains if your load tests also do other CPU-intensive things.

.. note::

    As long as your load generator CPU is not overloaded, FastHttpUser's response times should be almost identical to those of HttpUser. It is not "faster" in that sense. And of course, it cannot speed up the system you are testing.

How to use FastHttpUser
===========================

Just subclass FastHttpUser instead of HttpUser::

    from locust import task, FastHttpUser
    
    class MyUser(FastHttpUser):
        @task
        def index(self):
            response = self.client.get("/")

.. note::

    FastHttpUser/geventhttpclient is very similar to for HttpUser/python-requests, but sometimes there are subtle differences. This is particularly true if you work with the client library's internals, e.g. when manually managing cookies.

API
===


FastHttpUser class
--------------------

.. autoclass:: locust.contrib.fasthttp.FastHttpUser
    :members: network_timeout, connection_timeout, max_redirects, max_retries, insecure


FastHttpSession class
---------------------

.. autoclass:: locust.contrib.fasthttp.FastHttpSession
    :members: request, get, post, delete, put, head, options, patch

.. autoclass:: locust.contrib.fasthttp.FastResponse
    :members: content, text, json, headers
