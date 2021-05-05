.. _testing-other-systems:

===========================================
Testing other systems using custom clients
===========================================

Locust was built with HTTP as its main use case but it can be extended to load test almost any system. You do this by writing a custom client that triggers :py:attr:`request <locust.event.Events.request>`

.. note::

    Any protocol libraries that you use must be gevent-friendly (use the Python ``socket`` module or some other standard library function like ``subprocess``), or your calls are likely to block the whole Locust/Python process.
    
    Some C libraries cannot be monkey patched by gevent, but allow for other workarounds. For example, if you want to use psycopg2 to performance test PostgreSQL, you can use `psycogreen <https://github.com/psycopg/psycogreen/>`_. 

Example: writing an XML-RPC User/client
=======================================

Lets assume we had an XML-RPC server that we wanted to load test

.. literalinclude:: ../examples/custom_xmlrpc_client/server.py

We can build a generic XML-RPC client, by wrapping :py:class:`xmlrpc.client.ServerProxy`

.. literalinclude:: ../examples/custom_xmlrpc_client/xmlrpc_locustfile.py

For more examples, see `locust-plugins <https://github.com/SvenskaSpel/locust-plugins#users>`_

Example: writing a gRPC User/client
=======================================

Similarly to the XML-RPC example, we can also load test a gRPC server.

.. literalinclude:: ../examples/grpc/hello_server.py

In this case, the gRPC stub methods can also be wrapped so that we can record the request stats.

.. literalinclude:: ../examples/grpc/locustfile.py

Note: In order to make the `grpcio` Python library gevent-compatible the following code needs to be executed before creating the gRPC channel.

```python
import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()
```

Note: It is important to close the gRPC channel before stopping the User greenlet; otherwise Locust may not be able to stop executing. 
This is due to an issue in `grpcio` (see `grpc#15880 <https://github.com/grpc/grpc/issues/15880>`_).
