==========
Changelog
==========

0.6
===

Improvements and bug fixes
--------------------------

* Scheduled task callabled can now take keyword arguments.


API Changes
-----------

* Changed signature of :func:`locust.core.Locust.schedule_task`. Previously all extra arguments that
  was given to the method was passed on to the the task when it was called. It no longer accepts extra arguments. 
  Instead, it takes an *args* argument (list) and a *kwargs* argument (dict) which are be passed to the task when 
  it's called.


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
