##########
Changelog
##########

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

Previously one could specify avg_wait to :py:class:`TaskSet` and :py:class:`Locust` that Locust would try to strive to. However this can be sufficiently accomplished by using min_wait and max_wait for most use-cases. Therefore we've decided to remove the avg_wait as it's use-case is not clear or just too narrow to be in the Locust core.

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
