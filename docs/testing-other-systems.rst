.. _testing-other-systems:

========================
Testing non-HTTP systems
========================

Locust only comes with built-in support for HTTP/HTTPS but it can be extended to load test almost any system. You do this by writing a custom client that triggers :py:attr:`request <locust.event.Events.request>`

.. note::

    It is important that any protocol libraries you use can be `monkey-patched <http://www.gevent.org/intro.html#monkey-patching>`_ by gevent (if they use the Python ``socket`` module or some other standard library function like ``subprocess`` you will be fine). Otherwise your calls will block the whole Locust/Python process (in practice limiting you to running a single User per worker process)

    Some C libraries cannot be monkey patched by gevent, but allow for other workarounds. For example, if you want to use psycopg2 to performance test PostgreSQL, you can use `psycogreen <https://github.com/psycopg/psycogreen/>`_.

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