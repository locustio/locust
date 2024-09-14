# Overview

### Prerequisites:

- [`gevent`](https://www.gevent.org/install.html)
  - [For pymongo to use greenlets instead of standard threads](https://pymongo.readthedocs.io/en/stable/examples/gevent.html)
- [`pymongo`](https://pymongo.readthedocs.io/en/stable/installation.html)

### How to run the test:

- Set your environment variables for:
  `MONGODB_URI`

- Run locust as usual, see https://docs.locust.io/en/stable/quickstart.html

Note:

- It is recommended that you use the `--processes` parameter when running this test
  - see https://docs.locust.io/en/stable/running-distributed.html
