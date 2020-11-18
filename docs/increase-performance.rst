.. _increase-performance:

==============================================================
Increase Locust's performance with a faster HTTP client
==============================================================

Locust's default HTTP client uses `python-requests <http://www.python-requests.org/>`_. 
The reason for this is that requests is a very well-maintained python package, that 
provides a really nice API, that many python developers are familiar with. Therefore, 
in many cases, we recommend that you use the default :py:class:`HttpUser <locust.HttpUser>`
which uses requests. However, if you're planning to run really large scale tests, 
Locust comes with an alternative HTTP client, 
:py:class:`FastHttpUser <locust.contrib.fasthttp.FastHttpUser>` which
uses `geventhttpclient <https://github.com/gwik/geventhttpclient/>`_ instead of requests.
This client is significantly faster, and we've seen 5x-6x performance increases for making 
HTTP-requests. This does not necessarily mean that the number of users one can simulate 
per CPU core will automatically increase 5x-6x, since it also depends on what else 
the load testing script does. However, if your locust scripts are spending most of their 
CPU time in making HTTP-requests, you are likely to see significant performance gains.

It is impossible to say what your particular hardware can handle, but in a *best case* scenario
you should be able to do close to 5000 requests per second per core, instead of around 850 for 
the normal HttpUser (tested on a 2018 MacBook Pro i7 2.6GHz)

How to use FastHttpUser
===========================

Subclass FastHttpUser instead of HttpUser::

    from locust import task, between
    from locust.contrib.fasthttp import FastHttpUser
    
    class MyUser(FastHttpUser):
        wait_time = between(2, 5)
        
        @task
        def index(self):
            response = self.client.get("/")


.. note::

    Because FastHttpUser uses a different client implementation with a slightly different API,
    it may not always work as a drop-in replacement for HttpUser.


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
