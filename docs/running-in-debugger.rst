.. _running-in-debugger:

===========================
Running tests in a debugger
===========================

Running Locust in a debugger is extremely useful when developing your tests. Among other things, you can examine a particular response or check some User instance variable.

But debuggers sometimes have issues with complex gevent-applications like Locust, and there is a lot going on in the framework itself that you probably arent interested in. To simplify this, Locust provides a method called :py:func:`run_single_user <locust.debug.run_single_user>`:

Note that this is fairly new feature, and the api is subject to change.

.. literalinclude:: ../examples/debugging.py
    :language: python

It implicitly registeres an event handler for the :ref:`request <extending_locust>` event to print some stats about every request made:

.. code-block:: console

    type    name                                           resp_ms exception
    GET     /hello                                         38      ConnectionRefusedError(61, 'Connection refused')
    GET     /hello                                         4       ConnectionRefusedError(61, 'Connection refused')

You can configure exactly what is printed by specifying parameters to :py:func:`run_single_user <locust.debug.run_single_user>`.

Make sure you have enabled gevent in your debugger settings. In VS Code's ``launch.json`` it looks like this:

.. literalinclude:: ../.vscode/launch.json
    :language: json

There is a similar setting in `PyCharm <https://www.jetbrains.com/help/pycharm/debugger-python.html>`_

.. note::

    | VS Code/pydev may give you warnings about:
    | ``sys.settrace() should not be used when the debugger is being used``
    | It can safely be ignored (and if you know how to get rid of it, please let us know)

You can execute run_single_user multiple times, as shown in `debugging_advanced.py <https://github.com/locustio/locust/tree/master/examples/debugging_advanced.py>`_
