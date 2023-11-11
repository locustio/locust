# Locust

[![PyPI](https://img.shields.io/pypi/v/locust.svg)](https://pypi.org/project/locust/)
[![PyPI](https://img.shields.io/pypi/pyversions/locust.svg)](https://pypi.org/project/locust/)
[![Build Status](https://github.com/locustio/locust/workflows/Tests/badge.svg)](https://github.com/locustio/locust/actions?query=workflow%3ATests)
[![license](https://img.shields.io/github/license/locustio/locust.svg)](https://github.com/locustio/locust/blob/master/LICENSE)
[![GitHub contributors](https://img.shields.io/github/contributors/locustio/locust.svg)](https://github.com/locustio/locust/graphs/contributors)
[![Support Ukraine Badge](https://bit.ly/support-ukraine-now)](https://github.com/support-ukraine/support-ukraine)

Locust is an easy to use, scriptable and scalable performance testing tool. You define your load test in regular Python code, instead of being constrained by a UI or domain specific language that only pretends to be real code. This makes Locust infinitely expandable and very developer friendly.

To get started right away, head over to the [documentation](http://docs.locust.io/en/stable/installation.html).

## Features

#### Write user test scenarios in plain old Python

If you want your users to loop, perform some conditional behaviour or do some calculations, you just use the regular programming constructs provided by Python. Locust runs every user inside its own greenlet (a lightweight process/coroutine). This enables you to write your tests like normal (blocking) Python code instead of having to use callbacks or some other mechanism. Because your scenarios are “just python” you can use your regular IDE, and version control your tests as regular code (as opposed to some other tools that use XML or binary formats)

```python
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.client.post("/login", json={"username":"foo", "password":"bar"})

    @task
    def hello_world(self):
        self.client.get("/hello")
        self.client.get("/world")

    @task(3)
    def view_item(self):
        for item_id in range(10):
            self.client.get(f"/item?id={item_id}", name="/item")
```

#### Distributed & Scalable - supports hundreds of thousands of users

Locust makes it easy to run load tests distributed over multiple machines. It is event-based (using [gevent](http://www.gevent.org/)), which makes it possible for a single process to handle many thousands concurrent users. While there may be other tools that are capable of doing more requests per second on a given hardware, the low overhead of each Locust user makes it very suitable for testing highly concurrent workloads.

#### Web-based UI

Locust has a user friendly web interface that shows the progress of your test in real-time. You can even change the load while the test is running. It can also be run without the UI, making it easy to use for CI/CD testing.

<img src="https://raw.githubusercontent.com/locustio/locust/master/locust/static/img/ui-screenshot-charts.png" alt="Locust UI charts" width="200"/> <img src="https://raw.githubusercontent.com/locustio/locust/master/locust/static/img/ui-screenshot-stats.png" alt="Locust UI stats" width="200"/> <img src="https://raw.githubusercontent.com/locustio/locust/master/locust/static/img/ui-screenshot-workers.png" alt="Locust UI workers" width="200"/> <img src="https://raw.githubusercontent.com/locustio/locust/master/locust/static/img/ui-screenshot-start-test.png" alt="Locust UI start test" width="200"/>

#### Can test any system

Even though Locust primarily works with web sites/services, it can be used to test almost any system or protocol. Just [write a client](https://docs.locust.io/en/latest/testing-other-systems.html#testing-other-systems) for what you want to test, or [explore some created by the community](https://github.com/SvenskaSpel/locust-plugins#users).

## Hackable

Locust's code base is intentionally kept small and doesn't solve everything out of the box. Instead, we try to make it easy to adapt to any situation you may come across, using regular Python code. There is nothing stopping you from: 

* [Send real time reporting data to TimescaleDB and visualize it in Grafana](https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/dashboards/README.md)
* [Wrap calls to handle the peculiarities of your REST API](https://github.com/SvenskaSpel/locust-plugins/blob/8af21862d8129a5c3b17559677fe92192e312d8f/examples/rest_ex.py#L87) 
* [Use a totally custom load shape/profile](https://docs.locust.io/en/latest/custom-load-shape.html#custom-load-shape)
* ...

## Links

* Documentation: [docs.locust.io](https://docs.locust.io)
* Support/Questions: [StackOverflow](https://stackoverflow.com/questions/tagged/locust)
* Chat/discussion: [Slack](https://locustio.slack.com) [(signup)](https://communityinviter.com/apps/locustio/locust)

## Authors

* Maintainer: [Lars Holmberg](https://github.com/cyberw)
* Modern UI: [Andrew Baldwin](https://github.com/andrewbaldwin44)
* Original creator: [Jonatan Heyman](https://github.com/heyman)
* Massive thanks to [all of our contributors](https://github.com/locustio/locust/graphs/contributors)

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).
