####################
Changelog Highlights
####################

For full details of the Locust changelog, please see https://github.com/locustio/locust/blob/master/CHANGELOG.md

2.1.0
=====

* Fix docker builds (2.0 never got pushed to Docker Hub)
* Bump dependency on pyzmq to fix out of memory issue on Windows
* Use 1 as default for user count and spawn rate in web UI start form
* Various documentation updates

2.0.0
=====

User ramp up/down and User type selection is now controlled by the master instead of autonomously by the workers 
----------------------------------------------------------------------------------------------------------------
This has allowed us to fix some issues with incorrect/skewed User type selection and undesired stepping of ramp up. The issues were especially visible when running many workers and/or using LoadShape:s. This change also allows redistribution of Users if a worker disconnects during a test. This is a major change internally in Locust so please let us know if you encounter any problems (particularly regarding ramp up pace, User distribution, CPU usage on master, etc)

Other potentially breaking API changes
--------------------------------------
* Change the default User weight to 1 instead of 10 (the old default made no sense)
* Fire test_start and test_stop events on workers too (previously they were only fired on master/standalone instances)
* Workers now send their version number to master. Master will warn about version differences, and pre 2.0-versions will not be allowed to connect at all (because they would not work anyway)
* Update Flask dependency to 2.0

Significant merged PR:s (and prerelease version they were introduced in)
------------------------------------------------------------------------
* Allow workers to bypass version check by sending -1 as version (2.0.0) https://github.com/locustio/locust/pull/1830
* Improve logging messages and clean up code after dispatch refactoring (2.0.0b4) https://github.com/locustio/locust/pull/1826
* Remove `user_classes_count` from heartbeat payload (2.0.0b4) https://github.com/locustio/locust/pull/1825
* Add option to set concurrency of FastHttpUser/Session (2.0.0b3) https://github.com/locustio/locust/pull/1812/
* Fire test_start and test_stop events on worker nodes (2.0.0b3) https://github.com/locustio/locust/pull/1777/
* Auto shrink request stats table to fit terminal (2.0.0b2) https://github.com/locustio/locust/pull/1811
* Refactoring of the dispatch logic to improve performance (2.0.0b2) https://github.com/locustio/locust/pull/1809 
* Check version of workers when they connect. Warn if there is a mismatch, refuse 1.x workers to connect (2.0.0b1) https://github.com/locustio/locust/pull/1805 
* Change the default User weight to 1 instead of 10 (2.0.0b1) https://github.com/locustio/locust/pull/1803
* Upgrade to Flask 2 (2.0.0b1) https://github.com/locustio/locust/pull/1764
* Move User selection responsibility from worker to master in order to fix unbalanced distribution of users and uneven ramp-up (2.0.0b0) https://github.com/locustio/locust/pull/1621

Some of these are not really that significant and may be removed from this list at a later time, once 2.0 has stabilised.

1.6.0
=====

* Allow cross process communication using custom messages https://github.com/locustio/locust/pull/1782
* Fix: status "stopped" instead of "spawning", tick\(\) method of LoadShape called only once https://github.com/locustio/locust/pull/1769

1.5.3
=====

* Fix an issue with custom Users calling request_success/_failure.fire() not being added to statistics https://github.com/locustio/locust/pull/1761

1.5.2
=====

* Pin version of flask to 1.1.2, fixing https://github.com/locustio/locust/issues/1759
* Fix issue with GRPC compatibility and add GRPC example to documentation https://github.com/locustio/locust/pull/1755
* Use time.perf_counter() to calculate elapsed times everywhere, should only matter for Windows https://github.com/locustio/locust/pull/1758

1.5.1
=====

* Fixed an issue with 1.5.0 where an extra parameter (start_time) was passed to request event https://github.com/locustio/locust/pull/1754

1.5.0
=====

* Unify request_success/request_failure into a single event called request (the old ones are deprecated but still work) https://github.com/locustio/locust/issues/1724
* Add the response object and context as parameters to the request event. context is used to forward information to the request event handler (can be used for things like username, tags etc)

1.4.4
=====

* Ensure runner.quit finishes even when users are broken https://github.com/locustio/locust/pull/1728
* Make runner / user count available to LoadTestShape https://github.com/locustio/locust/pull/1719
* Other small fixes

1.4.3
=====

* Fix bug that broke the tooltips for charts in the Web UI 

1.4.2
=====

* Multiple improvements for charting including tooltips etc
* Added --html option to save HTML report https://github.com/locustio/locust/pull/1637
* Lots of other small fixes

1.4.1
=====

* Fix 100% cpu usage when running in docker/non-tty terminal https://github.com/locustio/locust/issues/1629

1.4.0
=====

* You can now control user count from terminal while the test is running https://github.com/locustio/locust/pull/1612
* Infinite run time is now the default for command line runs https://github.com/locustio/locust/pull/1625
* wait_time now defaults to zero https://github.com/locustio/locust/pull/1626

1.3.2
=====

* List Python 3.9 as supported in the package/on PyPi
* Fix XSS vulnerability in the web UI (sounds important but really isn't, as Locust UI is not meant to be exposed to outside users)

1.3.1
=====

* Bump minimum required gevent version to 20.9.0 (latest), as the previous ones had sneaky binary incompatibilities with the latest version of greenlet ("RuntimeWarning: greenlet.greenlet size changed, may indicate binary incompatibility. Expected 144 from C header, got 152 from PyObject")

1.3.0
=====

* Breaking change: Remove step-load feature (now that we have LoadTestShape it is no longer needed)
* More type hints to enable better code completion and linting of locustfiles

Bug fixes: 

* LoadTestShape.get\_run\_time is not relative to start of test https://github.com/locustio/locust/issues/1557
* Refactor and fix delayed user stopping in combination with on\_stop https://github.com/locustio/locust/pull/1560
* runner.quit gets blocked by slow on stop https://github.com/locustio/locust/issues/1552
* Remove legacy code that was only needed for py2
* Lots more

1.2.3
=====

* Bug fix (TypeError: code() takes at least 14 arguments (13 given) (Werkzeug version issue) https://github.com/locustio/locust/issues/1545)
* Bug fix (Locust stuck in "Shape worker starting" when restarting a test from the webUI https://github.com/locustio/locust/issues/1540)
* Various linting fixes that *should* have no functional impact

1.2.2
=====

* Bug fix (LoadTestShape in headless mode https://github.com/locustio/locust/pull/1539)

1.2.1
=====

* Bug fix (StatsEntry.use_response_times_cache must be set to True, https://github.com/locustio/locust/issues/1531)

1.2
===

* Rename hatch rate to spawn rate (the --hatch-rate parameter is only deprecated, but the hatch_complete event has been renamed spawning_complete)
* Ability to generate any custom load shape with LoadTestShape class
* Allow ramping down of users
* Ability to use save custom percentiles
* Improve command line stats output
* Bug fixes (excessive precision of metrics in losust csv stats, negative response time when system clock has changed, issue with non-string failure messages, some typos etc)
* Documentation improvements

1.1.1
=====

* --run-time flag is not respected if there is an exception in a test_stop listener
* FastHttpUser: Handle stream ended at an unexpected time and UnicodeDecodeError. Show bad/error status codes on failures page.
* Improve logging when locust master port is busy

1.1
===

* The official Docker image is now based on the ``python:3.8`` image instead of ``python:3.8-alpine``. This should 
  make it easier to install other python packages when extending the locust docker image.
* Allow Users to stop the runner by calling self.environment.runner.quit() (without deadlocking sometimes)
* Cut to only 5% free space on the top of the graphs
* Use csv module to generate csv data (solves issues with sample names that need escaping in csv)
* Various documentation improvements

1.0.3
=====

* Ability to control the exit code of the Locust process by setting :py:attr:`Environment.process_exit_code <locust.env.Environment.process_exit_code>`
* FastHttpLocust: Change dependency to use original geventhttpclient (now that releases can be made there) instead of geventhttpclient-wheels
* Fix search on readthedocs

1.0.2
=====

* Check for low open files limit (ulimit) and try to automatically increase it from within the locust process.
* Other various bug fixes as improvements


.. _changelog-1-0:

1.0, 1.0.1
==========

This version contains some breaking changes.

Locust class renamed to User
----------------------------

We've renamed the ``Locust`` and ``HttpLocust`` classes to ``User`` and ``HttpUser``. The ``locust`` attribute on 
:py:class:`TaskSet <locust.TaskSet>` instances has been renamed to :py:attr:`user <locust.TaskSet.user>`.

The parameter for setting number of users has also been changed, from ``-c`` / ``--clients`` to ``-u`` / ``--users``.

Ability to declare @task directly under the ``User`` class
----------------------------------------------------------

It's now possible to declare tasks directly under a User class like this:

.. code-block:: python

    class WebUser(User):
        @task
        def some_task(self):
            pass

In tasks declared under a User class (e.g. ``some_task`` in the example above), ``self`` refers to the User 
instance, as one would expect. For tasks defined under a :py:class:`TaskSet <locust.TaskSet>` class, ``self`` 
would refer to the ``TaskSet`` instance.

The ``task_set`` attribute on the ``User`` class (previously ``Locust`` class) has been removed. To declare a 
``User`` class with a single ``TaskSet`` one would now use the the :py:attr:`tasks <locust.User.tasks>` 
attribute instead:

.. code-block:: python

    class MyTaskSet(TaskSet):
        ...
    
    class WebUser(User):
        tasks = [MyTaskSet]


Task tagging
------------

A new :ref:`tag feature <tagging-tasks>` has been added that makes it possible to include/exclude tasks during 
a test run.

Tasks can be tagged using the :py:func:`@tag <locust.tag>` decorator:

.. code-block:: python

    class WebUser(User):
        @task
        @tag("tag1", "tag2")
        def my_task(self):
            ...

And tasks can then be specified/excluded using the ``--tags``/``-T`` and ``--exclude-tags``/``-E`` command line arguments. 


Environment variables changed
-----------------------------

The following changes has been made to the configuration environment variables

* ``LOCUST_MASTER`` has been renamed to ``LOCUST_MODE_MASTER`` (in order to make it less likely to get variable name collisions 
  when running Locust in Kubernetes/K8s which automatically adds environment variables depending on service/pod names).
* ``LOCUST_SLAVE`` has been renamed to ``LOCUST_MODE_WORKER``.
* ``LOCUST_MASTER_PORT`` has been renamed to ``LOCUST_MASTER_NODE_PORT``.
* ``LOCUST_MASTER_HOST`` has been renamed to ``LOCUST_MASTER_NODE_HOST``.
* ``CSVFILEBASE`` has been renamed to ``LOCUST_CSV``.

See the :ref:`configuration` documentation for a full list of available :ref:`environment variables <environment-variables>`.


Other breaking changes
----------------------

* The master/slave terminology has been changed to master/worker. Therefore the command line arguments ``--slave`` and
  ``--expect-slaves`` has been renamed to ``--worker`` and ``--expect-workers``.
* The option for running Locust without the Web UI has been renamed from ``--no-web`` to ``--headless``.
* Removed ``Locust.setup``, ``Locust.teardown``, ``TaskSet.setup`` and ``TaskSet.teardown`` hooks. If you want to 
  run code at the start or end of a test, you should instead use the :py:attr:`test_start <locust.event.Events.test_start>`
  and :py:attr:`test_stop <locust.event.Events.test_stop>` events:
  
  .. code-block:: python
  
      from locust import events
      
      @events.test_start.add_listener
      def on_test_start(**kw):
          print("test is starting")
        
      @events.test_stop.add_listener
      def on_test_start(**kw):
          print("test is stopping")
* ``TaskSequence`` and ``@seq_task`` has been replaced with :ref:`SequentialTaskSet <sequential-taskset>`.
* A ``User count`` column has been added to the history stats CSV file. The column order and column names has been changed.
* The official docker image no longer uses a shell script with a bunch of special environment variables to configure how 
  how locust is started. Instead, the ``locust`` command is now set as ``ENTRYPOINT`` of the docker image. See
  :ref:`running-locust-docker` for more info.
* Command line option ``--csv-base-name`` has been removed, since it was just an alias for ``--csv``.
* The way Locust handles logging has been changed. We no longer wrap stdout (and stderr) to automatically make print 
  statements go into the log. ``print()`` statements now only goes to stdout. To add custom entries to the log, one 
  should now use the Python logging module:
  
  .. code-block:: python
  
      import logging
      logging.info("custom logging message)
  
  For more info see :ref:`logging`


Web UI improvements
-------------------

* It's now possible to protect the Web UI with Basic Auth using hte ``--web-auth`` command line argument.
* The Web UI can now be served over HTTPS by specifying a TLS certificate and key with the ``--tls-cert`` 
  and ``--tls-key`` command line arguments.
* If the number of users and hatch rate are specified on command line, it's now used to pre-populate the input fields in 
  the Web UI.



Other fixes and improvements
----------------------------

* Added ``--config`` command line option for specifying a :ref:`configuration file <configuration-file>` path
* The code base has been refactored to make it possible to run :ref:`Locust as a python lib <use-as-lib>`. 
* It's now possible to call ``response.failure()`` or ``response.success()`` multiple times when using 
  the ``catch_response=True`` in the HTTP clients. Only the last call to ``success``/``failure`` will count.
* The ``--help`` output has been improved by grouping related options together.



0.14.6
======

* Fix bug when running with latest Gevent version, and pinned the latest version


0.14.0
======

* Drop Python 2 and Python 3.5 support!
* Continuously measure CPU usage and emit a warning if we get a five second average above 90%
* Show CPU usage of slave nodes in the Web UI
* Fixed issue when running Locust distributed and new slave nodes connected during the hatching/ramp-up 
  phase (https://github.com/locustio/locust/issues/1168)


0.13.5
======

Various minor fixes, mainly regarding FastHttpLocust.

0.13.4
======

Identical to previous version, but now built & deployed to Pypi using Travis.

0.13.3
======

* Unable to properly connect multiple slaves - https://github.com/locustio/locust/issues/1176
* Zero exit code on exception - https://github.com/locustio/locust/issues/1172
* `--stop-timeout` is not respected when changing number of running Users in distributed mode - https://github.com/locustio/locust/issues/1162

0.13.2
======

* Fixed bug that broke the Web UI's repsonse time graph

0.13.1
======

* Fixed crash bug on Python 3.8.0
* Various other bug fixes and improvements.


0.13.0
======

* New API for specifying wait time - https://github.com/locustio/locust/pull/1118

  Example of the new API::

      from locust import HttpLocust, between
      class User(HttpLocust):
          # wait between 5 and 30 seconds
          wait_time = between(5, 30)

  There are three built in :ref:`wait time functions <wait_time_functions>`: :py:func:`between <locust.wait_time.between>`,
  :py:func:`constant <locust.wait_time.constant>` and :py:func:`constant_pacing <locust.wait_time.constant_pacing>`.

* FastHttpLocust: Accept self signed SSL certificates, ignore host checks. Improved response code handling
* Add current working dir to sys.path - https://github.com/locustio/locust/pull/484
* Web UI improvements: Added 90th percentile to table, failure per seconds as a series in the chart
* Ability to specify host in web ui
* Added response_length to request_failure event - https://github.com/locustio/locust/pull/1144
* Added p99.9 and p99.99 to request stats distribution csv - https://github.com/locustio/locust/pull/1125
* Various other bug fixes and improvements.

0.12.2
======

* Added `--skip-log-setup` to disable Locust's default logging setup.
* Added `--stop-timeout` to allow tasks to finish running their iteration before stopping
* Added 99.9 and 99.99 percentile response times to csv output
* Allow custom clients to set request response time to None. Those requests will be excluded
  when calculating median, average, min, max and percentile response times.
* Renamed the last row in statistics table from "Total" to "Aggregated" (since the values aren't
  a sum of the individual table rows).
* Some visual improvements to the web UI.
* Fixed issue with simulating fewer number of locust users than the number of slave/worker nodes.
* Fixed bugs in the web UI related to the fact that the stats table is truncated at 500 entries.
* Various other bug fixes and improvements.


0.12.1
======

* Added new :code:`FastHttpLocust` class that uses a faster HTTP client, which should be 5-6 times faster
  than the normal :code:`HttpLocust` class. For more info see the documentation on :ref:`increasing performance <increase-performance>`.
* Added ability to set the exit code of the locust process when exceptions has occurred within the user code,
  using the :code:`--exit-code-on-error` parameter.
* Added TCP keep alive to master/slave communication sockets to avoid broken connections in some environments.
* Dropped support for Python 3.4
* Numerous other bug fixes and improvements.


0.10.0
======

* Python 3.7 support
* Added a status page to the web UI when running Locust distributed showing the status of slave nodes
  and detect down slaves using heartbeats
* Numerous bugfixes/documentation updates (see detailed changelog)


0.9.0
=====

* Added detailed changelog (https://github.com/locustio/locust/blob/master/CHANGELOG.md)
* Numerous bugfixes (see detailed changelog)
* Added sequential task support - https://github.com/locustio/locust/pull/827
* Added support for user-defined wait_function - https://github.com/locustio/locust/pull/785
* By default, Locust no longer resets the statistics when the hatching is complete.
  Therefore :code:`--no-reset-stats` has been deprected (since it's now the default behaviour),
  and instead a new :code:`--reset-stats` option has been added.
* Dropped support for Python 3.3
* Updated documentation

0.8.1
=====

* Updated pyzmq version, and changed so that we don't pin a specific version.
  This makes it easier to install Locust on Windows.


0.8
===

* Python 3 support
* Dropped support for Python 2.6
* Added :code:`--no-reset-stats` option for controling if the statistics should be reset once
  the hatching is complete
* Added charts to the web UI for requests per second, average response time, and number of
  simulated users.
* Updated the design of the web UI.
* Added ability to write a CSV file for results via command line flag
* Added the URL of the host that is currently being tested to the web UI.
* We now also apply gevent's monkey patching of threads. This fixes an issue when
  using Locust to test Cassandra (https://github.com/locustio/locust/issues/569).
* Various bug fixes and improvements


0.7.5
=====

* Use version 1.1.1 of gevent. Fixes an install issue on certain versions of python.


0.7.4
=====

* Use a newer version of requests, which fixed an issue for users with older versions of
  requests getting ConnectionErrors (https://github.com/locustio/locust/issues/273).
* Various fixes to documentation.


0.7.3
=====

* Fixed bug where POST requests (and other methods as well) got incorrectly reported as
  GET requests, if the request resulted in a redirect.
* Added ability to download exceptions in CSV format. Download links has also been moved
  to it's own tab in the web UI.


0.7.2
=====

* Locust now returns an exit code of 1 when any failed requests were reported.
* When making an HTTP request to an endpoint that responds with a redirect, the original
  URL that was requested is now used as the name for that entry in the statistics (unless
  an explicit override is specified through the *name* argument). Previously, the last
  URL in the redirect chain was used to label the request(s) in the statistics.
* Fixed bug which caused only the time of the last request in a redirect chain to be
  included in the reported time.
* Fixed bug which caused the download time of the request body not to be included in the
  reported response time.
* Fixed bug that occurred on some linux dists that were tampering with the python-requests
  system package (removing dependencies which requests is bundling). This bug only occured
  when installing Locust in the python system packages, and not when using virtualenv.
* Various minor fixes and improvements.


0.7.1
=====

* Exceptions that occurs within TaskSets are now catched by default.
* Fixed bug which caused Min response time to always be 0 after all locusts had been hatched
  and the statistics had been reset.
* Minor UI improvements in the web interface.
* Handle messages from "zombie" slaves by ignoring the message and making a log entry
  in the master process.



0.7
===

HTTP client functionality moved to HttpLocust
---------------------------------------------

Previously, the Locust class instantiated a :py:class:`HttpSession <locust.clients.HttpSession>`
under the client attribute that was used to make HTTP requests. This funcionality has
now been moved into the :py:class:`HttpLocust <locust.core.HttpLocust>` class, in an
effort to make it more obvious how one can use Locust to
:doc:`load test non-HTTP systems <testing-other-systems>`.

To make existing locust scripts compatible with the new version you should make your
locust classes inherit from HttpLocust instead of the base Locust class.


msgpack for serializing master/slave data
-----------------------------------------

Locust now uses `msgpack <http://msgpack.org/>`_ for serializing data that is sent between
a master node and it's slaves. This adresses a possible attack that can be used to execute
code remote, if one has access to the internal locust ports that are used for master-slave
communication. The reason for this exploit was due to the fact that pickle was used.

.. warning::

    Anyone who uses an older version should make sure that their Locust machines are not publicly
    accessible on port 5557 and 5558. Also, one should never run Locust as root.

Anyone who uses the :py:class:`report_to_master <locust.events.report_to_master>` and
:py:class:`slave_report <locust.events.slave_report>` events, needs to make sure that
any data that is attached to the slave reports is serializable by msgpack.

requests updated to version 2.2
-------------------------------

Locust updated `requests <http://python-requests.org/>`_ to the latest major release.

.. note::

   Requests 1.0 introduced some major API changes (and 2.0 just a few). Please check if you
   are using any internal features and check the documentation:
   `Migrating to 1.x <http://docs.python-requests.org/en/latest/api/#migrating-to-1-x>`_ and
   `Migrationg to 2.x <http://docs.python-requests.org/en/latest/api/#migrating-to-2-x>`_

gevent updated to version 1.0
-------------------------------

gevent 1.0 has now been released and Locust has been updated accordingly.

Big refactoring of request statistics code
------------------------------------------

Refactored :py:class:`RequestStats`.

* Created :py:class:`StatsEntry` which represents a single stats entry (URL).

Previously the :py:class:`RequestStats` was actually doing two different things:

* It was holding track of the aggregated stats from all requests
* It was holding the stats for single stats entries.

Now RequestStats should be instantiated and holds the global stats, as well as a dict of StatsEntry instances which holds the stats for single stats entries (URLs)

Removed support for avg_wait
----------------------------

Previously one could specify avg_wait to :py:class:`TaskSet` and :py:class:`Locust` that Locust would try to strive to. However this can be sufficiently accomplished by using min_wait and max_wait for most use-cases. Therefore we've decided to remove the avg_wait as its use-case is not clear or just too narrow to be in the Locust core.

Removed support for ramping
----------------------------

Previously one could tell Locust, using the --ramp option, to try to find a stable client count that the target host could handle, but it's been broken and undocumented for quite a while so we've decided to remove it from the locust core and perhaps have it reappear as a plugin in the future.


Locust Event hooks now takes keyword argument
---------------------------------------------

When :doc:`extending-locust` by listening to :ref:`events`, the listener functions should now expect
the arguments to be passed in as keyword arguments. It's also highly recommended to add an extra
wildcard keyword arguments to listener functions, since they're then less likely to break if extra
arguments are added to that event in some future version. For example::

    from locust import events

    def on_request(request_type, name, response_time, response_length, **kw):
        print "Got request!"

    locust.events.request_success += on_request

The *method* and *path* arguments to :py:obj:`request_success <locust.events.request_success>` and
:py:obj:`request_failure <locust.events.request_failure>` are now called *request_type* and *name*,
since it's less HTTP specific.


Other changes
-------------

* You can now specify the port on which to run the web host
* Various code cleanups
* Updated gevent/zmq libraries
* Switched to unittest2 discovery
* Added option --only-summary to only output the summary to the console, thus disabling the periodic stats output.
* Locust will now make sure to spawn all the specified locusts in distributed mode, not just a multiple of the number of slaves.
* Fixed the broken Vagrant example.
* Fixed the broken events example (events.py).
* Fixed issue where the request column was not sortable in the web-ui.
* Minor styling of the statistics table in the web-ui.
* Added options to specify host and ports in distributed mode using --master-host, --master-port for the slaves, --master-bind-host, --master-bind-port for the master.
* Removed previously deprecated and obsolete classes WebLocust and SubLocust.
* Fixed so that also failed requests count, when specifying a maximum number of requests on the command line


0.6.2
=====

* Made Locust compatible with gevent 1.0rc2. This allows user to step around a problem
  with running Locust under some versions of CentOS, that can be fixed by upgrading
  gevent to 1.0.
* Added :py:attr:`parent <locust.core.TaskSet.parent>` attribute to TaskSet class that
  refers to the parent TaskSet, or Locust, instance. Contributed by Aaron Daubman.


0.6.1
=====

* Fixed bug that was causing problems when setting a maximum number of requests using the
  **-n** or **--num-request** command line parameter.


0.6
===

.. warning::

    This version comes with non backward compatible changes to the API.
    Anyone who is currently using existing locust scripts and want to upgrade to 0.6
    should read through these changes.

:py:class:`SubLocust <locust.core.SubLocust>` replaced by :py:class:`TaskSet <locust.core.TaskSet>` and :py:class:`Locust <locust.core.Locust>` class behaviour changed
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

:py:class:`Locust <locust.core.Locust>` classes does no longer control task scheduling and execution.
Therefore, you no longer define tasks within Locust classes, instead the Locust class has a
:py:attr:`task_set <locust.core.Locust.task_set>` attribute which should point to a
:py:class:`TaskSet <locust.core.TaskSet>` class. Tasks should now be defined in TaskSet
classes, in the same way that was previously done in Locust and SubLocust classes. TaskSets can be
nested just like SubLocust classes could.

So the following code for 0.5.1::

    class User(Locust):
        min_wait = 10000
        max_wait = 120000

        @task(10)
        def index(self):
            self.client.get("/")

        @task(2)
        class AboutPage(SubLocust):
            min_wait = 10000
            max_wait = 120000

            def on_init(self):
                self.client.get("/about/")

            @task
            def team_page(self):
                self.client.get("/about/team/")

            @task
            def press_page(self):
                self.client.get("/about/press/")

            @task
            def stop(self):
                self.interrupt()

Should now be written like::

    class BrowsePage(TaskSet):
        @task(10)
        def index(self):
            self.client.get("/")

        @task(2)
        class AboutPage(TaskSet):
            def on_init(self):
                self.client.get("/about/")

            @task
            def team_page(self):
                self.client.get("/about/team/")

            @task
            def press_page(self):
                self.client.get("/about/press/")

            @task
            def stop(self):
                self.interrupt()

    class User(Locust):
        min_wait = 10000
        max_wait = 120000
        task_set = BrowsePage

Each TaskSet instance gets a :py:attr:`locust <locust.core.TaskSet.locust>` attribute, which refers to the
Locust class.

Locust now uses Requests
------------------------

Locust's own HttpBrowser class (which was typically accessed through *self.client* from within a locust class)
has been replaced by a thin wrapper around the requests library (http://python-requests.org). This comes with
a number of advantages. Users can  now take advantage of a well documented, well written, fully fledged
library for making HTTP requests. However, it also comes with some small API changes wich will require users
to update their existing load testing scripts.

Gzip encoding turned on by default
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The HTTP client now sends headers for accepting gzip encoding by default. The **--gzip** command line argument
has been removed and if someone want to disable the *Accept-Encoding* that the HTTP client uses, or any
other HTTP headers you can do::

    class MyWebUser(Locust):
        def on_start(self):
            self.client.headers = {"Accept-Encoding":""}


Improved HTTP client
^^^^^^^^^^^^^^^^^^^^

Because of the switch to using python-requests in the HTTP client, the API for the client has also
gotten a few changes.

* Additionally to the :py:meth:`get <locust.clients.HttpSession.get>`, :py:meth:`post <locust.clients.HttpSession.post>`,
  :py:meth:`put <locust.clients.HttpSession.put>`, :py:meth:`delete <locust.clients.HttpSession.delete>` and
  :py:meth:`head <locust.clients.HttpSession.head>` methods, the :py:class:`HttpSession <locust.clients.HttpSession>` class
  now also has :py:meth:`patch <locust.clients.HttpSession.patch>` and :py:meth:`options <locust.clients.HttpSession.options>` methods.

* All arguments to the HTTP request methods, except for **url** and **data** should now be specified as keyword arguments.
  For example, previously one could specify headers using::

      client.get("/path", {"User-Agent":"locust"}) # this will no longer work

  And should now be specified like::

      client.get("/path", headers={"User-Agent":"locust"})

* In general the whole HTTP client is now more powerful since it leverages on python-requests. Features that we're
  now able to use in Locust includes file upload, SSL, connection keep-alive, and more.
  See the `python-requests documentation <http://python-requests.org>`_ for more details.

* The new :py:class:`HttpSession <locust.clients.HttpSession>` class' methods now return python-request
  :py:class:`Response <requests.Response>` objects. This means that accessing the content of the response
  is no longer made using the **data** attribute, but instead the **content** attribute. The HTTP response
  code is now accessed through the **status_code** attribute, instead of the **code** attribute.


HttpSession methods' catch_response argument improved and allow_http_error argument removed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* When doing HTTP requests using the **catch_response** argument, the context manager that is returned now
  provides two functions, :py:meth:`success <locust.clients.ResponseContextManager.success>` and
  :py:meth:`failure <locust.clients.ResponseContextManager.failure>` that can be used to manually control
  what the request should be reported as in Locust's statistics.

  .. autoclass:: locust.clients.ResponseContextManager
    :members: success, failure
    :noindex:

* The **allow_http_error** argument of the HTTP client's methods has been removed. Instead one can use the
  **catch_response** argument to get a context manager, which can be used together with a with statement.

  The following code in the previous Locust version::

      client.get("/does/not/exist", allow_http_error=True)

  Can instead now be written like::

      with client.get("/does/not/exist", catch_response=True) as response:
          response.success()


Other improvements and bug fixes
--------------------------------

* Scheduled task callables can now take keyword arguments and not only normal function arguments.
* SubLocust classes that are scheduled using :func:`locust.core.Locust.schedule_task` can now take
  arguments and keyword arguments (available in *self.args* and *self.kwargs*).
* Fixed bug where the average content size would be zero when doing requests against a server that
  didn't set the content-length header (i.e. server that uses *Transfer-Encoding: chunked*)



Smaller API Changes
-------------------

* The *require_once* decorator has been removed. It was an old legacy function that no longer fit into
  the current way of writing Locust tests, where tasks are either methods under a Locust class or SubLocust
  classes containing task methods.
* Changed signature of :func:`locust.core.Locust.schedule_task`. Previously all extra arguments that
  was given to the method was passed on to the task when it was called. It no longer accepts extra arguments.
  Instead, it takes an *args* argument (list) and a *kwargs* argument (dict) which are be passed to the task when
  it's called.
* Arguments for :py:class:`request_success <locust.events.request_success>` event hook has been changed.
  Previously it took an HTTP Response instance as argument, but this has been changed to take the
  content-length of the response instead. This makes it easier to write custom clients for Locust.


0.5.1
=====

* Fixed bug which caused --logfile and --loglevel command line parameters to not be respected when running
  locust without zeromq.

0.5
===

API changes
-----------

* Web inteface is now turned on by default. The **--web** command line option has been replaced by --no-web.
* :func:`locust.events.request_success`  and :func:`locust.events.request_failure` now gets the HTTP method as the first argument.

Improvements and bug fixes
--------------------------

* Removed **--show-task-ratio-confluence** and added a **--show-task-ratio-json** option instead. The
  **--show-task-ratio-json** will output JSON data containing the task execution ratio for the locust
  "brain".
* The HTTP method used when a client requests a URL is now displayed in the web UI
* Some fixes and improvements in the stats exporting:

 * A file name is now set (using content-disposition header) when downloading stats.
 * The order of the column headers for request stats was wrong.
 * Thanks Benjamin W. Smith, Jussi Kuosa and Samuele Pedroni!

0.4
===

API changes
-----------

* WebLocust class has been deprecated and is now called just Locust. The class that was previously
  called Locust is now called LocustBase.
* The *catch_http_error* argument to HttpClient.get() and HttpClient.post() has been renamed to
  *allow_http_error*.

Improvements and bug fixes
--------------------------

* Locust now uses python's logging module for all logging
* Added the ability to change the number of spawned users when a test is running, without having
  to restart the test.
* Experimental support for automatically ramping up and down the number of locust to find a maximum
  number of concurrent users (based on some parameters like response times and acceptable failure
  rate).
* Added support for failing requests based on the response data, even if the HTTP response was OK.
* Improved master node performance in order to not get bottlenecked when using enough slaves (>100)
* Minor improvements in web interface.
* Fixed missing template dir in MANIFEST file causing locust installed with "setup.py install" not to work.
