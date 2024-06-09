.. _extensions:

======================
Third party extensions
======================

Support for load testing other protocols, reporting etc
-------------------------------------------------------

-  `locust-plugins <https://github.com/SvenskaSpel/locust-plugins/>`__

   -  request logging & graphing
   -  new protocols like websockets, selenium/webdriver, http users that
      load html page resources
   -  readers (ways to get test data into your tests)
   -  wait time (custom wait time functions)
   -  debug (support for running a single user in the debugger)
   -  checks (adds command line parameters to set locust exit code based
      on requests/s, error percentage and average response times)

Automate distributed runs over SSH
----------------------------------

-  `locust-swarm <https://github.com/SvenskaSpel/locust-swarm/>`__

Automatically translate a browser recording (HAR-file) to a locustfile
----------------------------------------------------------------------

-  `har2locust <https://github.com/SvenskaSpel/har2locust>`__

Workers written in other languages than Python
----------------------------------------------

A Locust master and a Locust worker communicate by exchanging
`msgpack <http://msgpack.org/>`__ messages, which is supported by many
languages. So, you can write your User tasks in any languages you like.
For convenience, some libraries do the job as a worker runner. They run
your User tasks, and report to master regularly.

-  `Boomer <https://github.com/myzhan/boomer/>`__ - Go
-  `Locust4j <https://github.com/myzhan/locust4j>`__ - Java
