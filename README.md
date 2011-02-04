<img src="http://github.com/heyman/locust/raw/master/locust/static/locust_banner.png" width="901" height="129"><br><br>

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


## Installation

First install Locust's requirements (gevent, greenlet, bottle) using:

    pip install -r requirements.txt

Then install locust:

    python setup.py install

(Soon locust will be installabe through: pip install locust.)

When Locust is installed, a **locust** command should be available in your shell (if your not using, virtualenv - which you should - make sure your python script directory is on your path).
To see available options, run:

    locust --help

Locust uses locustfiles to define it's tests. Take a look at the documentation on how to create a locustfile or check out one of the examples.

## Getting started
Below is a quick little example of a simple locustfile.py:

    from locust.core import Locust, require_once
    
    def login(l):
        l.client.post("/login", {"username":"ellen_key", "password":"education"})
    
    def index(l):
        l.client.get("/")
    
    @require_once(login)
    def profile(l):
        l.client.get("/profile")
    
    class WebsiteUser(WebLocust):
        tasks = {index:2, profile:1}
        min_wait=5000
        max_wait=9000

Here we define a number of locust tasks, which are normal Python callables that take one 
argument (a Locust class instance). These tasks are gathered under a Locust class in the *task* attribute. 

The Locust class also allows one to specify minimum and maximum wait time between the execution of 
tasks (per user/client) as well as other user behaviours.

To run Locust with the above locustfile we could run something like this:

    locust -c 100 -r 100 WebsiteUser

or if the locustfile is located elsewhere we could run:

    locust -c 100 -r 100 -f ../locust_files/my_locust_file.py WebsiteUser

The locust command must always get a Locust class argument. To list available Locust classes run:

    locust -l

or if the locustfile is located elsewhere run:

    locust -f ../locust_files/my_locust_file.py -l


## Writing a locustfile

A locustfile is a normal python file. The only requirement is that it declares at least one class, let's call it the locust class, that inherits from the Locust class
(or, when load testing a web application, the WebLocust class). The locust class has to declare a *tasks* attribute which is either a list of python callables or a 
*<callable : int>* dict. A locust class represents one website user. Locust will spawn one instance of the locust class for each user that is being simulated. The task 
attribute defines the different tasks that a website user might do. The tasks are python callables, that recieves one argument - the locust class instance representing 
the user that is performing the task. Here is an extremely simple example of a locustfile (this locsutfile won't actually load test anything):

    def my_task(l):
        pass
    
    class MyLocust(WebLocust):
        tasks = [my_task]

### The *min_wait* and *max_wait* attributes

Additionally to the tasks attribute, one usually want to declare the *min_wait* and *max_wait* attributes. These are the minimum and maximum time, in milliseconds, that
a user will wait between executing each task. *min_wait* and *max_wait* defaults to 1000, and therefore a locust will always wait 1 second between each task if *min_wait*
and *max_wait* is not declared.

With the following locustfile, each user would wait between 5 and 15 seconds between tasks:

    def my_task(l):
        pass
    
    class MyLocust(WebLocust):
        tasks = [my_task]
        min_wait = 5000
        max_wait = 15000

### The *tasks* attribute

As stated above, the tasks attribute defines the different tasks a locust user will perform. If the tasks attribute is specified as a list, each time a task is to be performed,
it will be randomly chosen from the *tasks* attribute. If however, *tasks* is a dict - with callables as keys and ints as values - the task that is to be executed will be
chosen at random but with the int as ratio. So with a tasks that looks like this:

    {my_task: 3, another_task:1}

*my_task* would be 3 times more likely to be executed than *another_task*.

### Making HTTP requests




## Background
Locust was created because we were fed up with existing solutions. None of them are solving the right problem and to me, they are missing the point.
We've tried both Apache JMeter and Tsung. Both tools are quite ok to use, we've used the former many times benchmarking stuff at work. JMeter comes with UI which you might think for second is a good thing. But you soon realize it's a PITA to "code" your testing scenarios through some point-and-click interface. Secondly, JMeter is thread-bound. This means for every user you want to simulate, you need a separate thread. Needless to say, benchmarking thousands of users on a single machine just isn't feasible.

Tsung, on the other hand, does not have these thread issues as it's written Erlang. It can make use of the light-weight processes offered by BEAM itself and happily scale up. But when it comes to defining the scenarios, Tsung is as limited as JMeter. It offers an XML-based DSL to define how a user should behave when testing. I guess you can imagine the horror of "coding" this. Displaying any sorts of graphs or reports when completed requires you post-process the log files generated from the test. Only then can you get an understanding of how the test went. Silly.

Anyway, we've tried to address these issues when creating Locust. Hopefully none of the above painpoints should exist.

I guess you could say we're really just trying to scratch our own itch here. We hope others will find it as useful as we do.

## Roadmap
Fair to say, Locust is still early in development. Just the basics have been put into place.
This means you probably are missing some features. But really, you shouldn't despair.
It's really easy to hack in new features. Every thing is normal Python together with HTML, CSS and JavaScript.

There are a few things that could be useful to implement:

* **Charts/graphs**
A way to represent the numbers more visually through charts/graphs/sparklines. The Raphael JS library looks like a good candidate for doing this.

* **Use Web Sockets instead of polling**
While not that important, it would be nice to use Web Sockets instead of dirty old AJAX polling.
However, polling works just fine right now as the number of users using the web UI are expected to quite few :)

* **View resource utilization of "victims"**
To see the load of the machines currently being swarmed would be nice. Helpful when tracking sluggish requests.

## Old screencast

<a href="http://www.screencast.com/t/YTYxNWM5N"><img src="http://github.com/cgbystrom/locust/raw/master/public/screencast_thumbnail.png" width="400" height="300"></a>

## Authors

- Carl Bystr&ouml;m (@<a href="http://twitter.com/cgbystrom">cgbystrom</a> on Twitter)
- <a href="http://heyman.info">Jonatan Heyman</a> (@<a href="http://twitter.com/jonatanheyman">jonatanheyman</a> on Twitter)

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).

