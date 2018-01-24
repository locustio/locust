.. _increase-performance:

==============================================================
Increase Locust's performance with a faster HTTP client
==============================================================

Locust's default HTTP client uses `python-requests <http://www.python-requests.org/>`_. 
The reason for this is that requests is a very well-maintained python package, that 
provides a really nice API, that many python developers are familiar with. Therefore, 
in many cases, we recommend that you use the default :py:class:`HttpLocust <locust.core.HttpLocust>` 
which uses requests. However, if you're planning to run really large scale scale tests, 
Locust comes with an alternative HTTP client, 
:py:class:`FastHttpLocust <locust.contrib.fasthttp.FastHttpLocust>` which 
uses `geventhttpclient <https://github.com/gwik/geventhttpclient/>`_ instead of requests.
This client is significantly faster, and we've seen 5x-6x performance increases for making 
HTTP-requests. This does not necessarily mean that the number of users one can simulate 
per CPU core will automatically increase 5x-6x, since it also depends on what else 
the load testing script does. However, if your locust scripts are spending most of their 
CPU time in making HTTP-requests, you are likely to see signifant performance gains.


How to use FastHttpLocust
===========================

First, you need to install the geventhttplocust python package::

    pip install geventhttpclient

Then you just subclass FastHttpLocust instead of HttpLocust::

    from locust import TaskSet, task
    from locust.contrib.fasthttp import FastHttpLocust
    
    class MyTaskSet(TaskSet):
        @task
        def index(self):
            response = self.client.get("/")
    
    class MyLocust(FastHttpLocust):
        task_set = MyTaskSet
        min_wait = 1000
        max_wait = 60000


.. note::

    FastHttpLocust uses a whole other HTTP client implementation, with a different API, compared to 
    the default HttpLocust that uses python-requests. Therefore FastHttpLocust might not work as a d
    rop-in replacement for HttpLocust, depending on how the HttpClient is used.


API
===

FastHttpSession class
=====================

.. autoclass:: locust.contrib.fasthttp.FastHttpSession
    :members: __init__, request, get, post, delete, put, head, options, patch

.. autoclass:: locust.contrib.fasthttp.FastResponse
    :members: content, text, headers
