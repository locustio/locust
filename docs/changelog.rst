==========
Changelog
==========

0.4
===

.. note::

    Work in progress. Version not released.

API changes
-----------

* WebLocust class has been deprecated and is now called just Locust. The class that was previously called Locust 
  is now called LocustBase.
* The *catch_http_error* argument to HttpClient.get() and HttpClient.post() has been renamed to *allow_http_error*.

Improvements and bug fixes
--------------------------

* Added support for failing requests based on the response data, even if the HTTP response was OK.
* Improved master node performance in order to not get bottlenecked when using enough slaves (>100)
* Minor improvements in web interface.
* Fixed missing template dir in MANIFEST file causing locust installed with "setup.py install" not to work.
