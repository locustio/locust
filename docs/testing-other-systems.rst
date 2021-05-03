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
