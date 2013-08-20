##########
Changelog
##########

0.7 (In GIT repo, Not yet released)
===================================

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

requests updated to version 1.2
-------------------------------

Locust updated `requests <http://python-requests.org/>`_ to the latest major release.

.. note::

   Requests 1.0 introduced some major API changes. Please check if you
   are using any internal features and check the documentation:
   `Migrating to 1.x <http://docs.python-requests.org/en/latest/api/#migrating-to-1-x>`_


Big refactoring of request statistics code
------------------------------------------

Refactored :py:class:`RequestStats`.

* Created :py:class:`StatsEntry` which represents a single stats entry (URL).

Previously the :py:class:`RequestStats` was actually doing two different things:

* It was holding track of the aggregated stats from all requests
* It was holding the stats for single stats entries.

Now RequestStats should be instantiated and holds the global stats, as well as a dict of StatsEntry instances which holds the stats for single stats entries (URLs)


Other changes
-------------

* You can now specify the port on which to run the web host
* Various code cleanups
* Updated gevent/zmq libraries
* Switched to unittest2 discovery



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
  was given to the method was passed on to the the task when it was called. It no longer accepts extra arguments. 
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
