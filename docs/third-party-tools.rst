=====================
Third party tools
=====================

Using other languages
=====================

A Locust master and a Locust slave communicate by exchanging `msgpack <http://msgpack.org/>`_ messages, which is
supported by many languages. So, you can write your Locust tasks in any languages you like. For convenience, some
libraries do the job as a slave runner. They run your Locust tasks, and report to master regularly.


Boomer (Golang)
---------------

`Boomer <https://github.com/myzhan/boomer/>`_ is a Locust slave runner written in golang.

Locust4j (Java)
---------------

`Locust4j <https://github.com/myzhan/locust4j>`_ is a Locust slave runner written in Java.


Configuration Management
========================

Deploying Locust is easy, but here and there some tools can still provide a measure of convenience.

`tinx.locust <https://github.com/tinx/ansible-role-locust>`_ is an Ansible role to install, configure and
control Locust as a systemd service, or to build Locust docker images using ansible-container. Also
manages locustfiles and accompanying test data.
