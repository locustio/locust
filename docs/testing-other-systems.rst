.. _testing-other-systems:

===============================
Testing other systems/protocols
===============================

Locust only comes with built-in support for HTTP/HTTPS but it can be extended to test almost any system. This is normally done by wrapping the protocol library and triggering a :py:attr:`request <locust.event.Events.request>` event after each call has completed, to let Locust know what happened.

.. note::

    It is important that the protocol libraries you use can be `monkey-patched <https://www.gevent.org/intro.html#monkey-patching>`_ by gevent. 
    
    Almost any libraries that are pure Python (using the Python ``socket`` module or some other standard library function like ``subprocess``) should work fine out of the box - but if they do their I/O calls from compiled code C, gevent will be unable to patch it. This will block the whole Locust/Python process (in practice limiting you to running a single User per worker process).

    Some C libraries allow for other workarounds. For example, if you want to use psycopg2 to performance test PostgreSQL, you can use `psycogreen <https://github.com/psycopg/psycogreen/>`_. If you are willing to get your hands dirty, you may be able to patch a library yourself, but that is beyond the scope of this documentation.

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

See :ref:`FastHttpUser <rest>`

SocketIO
========

See :ref:`SocketIOUser <socketio>`

.. note::

    SocketIO support is experimental and may change without notice.

pytest
======

Locust allows you to use `pytest <https://docs.pytest.org/>`_ syntax to define Locust Users using pytest fixtures (currently :py:class:`HttpSession <locust.clients.HttpSession>` and :py:class:`FastHttpSession <locust.contrib.fasthttp.FastHttpSession>`). It has multiple benefits:

* Simpler syntax than regular Locustfiles
* Run or debug easily from any editor that supports pytest
* Reliably reuse functional test cases for load testing

.. literalinclude:: ../examples/test_pytest.py

Example usage:

.. code-block:: sh

    $ locust -f test_pytest.py
    $ pytest test_pytest.py
    # if you have issues with gevent patching (RecursionError: maximum recursion depth exceeded)
    $ python -m gevent.monkey -m pytest test_pytest.py

Limitations:

* Each test case becomes a Locust User under the hood. We don't (yet) support weighting users.
* Locust will only look for pytest-style tests if there are no regular User classes defined.
* Adding other pytest fixtures or pytest plugins may cause issues (do let us know though)
* For a more complex example, see  `<https://github.com/locustio/locust/blob/master/locust/test/test_pytest_locustfile.py>`_

.. note::

    pytest support is experimental and may change without a new major release version.

OpenAI
======

Performance/load testing AI services is a little different. While you could call the OpenAI API using HttpUser or FastHttpUser, it is often convenient to use `the SDK <https://github.com/openai/openai-python>`_.

.. literalinclude:: ../examples/openai_ex.py

.. note::

    OpenAIUser is experimental and may change without notice.

MQTT
====

Locust uses to `paho-mqtt https://github.com/eclipse-paho/paho.mqtt.python`_ to provide Mqtt connection capabilities.

.. literalinclude:: ../examples/mqtt/locustfile.py

Alternatively, if you need more control over the Mqtt client you can use a custom implementation.

.. literalinclude:: ../examples/mqtt/locustfile_custom_mqtt_client.py

.. note::

    MqttUser is experimental and may change without notice.


Other examples
==============

See `locust-plugins <https://github.com/SvenskaSpel/locust-plugins#users>`_ it has users for Kafka, Selenium/WebDriver, Playwright and more.
