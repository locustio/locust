.. _increaserr:

===========================
Increasing the request rate
===========================

If you're not getting the desired/expected throughput there are a number of things you can do.

Concurrency
-----------

Increase the number of Users. To fully utilize your target system you may need a lot of concurrent requests. Note that spawn rate/ramp up does not change peak load, it only changes how fast you get there. High `wait times <writing-a-locustfile.html#wait-time>`_ and sleeps *do* impact throughput, so that may make it necessary to launch even more Users. You can find a whole blog post on this topic `here <https://www.locust.cloud/blog/closed-vs-open-workload-models>`__.

Load generation performance
---------------------------

If Locust prints a warning about high CPU usage (``WARNING/root: CPU usage above 90%! ...``) try the following:

    -  Run Locust `distributed <https://docs.locust.io/en/stable/running-distributed.html>`__ to utilize multiple cores & multiple machines
    -  Try switching to `FastHttpUser <https://docs.locust.io/en/stable/increase-performance.html#increase-performance>`__ to reduce CPU usage
    -  Check to see that there are no strange/infinite loops in your code

Also, if you are using a custom client (not HttpUser or FastHttpUser), make sure any client library you are using is `gevent-friendly <https://www.gevent.org/api/gevent.monkey.html>`__ otherwise it will block the entire Python process (essentially limiting you to one user per worker)

If you're doing really high throughput or using a lot of bandwidth, you may also want to check out your network utilization and other OS level metrics.

If you prefer to have someone else worry about load generator performance, you should check out :ref:`Locust Cloud <locust-cloud>`.

Actual issues with the system under test
----------------------------------------

If response times are high and/or increasing as the number of users go up, then you have probably saturated the system you are testing. This is not a Locust problem, but here are some things you may want to check:

    -  resource utilization (e.g. CPU, memory & network)
    -  configuration (e.g. max threads for your web server)
    -  back end response times (e.g. DB)

There are a few common pitfalls specific to load testing too:

    -  load balancing (make sure locust isn't hitting only a few of your instances)
    -  flood protection (sometimes a load test with the high amount of load from only a few machines will trigger this)
