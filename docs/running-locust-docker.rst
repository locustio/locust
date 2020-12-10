.. _running-locust-docker:

=================================
Running Locust with Docker
=================================

The official Docker image is currently found at `locustio/locust <https://hub.docker.com/r/locustio/locust>`_.

The docker image can be used like this (assuming that the ``locustfile.py`` exists in the current working directory)::

    docker run -p 8089:8089 -v $PWD:/mnt/locust locustio/locust -f /mnt/locust/locustfile.py


Docker Compose
==============

Here's an example Docker Compose file that could be used to start both a master node, and worker nodes:

.. literalinclude:: ../examples/docker-compose/docker-compose.yml
    :language: yaml

The above compose configuration could be used to start a master node and 4 workers using the following command::

    docker-compose up --scale worker=4


Use docker image as a base image
================================

It's very common to have test scripts that rely on third party python packages. In those cases you can use the
official Locust docker image as a base image::

    FROM locustio/locust
    RUN pip3 install some-python-package


Running a distributed load test on Kubernetes
=============================================

The easiest way to run Locust on Kubernetes is to use a Helm chart. A Helm chart will package all settings and kubernetes resources together into an easy to manage way.

Currently the most up to date Helm chart is here: `github.com/deliveryhero/helm-charts <https://github.com/deliveryhero/helm-charts/tree/master/stable/locust>`_

Note: this Helm chart is not maintained or supported directly by Locust maintainers.
