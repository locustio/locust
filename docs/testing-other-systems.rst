.. _testing-other-systems:

===============================
Testing other systems/protocols
===============================

Locust only comes with built-in support for HTTP/HTTPS but it can be extended to test almost any system. This is normally done by wrapping the protocol library and triggering a :py:attr:`request <locust.event.Events.request>` event after each call has completed, to let Locust know what happened.

.. note::

    It is important that the protocol libraries you use can be `monkey-patched <http://www.gevent.org/intro.html#monkey-patching>`_ by gevent. 
    
    Almost any libraries that are pure Python (using the Python ``socket`` module or some other standard library function like ``subprocess``) should work fine out of the box - but if they do their I/O calls in C, gevent will be unable to patch it. This will block the whole Locust/Python process (in practice limiting you to running a single User per worker process).

    Some C libraries allow for other workarounds. For example, if you want to use psycopg2 to performance test PostgreSQL, you can use `psycogreen <https://github.com/psycopg/psycogreen/>`_. If you are willing to get your hands dirty, you may also be able to patch a library yourself, but that is beyond the scope of this documentation.

XML-RPC
=======

Lets assume we have an XML-RPC server that we want to load test.

.. literalinclude:: ../examples/custom_xmlrpc_client/server.py

We can build a generic XML-RPC client, by wrapping :py:class:`xmlrpc.client.ServerProxy`.

.. literalinclude:: ../examples/custom_xmlrpc_client/xmlrpc_locustfile.py

gRPC
====

Lets assume we have a `gRPC <https://github.com/grpc/grpc>`_ server that we want to load test:

.. literalinclude:: ../examples/grpc/hello_server.py

The generic GrpcUser base class sends events to Locust using an `interceptor <https://pypi.org/project/grpc-interceptor/>`_:

.. literalinclude:: ../examples/grpc/grpc_user.py

And a locustfile using the above would look like this:

.. literalinclude:: ../examples/grpc/locustfile.py

.. _testing-request-sdks:

requests-based libraries/SDKs
=============================

If you want to use a library that uses a `requests.Session <https://requests.readthedocs.io/en/latest/api/#requests.Session>`_ object under the hood you will most likely be able to skip all the above complexity.

Some libraries allow you to pass a Session explicitly, like for example the SOAP client provided by `Zeep <https://docs.python-zeep.org/en/master/transport.html#tls-verification>`_. In that case, just pass it your ``HttpUser``'s :py:attr:`client <locust.HttpUser.client>`, and any requests made using the library will be logged in Locust.

Even if your library doesn't expose that in its interface, you may be able to get it working by overwriting some internally used Session. Here's an example of how to do that for the `Archivist <https://github.com/jitsuin-inc/archivist-python>`_ client.

.. literalinclude:: ../examples/sdk_session_patching/session_patch_locustfile.py


REST
====

While you can subclass :ref:`HttpUser <quickstart>`/:ref:`FastHttpUser <increase-performance>` to test RESTful HTTP endpoints, you can avoid having to reinvent the wheel by using :py:class:`RestUser <locust.contrib.rest.RestUser>`. It extends FastHttpUser, adding the ``rest`` method, a wrapper around :py:class:`self.client.request <locust.contrib.fasthttp.FastHttpUser.client>` that:
    
* Parses the JSON response to a dict called ``js`` in the response object. Marks the request as failed if the response was not valid JSON.
* Defaults ``Content-Type`` and ``Accept`` headers to ``application/json``
* Sets ``catch_response=True`` (so use a :ref:`with-block <catch-response>`)
* Catches any unhandled exceptions thrown inside your with-block, marking the sample as failed (instead of exiting the task immediately without even firing the request event)

.. code-block:: python

    from locust import task, RestUser

    class MyUser(RestUser):
        @task
        def t(self):
            with self.rest("POST", "/", json={"foo": 1}) as resp:
                if resp.js is None:
                    pass # no need to do anything, already marked as failed
                elif "bar" not in resp.js:
                    resp.failure(f"'bar' missing from response {resp.text}")
                elif resp.js["bar"] != 42:
                    resp.failure(f"'bar' had an unexpected value: {resp.js['bar']}")

For a complete example, see `resp_ex.py <https://github.com/locustio/locust/blob/master/examples/rest_ex.py>`_. That also shows how you can subclass :py:class:`RestUser <locust.contrib.rest.RestUser>` to provide behaviours specific to your API, like like always sending common headers or always applying some validation to the response.

.. note::

    RestUser is new and details of its interface/implementation may change in new versions of Locust.


Other examples
==============

See `locust-plugins <https://github.com/SvenskaSpel/locust-plugins#users>`_ it has users for WebSocket/SocketIO, Kafka, Selenium/WebDriver, Playwright and more.

