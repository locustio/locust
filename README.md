# Locust

[![Build Status](https://secure.travis-ci.org/locustio/locust.png)](http://travis-ci.org/locustio/locust) 
[![Gitter Chat](https://badges.gitter.im/locustio/locust.png)](https://gitter.im/locustio/locust) 

## Links

* Website: <a href="http://locust.io">locust.io</a>
* Documentation: <a href="http://docs.locust.io">docs.locust.io</a>

## Description

Locust is an easy-to-use, distributed, user load testing tool. Intended for load testing web sites (or other systems) and figuring
out how many concurrent users a system can handle.

The idea is that during a test, a swarm of locusts will attack your website. The behavior of each locust (or test user if you will) is 
defined by you and the swarming process is monitored from a web UI in real-time. This will help you battle test and identify bottlenecks 
in your code before letting real users in.

Locust is completely event based, and therefore it's possible to support thousands of concurrent users on a single machine.
In contrast to many other event-based apps it doesn't use callbacks. Instead it uses light-weight processes, through <a href="http://www.gevent.org/">gevent</a>.
Each locust swarming your site is actually running inside it's own process (or greenlet, to be correct).
This allows you to write very expressive scenarios in Python without complicating your code with callbacks.


## Features
* **Write user test scenarios in plain-old Python**<br>
 No need for clunky UIs or bloated XML, just code as you normally would. Based on coroutines instead of callbacks (aka boomerang code) allows code to look and behave like normal, blocking Python code.

* **Distributed & Scalable - supports hundreds of thousands of users**<br>
 Locust supports running load tests distributed over multiple machines.
 Being event based, even one Locust node can handle thousands of users in a single process.
 Part of the reason behind this is that even if you simulate that many users, not all are actively hitting your system. Often, users are idle figuring out what to do next. Request per second != number of users online.

* **Web-based UI**<br>
 Locust has a neat HTML+JS that shows all relevent test details in real-time. And since the UI is web-based, it's cross-platform and easily extendable. 

* **Can test any system**<br>
 Even though Locust is web-oriented, it can be used to test almost any system. Just write a client for what ever you wish to test and swarm it with locusts! It's super easy!

* **Hackable**<br>
 Locust is very small and very hackable and we intend to keep it that way. All heavy-lifting of evented I/O and coroutines are delegated to gevent. The brittleness of alternative testing tools was the reason we created Locust.


## Documentation

More info and documentation can be found at: <a href="http://docs.locust.io/">http://docs.locust.io/</a>


## Authors

- <a href="http://cgbystrom.com">Carl Bystr&ouml;m</a> (@<a href="http://twitter.com/cgbystrom">cgbystrom</a> on Twitter)
- <a href="http://heyman.info">Jonatan Heyman</a> (@<a href="http://twitter.com/jonatanheyman">jonatanheyman</a> on Twitter)
- Joakim Hamrén (@<a href="http://twitter.com/Jahaaja">Jahaaja</a>)
- Hugo Heyman (@<a href="http://twitter.com/hugoheyman">hugoheyman</a>)

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).

