<img src="http://github.com/cgbystrom/locust/raw/master/public/locust_banner.png" width="901" height="129"><br><br>

Locust is an easy-to-use user load testing tool. Intended for load testing web sites (or other systems) and figuring
out how many concurrent users your system can handle.

The idea is that during a test, a swarm of locusts will attack your website. They will hammer it until they find the breaking point of your site. The behavior of each locust (or test user if you will) is defined by you and the swarming process is monitored from a web UI in real-time. This will help you battle test and identify bottlenecks in your code before letting real users in.

The scalability comes from being completely event-based. Thus making it possible to support thousands of concurrent users on a single machine.
In contrast to many other event-based apps it doesn't use callbacks. Instead it uses light-weight processes, similar Erlang but without the quirkiness.
Each locust swarming your site is actually running inside it's own process (or greenlet, to be correct).
This allows you to write very expressive scenarios in Python without complicating your code with callbacks.


## Features
* **Write user test scenarios in plain-old Python**<br>
 No need for clunky UIs or bloated XML, just code as you normally would. Based on coroutines instead of callbacks (aka boomerang code) allows code to look and behave like normal, blocking Python code.

* **Scalable - supports thousands users**<br>
 Being event based, Locust can handle thousands of users in a single process.
 Part of the reason behind this is that even if you simulate that many users, not all are actively hitting your system. Often, users are idle figuring out what to do next. Request per second != number of users online.

* **Web-based UI**<br>
 Locust has a neat HTML+JS that shows all relevent test details in real-time. And since the UI is web-based,
 it's cross-platform and easily extendable. Monitoring your data through a console or log files is ineffective and stupid

* **Can test any system**<br>
 Even though Locust is web-oriented, it can be used to test almost any system. Just write a client for what you wish to test and swarm it with locusts! It's super easy!

* **Hackable**<br>
 Locust is very small and very hackable and I intend to keep it that way. All heavy-lifting of evented I/O and coroutines are delegated to gevent. The brittleness of alternative testing tools was the reason I created Locust.


## Example
Below is a quick little example of how easy it is to write tests.
To get started, you simply need write a normal Python function to define the behavior of your swarming locusts.

    def website_user(name):
        c = HTTPClient('http://localhost:8088')
        for i in range(0, 10):
            # Request the fast page, wait for the response
            c.get('/fast', name='Fast page')
            # Response received!

            # Think for 5 seconds
            gevent.sleep(5)
            
            # Done thinking. Request the slow page...
            c.get('/slow', name='Slow page')

        # Loop ended, function will exit. Locust dies


## Getting started
Locust assume you have the following installed:

* Python 2.6
* gevent (coroutine library, see http://www.gevent.org/)
* bottle (the web UI uses bottle, install with "easy_install -U bottle")

After you've installed those dependencies, clone this repo and fire up:

    python example.py

This will start a small example demonstrating Locust. Open http://localhost:8089 in your browser to start the test.

## Background
Locust was created because I was fed up with existing solutions. None of them are solving the right problem and to me, they are missing the point.
I've tried both Apache JMeter and Tsung. Both tools are quite ok to use, I've used the former many times benchmarking stuff at work. JMeter comes with UI which you might think for second is a good thing. But you soon realize it's a PITA to "code" your testing scenarios through some point-and-click interface. Secondly, JMeter is thread-bound. This means for every user you want to simulate, you need a separate thread. Needless to say, benchmarking thousands of users on a single machine just isn't feasible.

Tsung, on the other hand, does not have these thread issues as it's written Erlang. It can make use of the light-weight processes offered by BEAM itself and happily scale up. But when it comes to defining the scenarios, Tsung is as limited as JMeter. It offers an XML-based DSL to define how a user should behave when testing. I guess you can imagine the horror of "coding" this. Displaying any sorts of graphs or reports when completed requires you post-process the log files generated from the test. Only then can you get an understanding of how the test went. Silly.

Anyway, I've tried to address these issues when creating Locust. Hopefully none of the above painpoints should exist.
However, the current version of Locust has only a fraction of the features. Mostly because this project is so young and I haven't been able to put the time in. But it's also because I want Locust to stay minimal. Java GUIs and XML DSLs don't belong here.

I guess you could say I'm really just trying to scratch my own itch here. I hope others will find it as useful as I do.

## Roadmap
Fair to say, Locust is still early in development. Just the basics have been put into place.
This means you probably are missing some features. But really, you shouldn't despair.
It's really easy to hack in new features. Every thing is normal Python together with HTML, CSS and JavaScript.

There are a few things that could be useful to implement:

* **Support for workers**
As you need to scale beyond a single process, a way of dealing with remote processes is needed.
Most likely way of solving this would be to add support for worker process that are controlled from a master process.

* **Charts/graphs**
A way to represent the numbers more visually through charts/graphs/sparklines. The Raphael JS library looks like a good candidate for doing this.

* **Use Web Sockets instead of polling**
While not that important, it would be nice to use Web Sockets instead of dirty old AJAX polling.
However, polling works just fine right now as the number of users using the web UI are expected to quite few :)

* **View resource utilization of "victims"**
To see the load of the machines currently being swarmed would be nice. Helpful when tracking sluggish requests.


## Authors

- Carl Bystr&ouml;m (@<a href="http://twitter.com/cgbystrom">cgbystrom</a> on Twitter)

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).

