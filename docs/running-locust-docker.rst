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

The path inside the container to the locustfile. Defaults to '/locustfile.py`

- ``LOCUST_MASTER_HOST``

The hostname of the master.

- ``LOCUST_MASTER_PORT``

The port used to communicate with the master. Defaults to 5557.


Add your tests
---------------------------------------------

The easiest way to get your tests running is to build an image with your test file built in. Once you've 
written your locustfile you can bake it into a Docker image with a simple ``Dockerfile``:

```
FROM locustio/locust
ADD locustfile.py locustfile.py
```

You'll need to push the built image to a Docker repository such as Dockerhub, AWS ECR, or GCR in order for
distributed infrastructure to be able to pull the image. See your chosen repository's documentation on how
to authenticate with the repository to pull the image.
