.. _running-locust-docker:

=================================
Running Locust with Docker
=================================

To keep things simple we provide a single Docker image that can run standalone, as a master, or as a slave.

Environment Variables
---------------------------------------------

- ``LOCUST_MODE``

One of 'standalone', 'master', or 'slave'. Defaults to 'standalone'.

- ``LOCUSTFILE_PATH``

The path inside the container to the locustfile. Defaults to '/locustfile.py'

- ``LOCUST_MASTER_HOST``

The hostname of the master.

- ``LOCUST_MASTER_PORT``

The port used to communicate with the master. Defaults to 5557.

- ``LOCUST_OPTS``

Additional options to pass to locust. Defaults to ''

Running your tests
---------------------------------------------

The easiest way to get your tests running is to build an image with your test file built in. Once you've
written your locustfile you can bake it into a Docker image with a simple ``Dockerfile``:

.. code-block:: docker

    FROM locustio/locust
    ADD locustfile.py locustfile.py


You'll need to push the built image to a Docker repository such as Dockerhub, AWS ECR, or GCR in order for
distributed infrastructure to be able to pull the image. See your chosen repository's documentation on how
to authenticate with the repository to pull the image.

For debugging locally you can run a container and pass your locustfile in as a volume:

.. code-block:: console

    docker run -p 8089:8089 --volume $PWD/dir/of/locustfile:/mnt/locust -e LOCUSTFILE_PATH=/mnt/locust/locustfile.py -e TARGET_URL=https://abc.com locustio/locust


To run in standalone mode without the web UI, you can use the ``LOCUST_OPTS`` environment variable to add the required options:

.. code-block:: console

    docker run --volume $PWD/dir/of/locustfile:/mnt/locust -e LOCUSTFILE_PATH=/mnt/locust/locustfile.py -e TARGET_URL=https://abc.com -e LOCUST_OPTS="--clients=10 --no-web --run-time=600" locustio/locust


If you are Kubernetes user, you can use the `Helm chart <https://github.com/helm/charts/tree/master/stable/locust>`_ to scale and run locust.
