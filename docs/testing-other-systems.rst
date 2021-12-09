.. _testing-other-systems:

========================
Testing non-HTTP systems
========================

Locust only comes with built-in support for HTTP/HTTPS but it can be extended to test almost any system. This is normally done by wrapping the protocol library and triggering a :py:attr:`request <locust.event.Events.request>` event after each call has completed, to let Locust know what happened.

.. note::

    It is important that the protocol libraries you use can be `monkey-patched <http://www.gevent.org/intro.html#monkey-patching>`_ by gevent. 
    
    Almost any libraries that are pure Python (using the Python ``socket`` module or some other standard library function like ``subprocess``) should work fine out of the box - but if they do their I/O calls in C gevent will be unable to patch it. This will block the whole Locust/Python process (in practice limiting you to running a single User per worker process)

    Some C libraries allow for other workarounds. For example, if you want to use psycopg2 to performance test PostgreSQL, you can use `psycogreen <https://github.com/psycopg/psycogreen/>`_. If you are willing to get your hands dirty, you may also be able to do patch a library yourself, but that is beyond the scope of this documentation.

Example: writing an XML-RPC User/client
=======================================

Lets assume we had an XML-RPC server that we wanted to load test

.. literalinclude:: ../examples/custom_xmlrpc_client/server.py

We can build a generic XML-RPC client, by wrapping :py:class:`xmlrpc.client.ServerProxy`

.. literalinclude:: ../examples/custom_xmlrpc_client/xmlrpc_locustfile.py

Example: writing a gRPC User/client
=======================================

If you have understood the XML-RPC example, you can easily build a `gRPC <https://github.com/grpc/grpc>`_ User.

The only significant difference is that you need to make gRPC gevent-compatible, by executing this code before opening the channel:

.. code-block:: python

    import grpc.experimental.gevent as grpc_gevent

    grpc_gevent.init_gevent()

Dummy server to test:

.. literalinclude:: ../examples/grpc/hello_server.py

gRPC client, base User and example usage:

.. literalinclude:: ../examples/grpc/locustfile.py


For more examples of user types, see `locust-plugins <https://github.com/SvenskaSpel/locust-plugins#users>`_ (it has users for WebSocket/SocketIO, Kafka, Selenium/WebDriver and more)