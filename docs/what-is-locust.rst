===============================
What is Locust?
===============================

Locust is an easy-to-use, distributed, user load testing tool. It is intended for load-testing web sites
(or other systems) and figuring out how many concurrent users a system can handle.

The idea is that during a test, a swarm of `locusts <http://en.wikipedia.org/wiki/Locust>`_ 
will attack your website. The behavior of each 
locust (or test user if you will) is defined by you and the swarming process is monitored from a 
web UI in real-time. This will help you battle test and identify bottlenecks in your code before 
letting real users in.

Locust is completely event-based, and therefore it's possible to support thousands of concurrent
users on a single machine. In contrast to many other event-based apps it doesn't use callbacks. 
Instead it uses light-weight processes, through `gevent <http://www.gevent.org/>`_. Each locust 
swarming your site is actually running inside its own process (or greenlet, to be correct). This
allows you to write very expressive scenarios in Python without complicating your code with callbacks.


Features
========

* **Write user test scenarios in plain-old Python**

 No need for clunky UIs or bloated XML—just code as you normally would. Based on coroutines instead
 of callbacks, your code looks and behaves like normal, blocking Python code.

* **Distributed & Scalable - supports hundreds of thousands of users**

 Locust supports running load tests distributed over multiple machines.
 Being event-based, even one Locust node can handle thousands of users in a single process.
 Part of the reason behind this is that even if you simulate that many users, not all are actively 
 hitting your system. Often, users are idle figuring out what to do next. 
 Requests per second != number of users online.

* **Web-based UI**

 Locust has a neat HTML+JS user interface that shows relevant test details in real-time. And since 
 the UI is web-based, it's cross-platform and easily extendable. 

* **Can test any system**

 Even though Locust is web-oriented, it can be used to test almost any system. Just write a client 
 for what ever you wish to test and swarm it with locusts! It's super easy!

* **Hackable**

 Locust is small and very hackable and we intend to keep it that way. All heavy-lifting of evented 
 I/O and coroutines are delegated to gevent. The brittleness of alternative testing tools was the 
 reason we created Locust.

Background
==========

Locust was created because we were fed up with existing solutions. None of them are solving the 
right problem and to me, they are missing the point. We've tried both Apache JMeter and Tsung. 
Both tools are quite OK to use; we've used the former many times benchmarking stuff at work.
JMeter comes with a UI, which you might think for a second is a good thing. But you soon realize it's
a PITA to "code" your testing scenarios through some point-and-click interface. Secondly, JMeter 
is thread-bound. This means for every user you want to simulate, you need a separate thread. 
Needless to say, benchmarking thousands of users on a single machine just isn't feasible.

Tsung, on the other hand, does not have these thread issues as it's written in Erlang. It can make 
use of the light-weight processes offered by BEAM itself and happily scale up. But when it comes to 
defining the test scenarios, Tsung is as limited as JMeter. It offers an XML-based DSL to define how 
a user should behave when testing. I guess you can imagine the horror of "coding" this. Displaying 
any sorts of graphs or reports when completed requires you to post-process the log files generated from
the test. Only then can you get an understanding of how the test went.

Anyway, we've tried to address these issues when creating Locust. Hopefully none of the above 
pain points should exist.

I guess you could say we're really just trying to scratch our own itch here. We hope others will 
find it as useful as we do.

Authors
=======

- `Jonatan Heyman <http://heyman.info>`_ (`@jonatanheyman <https://twitter.com/jonatanheyman>`_ on Twitter)
- Carl Byström (`@cgbystrom <https://twitter.com/cgbystrom>`_ on Twitter)
- Joakim Hamrén (`@Jahaaja <https://twitter.com/Jahaaja>`_ on Twitter)
- Hugo Heyman (`@hugoheyman <https://twitter.com/hugoheyman>`_ on Twitter)

License
=======

Open source licensed under the MIT license (see LICENSE file for details).

