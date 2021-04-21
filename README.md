# Bevy's Locust Fork

## Manging the Bevy Locust Fork

Bevy maintains a custom fork of locust to allow us to have custom features server-side that are not in the base locustio/locust package.
Out of consideration for the maintainers of this open-source tool, it is recommended that if you intend to contribute to the Bevy 
Locust fork that you follow the git recommended patterns for working with upstream remotes. An overview of those upstream patterns 
can be found [here](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes) and a how-to guide for managing remotes can 
be found [here](https://docs.github.com/en/github/getting-started-with-github/managing-remote-repositories). 

A specific guide for configuring a remote for a fork can be found [here](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/configuring-a-remote-for-a-fork).

The basics for contributing are these:

1) Clone a copy of this repo - `bevy/locust` - to your machine. In doing so, git will likely preset the origin push and pull urls 
for you. You can find this out with `git remote -v`:

```
git remote -v
origin  git@github.com:bevy/locust.git (fetch)
origin  git@github.com:bevy/locust.git (push)
```

This should probably be enough for contributing new Bevy-specific features. However, since `locustio/locust` is an actively maintained project 
as of this writing, there might ocassionaly be a need to update the `bevy/locust` fork from the upstream `locustio/locust` repo. 

2) If you need to pull new features from `locustio/locust` , then first add the original repo as an upstream:

```
git remote add upstream git@github.com:locustio/locust.git
```

Calling `git remote -v` should indicate that `locustio/locust` is configured as an upstream now:

```
git remote -v                                             
origin  git@github.com:bevy/locust.git (fetch)
origin  git@github.com:bevy/locust.git (push)
upstream    git@github.com:locustio/locust.git (fetch)
upstream    git@github.com:locustio/locust.git (push)
```

3) Out of respect for the maintainers of `locustio/locust`, disable upstream pushes in order to avoid accidental pushes to the 
original project's repository.

```
git remote set-url --push upstream no_push
```

Which yields:

```
git remote -v                                       
origin  git@github.com:bevy/locust.git (fetch)
origin  git@github.com:bevy/locust.git (push)
upstream    git@github.com:locustio/locust.git (fetch)
upstream    no_push (push)
```

This is a bit hacky, but it prevents accidental pushes to the original package:

```
git push upstream
fatal: 'no_push' does not appear to be a git repository
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

## locustio/locust updates

[![Build Status](https://github.com/locustio/locust/workflows/Tests/badge.svg)](https://github.com/locustio/locust/actions?query=workflow%3ATests)
[![codecov](https://codecov.io/gh/locustio/locust/branch/master/graph/badge.svg)](https://codecov.io/gh/locustio/locust)
[![license](https://img.shields.io/github/license/locustio/locust.svg)](https://github.com/locustio/locust/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/locust.svg)](https://pypi.org/project/locust/)
[![PyPI](https://img.shields.io/pypi/pyversions/locust.svg)](https://pypi.org/project/locust/)
[![GitHub contributors](https://img.shields.io/github/contributors/locustio/locust.svg)](https://github.com/locustio/locust/graphs/contributors)

Locust is an easy to use, scriptable and scalable performance testing tool. You define the behaviour of your users in regular Python code, instead of using a clunky UI or domain specific language. This makes Locust infinitely expandable and very developer friendly.

## Features

#### Write user test scenarios in plain-old Python

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

Locust is small and very flexible and we intend to keep it that way. If you want to [send reporting data to that database & graphing system you like](https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/listeners.py), wrap calls to a REST API to handle the particulars of your system or run a [totally custom load pattern](https://docs.locust.io/en/latest/generating-custom-load-shape.html#generating-custom-load-shape), there is nothing stopping you!

## Links

* Website: [locust.io](https://locust.io)
* Documentation: [docs.locust.io](https://docs.locust.io)
* Code/issues: [Github](https://github.com/locustio/locust)
* Support/Questions: [StackOverflow](https://stackoverflow.com/questions/tagged/locust)
* Chat/discussion: [Slack signup](https://slack.locust.io/)

## Authors

* [Carl Bystr](http://cgbystrom.com) ([@cgbystrom](https://twitter.com/cgbystrom) on Twitter)
* [Jonatan Heyman](http://heyman.info) ([@jonatanheyman](https://twitter.com/jonatanheyman) on Twitter)
* [Joakim Hamrén](https://github.com/Jahaja) ([@Jahaaja](https://twitter.com/Jahaaja) on Twitter)
* [Hugo Heyman](https://github.com/HeyHugo) ([@hugoheyman](https://twitter.com/hugoheyman) on Twitter)
* [Lars Holmberg](https://github.com/cyberw)

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).
