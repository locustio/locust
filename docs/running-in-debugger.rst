.. _running-in-debugger:

===========================
Running tests in a debugger
===========================

Running Locust in a debugger is extremely useful when developing your tests. Among other things, you can examine a particular response or check some User instance variable.

But debuggers sometimes have issues with complex gevent-applications like Locust, and there is a lot going on in the framework itself that you probably aren't interested in. To simplify this, Locust provides a method called :py:func:`run_single_user <locust.debug.run_single_user>`:

.. literalinclude:: ../examples/debugging.py
    :language: python

It implicitly registers an event handler for the :ref:`request <extending_locust>` event to print some stats about every request made:

.. code-block:: console

    type    name                                           resp_ms exception
    GET     /hello                                         38      ConnectionRefusedError(61, 'Connection refused')
    GET     /hello                                         4       ConnectionRefusedError(61, 'Connection refused')

You can configure exactly what is printed by specifying parameters to :py:func:`run_single_user <locust.debug.run_single_user>`.

Make sure you have enabled gevent in your debugger settings. In VS Code's ``launch.json`` it looks like this:

.. literalinclude:: ../.vscode/launch.json
    :language: json

If you want to the whole Locust runtime (with ramp up, command line parsing etc), you can do that too:

.. literalinclude:: ../.vscode/launch_locust.json
    :language: json

There is a similar setting in `PyCharm <https://www.jetbrains.com/help/pycharm/debugger-python.html>`_.

.. note::

    | VS Code/pydev may give you warnings about:
    | ``sys.settrace() should not be used when the debugger is being used``
    | It can safely be ignored (and if you know how to get rid of it, please let us know)

You can execute run_single_user multiple times, as shown in `debugging_advanced.py <https://github.com/locustio/locust/tree/master/examples/debugging_advanced.py>`_.


Print HTTP communication
========================

Sometimes it can be hard to understand why an HTTP request fails in Locust when it works from a regular browser/other application. Here's how to examine the communication in detail:

For ``HttpUser`` (`python-requests <https://python-requests.org>`_):

.. code-block:: python

    # put this at the top of your locustfile (or just before the request you want to trace)
    import logging
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

For ``FastHttpUser`` (`geventhttpclient <https://github.com/gwik/geventhttpclient/>`_):

.. code-block:: python

    import sys
    ...

    class MyUser(FastHttpUser):
        @task
        def t(self):
            self.client.get("http://example.com/", debug_stream=sys.stderr)

Example output (for FastHttpUser):

.. code-block:: console

    REQUEST: http://example.com/
    GET / HTTP/1.1
    user-agent: python/gevent-http-client-1.5.3
    accept-encoding: gzip, deflate
    host: example.com

    RESPONSE: HTTP/1.1 200
    Content-Encoding: gzip
    Accept-Ranges: bytes
    Age: 460461
    Cache-Control: max-age=604800
    Content-Type: text/html; charset=UTF-8
    Date: Fri, 12 Aug 2022 09:20:07 GMT
    Etag: "3147526947+ident"
    Expires: Fri, 19 Aug 2022 09:20:07 GMT
    Last-Modified: Thu, 17 Oct 2019 07:18:26 GMT
    Server: ECS (nyb/1D20)
    Vary: Accept-Encoding
    X-Cache: HIT
    Content-Length: 648

    <!doctype html>
    <html>
    <head>
    ...

These approaches can of course be used when doing a full load test, but you might get a lot of output :)