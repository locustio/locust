3rd party extensions
====================

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

Configuration Management
------------------------

-  `ansible-role-locust <https://github.com/tinx/ansible-role-locust>`__
   - an Ansible role to install, configure and control Locust as a
   systemd service, or to build Locust docker images using
   ansible-container. Also manages locustfiles and accompanying test
   data.
-  `locust_slave <https://github.com/tinx/locust_slave>`__ - an Ansible
   role to manage Locust slave instances.

Helm
----

DeliveryHero maintains an extensive list of helm charts, including `one
for
locust <https://github.com/deliveryhero/helm-charts/tree/master/stable/locust>`__.

Kubernetes Operator
-------------------

AbdelrhmanHamouda has written a `Kubernetes
Operator <https://github.com/AbdelrhmanHamouda/locust-k8s-operator>`__
for Locust

.. _rd-party-extensions-1:

3rd party extensions
====================

.. _support-for-load-testing-other-protocols-reporting-etc-1:

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

.. _automate-distributed-runs-over-ssh-1:

Automate distributed runs over SSH
----------------------------------

-  `locust-swarm <https://github.com/SvenskaSpel/locust-swarm/>`__

.. _automatically-translate-a-browser-recording-har-file-to-a-locustfile-1:

Automatically translate a browser recording (HAR-file) to a locustfile
----------------------------------------------------------------------

-  `har2locust <https://github.com/SvenskaSpel/har2locust>`__

.. _workers-written-in-other-languages-than-python-1:

Workers written in other languages than Python
----------------------------------------------

A Locust master and a Locust worker communicate by exchanging
`msgpack <http://msgpack.org/>`__ messages, which is supported by many
languages. So, you can write your User tasks in any languages you like.
For convenience, some libraries do the job as a worker runner. They run
your User tasks, and report to master regularly.

-  `Boomer <https://github.com/myzhan/boomer/>`__ - Go
-  `Locust4j <https://github.com/myzhan/locust4j>`__ - Java

.. _configuration-management-1:

Configuration Management
------------------------

-  `ansible-role-locust <https://github.com/tinx/ansible-role-locust>`__
   - an Ansible role to install, configure and control Locust as a
   systemd service, or to build Locust docker images using
   ansible-container. Also manages locustfiles and accompanying test
   data.
-  `locust_slave <https://github.com/tinx/locust_slave>`__ - an Ansible
   role to manage Locust slave instances.

.. _helm-1:

Helm
----

DeliveryHero maintains an extensive list of helm charts, including `one
for
locust <https://github.com/deliveryhero/helm-charts/tree/master/stable/locust>`__.

.. _kubernetes-operator-1:

Kubernetes Operator
-------------------

AbdelrhmanHamouda has written a `Kubernetes
Operator <https://github.com/AbdelrhmanHamouda/locust-k8s-operator>`__
for Locust
