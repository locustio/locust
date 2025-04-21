# Locust

[![PyPI](https://img.shields.io/pypi/v/locust.svg)](https://pypi.org/project/locust/)<!--![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Flocustio%2Flocust%2Fmaster%2Fpyproject.toml)-->
[![Downloads](https://pepy.tech/badge/locust/week)](https://pepy.tech/project/locust)
[![GitHub contributors](https://img.shields.io/github/contributors/locustio/locust.svg)](https://github.com/locustio/locust/graphs/contributors)
[![Support Ukraine Badge](https://bit.ly/support-ukraine-now)](https://github.com/support-ukraine/support-ukraine)

Locust is an open source performance/load testing tool for HTTP and other protocols. Its developer-friendly approach lets you define your tests in regular Python code.

Locust tests can be run from command line or using its web-based UI. Throughput, response times and errors can be viewed in real time and/or exported for later analysis.

You can import regular Python libraries into your tests, and with Locust's pluggable architecture it is infinitely expandable. Unlike when using most other tools, your test design will never be limited by a GUI or domain-specific language.

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

<picture>
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/bottlenecked-server-light.png" alt="Locust UI charts" height="100" width="200"/>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/bottlenecked-server-dark.png" alt="Locust UI charts" height="100" width="200"/>
<img src="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/bottlenecked-server-light.png" alt="Locust UI charts" height="100" width="200"/>
</picture>
<picture>
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/webui-running-statistics-light.png" alt="Locust UI stats" height="100" width="200"/>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/webui-running-statistics-dark.png" alt="Locust UI stats" height="100" width="200"/>
<img src="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/webui-running-statistics-light.png" alt="Locust UI stats" height="100" width="200"/>
</picture>
<picture>
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/locust-workers-light.png" alt="Locust UI workers" height="100" width="200"/>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/locust-workers-dark.png" alt="Locust UI workers" height="100" width="200"/>
<img src="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/locust-workers-light.png" alt="Locust UI workers" height="100" width="200"/>
</picture>
<picture>
<source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/webui-splash-light.png" alt="Locust UI start test" height="100" width="200"/>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/webui-splash-dark.png" alt="Locust UI start test" height="100" width="200"/>
<img src="https://raw.githubusercontent.com/locustio/locust/refs/heads/master/docs/images/webui-splash-light.png" alt="Locust UI start test" height="100" width="200"/>
</picture>

#### Can test any system

Even though Locust primarily works with web sites/services, it can be used to test almost any system or protocol. Just [write a client](https://docs.locust.io/en/latest/testing-other-systems.html#testing-other-systems) for what you want to test, or [explore some created by the community](https://github.com/SvenskaSpel/locust-plugins#users).

## Hackable

Locust's code base is intentionally kept small and doesn't solve everything out of the box. Instead, we try to make it easy to adapt to any situation you may come across, using regular Python code. There is nothing stopping you from: 

* [Send real time reporting data to TimescaleDB and visualize it in Grafana](https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/dashboards/README.md)
* [Wrap calls to handle the peculiarities of your REST API](https://github.com/SvenskaSpel/locust-plugins/blob/8af21862d8129a5c3b17559677fe92192e312d8f/examples/rest_ex.py#L87) 
* [Use a totally custom load shape/profile](https://docs.locust.io/en/latest/custom-load-shape.html#custom-load-shape)
* [...](https://github.com/locustio/locust/wiki/Extensions)

## Links

* Documentation: [docs.locust.io](https://docs.locust.io)
* Support/Questions: [StackOverflow](https://stackoverflow.com/questions/tagged/locust)
* Github Discussions: [Github Discussions](https://github.com/orgs/locustio/discussions)
* Chat/discussion: [Slack](https://locustio.slack.com) [(signup)](https://communityinviter.com/apps/locustio/locust)

## Authors

* Maintainer: [Lars Holmberg](https://github.com/cyberw)
* UI: [Andrew Baldwin](https://github.com/andrewbaldwin44)
* Original creator: [Jonatan Heyman](https://github.com/heyman)
* Massive thanks to [all of our contributors](https://github.com/locustio/locust/graphs/contributors)

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).
