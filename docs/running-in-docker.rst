.. _running-in-docker:

=================
Running in Docker
=================

The official Docker image is at `locustio/locust <https://hub.docker.com/r/locustio/locust>`_.

Use it like this (assuming that the ``locustfile.py`` exists in the current working directory)::

    docker run -p 8089:8089 -v $PWD:/mnt/locust locustio/locust -f /mnt/locust/locustfile.py

On Windows, this command will sometimes cause errors. Windows users should try using this instead::

    docker run -p 8089:8089 --mount type=bind,source=$pwd,target=/mnt/locust locustio/locust -f /mnt/locust/locustfile.py

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

Running Locust using Kubernetes
===============================

See :ref:`Helm charts for Locust <helm>`