# Locust

[![Build Status](https://travis-ci.com/locustio/locust.svg?branch=master)](https://travis-ci.com/locustio/locust)
[![codecov](https://codecov.io/gh/locustio/locust/branch/master/graph/badge.svg)](https://codecov.io/gh/locustio/locust)
[![license](https://img.shields.io/github/license/locustio/locust.svg)](https://github.com/locustio/locust/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/locust.svg)](https://pypi.org/project/locust/)
[![PyPI](https://img.shields.io/pypi/pyversions/locust.svg)](https://pypi.org/project/locust/)
[![GitHub contributors](https://img.shields.io/github/contributors/locustio/locust.svg)](https://github.com/locustio/locust/graphs/contributors)

## Links

* Website: <a href="https://locust.io">locust.io</a>
* Documentation: <a href="https://docs.locust.io">docs.locust.io</a>
* Code/issues: <a href="https://github.com/locustio/locust">Github</a>
* Support/Questions: <a href="https://stackoverflow.com/questions/tagged/locust">StackOverflow</a>
* Chat/discussion: [Slack signup](https://slack.locust.io/)

## Description

Locust is an easy to use, scriptable and scalable performance testing tool.

You define the behaviour of your users in regular Python code, instead of using a clunky UI or domain specific language.

This makes Locust infintely expandable and very developer friendly.

## Features

* **Write user test scenarios in plain-old Python**<br>

 If you want your users to loop, perform some conditional behaviour or do some calculations, you just use the regular programming constructs provided by Python. Locust runs every user inside its own greenlet (a lightweight process/coroutine). This enables you to write your tests like normal (blocking) Python code instead of having to use callbacks or some other mechanism.
 Because your scenarios are "just python" you can use your regular IDE, and version control your tests as regular code (as opposed to some other tools that use XML or binary formats)

* **Distributed & Scalable - supports hundreds of thousands of users**<br>

 Locust makes it easy to run load tests distributed over multiple machines.
 It is event-based (using <a href="http://www.gevent.org/">gevent</a>), which makes it possible for a single process to handle many thousands concurrent users. While there may be other tools that are capable of doing more requests per second on a given hardware, the low overhead of each Locust user makes it very suitable for testing highly concurrent workloads.
 
* **Web-based UI**<br>

 Locust has a user friendly web interface that shows the progress of your test in real-time.

* **Can test any system**<br>

 Even though Locust primarily works with web sites/services, it can be used to test almost any system or protocol.

* **Hackable**

 Locust is small and very flexible and we intend to keep it that way.

## Documentation

More info and documentation can be found at: <a href="https://docs.locust.io/">https://docs.locust.io/</a>

## Authors

- <a href="http://cgbystrom.com">Carl Bystr&ouml;m</a> (@<a href="https://twitter.com/cgbystrom">cgbystrom</a> on Twitter)
- <a href="http://heyman.info">Jonatan Heyman</a> (@<a href="https://twitter.com/jonatanheyman">jonatanheyman</a> on Twitter)
- Joakim Hamrén (@<a href="https://twitter.com/Jahaaja">Jahaaja</a>)
- Hugo Heyman (@<a href="https://twitter.com/hugoheyman">hugoheyman</a>)
- Lars Holmberg

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).