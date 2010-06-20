Locust
======
Scalable user load testing tool.

Locust is an easy-to-use user load testing tool. Intended for load testing web sites (or other systems) and figuring
out how many concurrent users your system can handle.

The idea is that during a test, a swarm of locusts will attack your website. They will hammer it until they find the breaking point of your site. The behavior of each locust (or test user if you will) is defined by you and the swarming process is monitored from web UI in real-time. This will help you battle test and identify bottlenecks in your code before letting real users in.

The scalability comes from being completely event-based. Thus making it possible to support thousands of concurrent users on a single machine.
In contrast to many other event-based apps it doesn't use callbacks. Instead it uses light-weight processes, similar Erlang but without the quirkiness.
Each locust swarming your site is actually running inside it's own process (or greenlet, to be correct).
This allows you to write very expressive scenarios in Python without complicating your code with callbacks.


### Features
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


### Getting started
Locust assume you have the following installed:

* Python 2.6
* gevent
* bottle

After you've installed those dependencies, clone this repo and fire up:

    python example.py

This will start a small example demonstrating Locust. Open http://localhost:8089 in your browser to start the test.


## Authors

- Carl Bystr&ouml;m (@<a href="http://twitter.com/cgbystrom">cgbystrom</a> on Twitter)

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).

