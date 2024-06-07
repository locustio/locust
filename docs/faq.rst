.. _faq:

===
FAQ
===

How do I…

..

   Note: Hatch rate/ramp up does not change peak load, it only changes
   how fast you get there (people keep asking about this for some
   reason).

Resolve errors that occur during load (error 5xx, Connection aborted, Connection reset by peer, etc)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Check your server logs. If it works at low load then it is almost
   certainly not a Locust issue, but an issue with the system you are
   testing.

Clear cookies, to make the next task iteration seem like a new user to my system under test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Call ``self.client.cookies.clear()`` at the end of your task.

Control headers or other things about my HTTP requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Locust’s client in ``HttpUser`` inherits from
   `requests <https://requests.readthedocs.io/en/master/>`__ and the
   vast majority of parameters and methods for requests should just work
   with Locust. Check out the docs and Stack Overflow answers for
   requests first and then ask on Stack Overflow for additional Locust
   specific help if necessary.

Create a Locust file based on a recorded browser session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Try using `Transformer <https://transformer.readthedocs.io/>`__

How to run a Docker container of Locust in Windows Subsystem for Linux (Windows 10 users)?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   If you use WSL on a Windows computer, then you need one extra step
   than the `“docker run …”
   command <https://docs.locust.io/en/stable/running-locust-docker.html>`__:
   copy your locusttest1.py to a folder in a Windows path on your WSL
   and mount that folder instead of your normal WSL folder:

::

   $ mkdir /c/Users/[YOUR_Windows_USER]/Documents/Locust/
   $ cp ~/path/to/locusttest1.py /c/Users/[YOUR_Windows_USER]/Documents/Locust/
   $ docker run -p 8089:8089 -v /c/Users/[YOUR_Windows_USER]/Documents/Locust/:/mnt/locust locustio/locust:1.3.1 -f /mnt/locust/locusttest1.py

How to run locust on custom endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Prefix the the endpoint to all ``@app.route`` definitions in
   ``locust/web.py`` file & also change as follows (where ``/locust`` is
   new endpoint)

``app = Flask(__name__, static_url_path='/locust')``

   Change the entries of static content location in file
   ``locust/templates/index.html``.

Eg:
``<link rel="shortcut icon" href="{{ url_for('static', filename='img/favicon.ico') }}" type="image/x-icon"/>``

Locust web UI doesn’t show my tasks running, says 0 RPS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Locust only knows what you’re doing when you tell it. There are `Event
Hooks <https://docs.locust.io/en/stable/api.html#events>`__ that you use
to tell Locust what’s going on in your code. If you use Locust’s
``HttpUser`` and then use ``self.client`` to make http calls, the proper
events are normally fired for you automatically, making less work for
you unless you want to override the default events.

If you use the plain ``User`` or use ``HttpUser`` and you’re not using
``self.client`` to make http calls, Locust will not fire events for you.
You will have to fire events yourself. See `the Locust
docs <https://docs.locust.io/en/stable/testing-other-systems.html>`__
for examples.

HTML Report is filled up with failed requests for long running tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

https://github.com/locustio/locust/issues/2328

Other questions and issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

`Check the list of issues (a lot of questions/misunderstandings are
filed as
issues) <https://github.com/locustio/locust/issues?q=is%3Aissue%20>`__

Add things that you ran into and solved here! Anyone with a GitHub
account can contribute!

If you have questions about Locust that are not answered here, please
check
`StackOverflow <https://stackoverflow.com/questions/tagged/locust>`__,
or post your question there. This wiki is not for asking questions but
for answering them :)