.. _increaserr:

===========================
Increasing the request rate
===========================

Increase the number of requests per second using a combination of the following steps:

#. Increase the number of users. To fully utilize your target system you may need a lot of simultaneous users, especially if each request takes a long time to complete.

#. If response times are unexpectedly high and/or increasing as the number of users go up, then you have probably saturated the system you are testing and need to dig into why. This is not really a Locust problem, but here are some things you may want to check:

    -  resource utilization (e.g. CPU, memory & network. Check these metrics on the locust side as well)
    -  configuration (e.g. max threads for your web server)
    -  back end response times (e.g. DB)
    -  client side DNS performance/flood protection (Locust will normally make at least one DNS Request per User)

#. If Locust prints a warning about high CPU usage (``WARNING/root: CPU usage above 90%! ...``) try the following:

    -  Run Locust `distributed <https://docs.locust.io/en/stable/running-locust-distributed.html>`__ to utilize multiple cores & multiple machines
    -  Try switching to `FastHttpUser <https://docs.locust.io/en/stable/increase-performance.html#increase-performance>`__ to reduce CPU usage
    -  Check to see that there are no strange/infinite loops in your code

#. If you are using a custom client (not HttpUser or FastHttpUser), make sure any client library you are using is gevent-friendly otherwise it will block the entire Python process (essentially limiting you to one user per worker)

.. note::

    Hatch rate/ramp up does not change peak load, it only changes how fast you get there.