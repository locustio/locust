Locust
======
Scalable user load testing tool.

Locust is an easy-to-use user load testing tool. Intended for load testing web sites (or other systems) and figuring
out how many concurrent users your system can handle.

The scalability is due to being completely event-based. Thus, making ideal for supporting thousands of concurrent users on a single machine.
In contrast to many other event-based apps it doesn't use callbacks. Instead it uses light-weight processes, similar to what Erlang has.
Each locust (aka users) swarming your site is actually running inside it's own process (or greenlet, to be correct).
This allows you write very expressive scenarios without complicating your code with callbacks.


### Features
* *Write user test scenarios in plain-old Python*<br>
 No need for clunky UIs or bloated XML, just code as you normally would. Based on coroutines instead of callbacks (aka boomerang code) also makes it look and behave like synchronous Python code.

* *Scalable - supports thousands users*<br>
 Being event based it can handle thousands of users in a single process.
 Even if you simulate that many users, not all are actively hitting your system. Often, users are idle figuring out what to do next.

* *Web-based UI*<br>
 Locust has a neat HTML+JS that shows all relevent test details in real-time. And since the UI is web-based,
 it's cross-platform and easily extendable. Monitoring your data through a console or log files is ineffective and stupid

* *Can test any system*<br>
 Even though Locust is oriented towards testing websites, it can be used to test almost any system. Just write a client for what you wish to test and swarm it with locusts! It's super easy!

* *Hackable*<br>
 Locust is very small and very hackable. All heavy-lifting parts of I/O and coroutines is delegated to gevent.

## Example
Let me show you a quick little introduction of how easy it is to write tests.
To get started you simple need write a normal Python function (or greenlet) to define the behavior of your swarming locusts.

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

