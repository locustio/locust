=====================
Third party tools
=====================

Support for other sampler protocols, reporting etc
==================================================

- `Locust Plugins <https://github.com/SvenskaSpel/locust-plugins/>`_


Automate distributed runs with no manual steps
==============================================

- `Locust Swarm <https://github.com/SvenskaSpel/locust-swarm/>`_


Using other languages
=====================

A Locust master and a Locust worker communicate by exchanging `msgpack <http://msgpack.org/>`_ messages, which is
supported by many languages. So, you can write your User tasks in any languages you like. For convenience, some
libraries do the job as a worker runner. They run your User tasks, and report to master regularly.


Golang
---------------

- `Boomer <https://github.com/myzhan/boomer/>`_

Java
---------------

- `Locust4j <https://github.com/myzhan/locust4j>`_

- `Swarm <https://github.com/anhldbk/swarm>`_


Configuration Management
========================

Deploying Locust is easy, but here and there some tools can still provide a measure of convenience.

`tinx.locust <https://github.com/tinx/ansible-role-locust>`_ is an Ansible role to install, configure and
control Locust as a systemd service, or to build Locust docker images using ansible-container. Also
manages locustfiles and accompanying test data.

Further reading
===============

- `An introduction to Locust for JMeter users <https://howardosborne.github.io/locust_for_jmeter_users/>`_
