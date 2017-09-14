=====================
Using other languages
=====================

A Locust master and a Locust slave communicate by exchanging `msgpack <http://msgpack.org/>`_ messages, which is
supported by many languages. So, you can write your Locust tasks in any languages you like. For convenience, some
libraries do the job as a slave runner. They run your Locust tasks, and report to master regularly.


Boomer
======

`Boomer <https://github.com/myzhan/boomer/>`_ is a Locust slave runner written in golang.
