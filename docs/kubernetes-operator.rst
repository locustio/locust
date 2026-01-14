.. _kubernetes-operator:

Kubernetes Operator
===================

The Locust Operator for Kubernetes is an operator that manages the lifecyle of :ref:`running-distributed` inside a Kubernetes cluster.

It is a Custom Resource Definition (CRD) and a Controller that run on your Kubernetes cluster and allow you to create and manage your Locust tests as Kubernetes resources.
Automatically creates master/worker jobs, mounts locustfiles, exposes the web UI, collects metrics, and handles restarts when the spec changes.


Installation
------------

Helm Charts
~~~~~~~~~~~

`Helm <https://helm.sh/>`_ is a package manager for Kubernetes that installs and manages Kubernetes applications.

1. Add the Helm repository

.. code-block:: bash

    $ helm repo add locust-operator https://locustio.github.io/k8s-operator
    "locust-operator" has been added to your repositories

    $ helm repo update
    Hang tight while we grab the latest from your chart repositories...
    ...Successfully got an update from the "locust-operator" chart repository
    Update Complete. ⎈Happy Helming!⎈

2. Install Locust Operator for Kubernetes

.. code-block:: bash

    $ helm install locust-operator locust-operator/locust-operator \
      --namespace locust-operator --create-namespace

3. Check that the operator is running and the CRD is installed

.. code-block:: bash

    $ kubectl get pods -A -l app.kubernetes.io/name=locust-operator 
    NAMESPACE         NAME                              READY   STATUS         RESTARTS   AGE
    locust-operator   locust-operator-xxxxxxxxx-xxxxx   1/1     Running        0          18s

    $ kubectl get crd                                                                                                                                                                        [none 🚀]
    NAME                       CREATED AT
    locusttests.locust.io      ...

Manifest Files
~~~~~~~~~~~~~~

Locust Operator for Kubernetes can be installed using raw manifest files with `kubectl <https://kubernetes.io/docs/reference/kubectl/>`_.
To generate the raw resources, you can use the Helm chart and output the manifests without installing them.

.. code-block:: bash

    $ helm repo add locust-operator https://locustio.github.io/k8s-operator
    $ helm repo update
    $ helm template locust-operator locust-operator/locust-operator \
      --namespace locust-operator > locust-operator.yaml

Then apply the generated manifest file:

.. code-block:: bash

    $ kubectl apply -f locust-operator.yaml


Quickstart
----------

1. Create a YAML file defining a ``LocustTest`` resource.

.. code-block:: yaml

    apiVersion: locust.io/v1
    kind: LocustTest
    metadata:
      name: load-test
    spec:
      workers: 2
      locustfile:
        content: |
          from locust import HttpUser, task
          class TestUser(HttpUser):
              @task
              def index(self):
                  self.client.get("/")

2. Apply it using ``kubectl apply -f <file>.yaml``.

3. You can verify the created resource using ``kubectl get locusttests`` and ``kubectl get pods`` to see the master and worker pods.

.. code-block:: bash

    $ kubectl apply -f locust-test.yaml
    locusttest.locust.io/load-test created

    $ kubectl get locusttests
    NAME                 STATE   WORKERS   FAIL_RATIO   RPS   USERS   AGE
    load-test            READY   2/2       0%           0     0       30s

    $ kubectl get pods -l locust.io/test-run=load-test
    NAME                       READY   STATUS    RESTARTS   AGE
    load-test-master-xxxxx     1/1     Running   0          35s
    load-test-worker-xxxxx     1/1     Running   0          35s
    load-test-worker-xxxxx     1/1     Running   0          35s

4. Access the Locust web UI by port-forwarding the service to your local machine. Then open your browser and navigate to `http://localhost:8089`.

.. code-block:: bash

   $ kubectl port-forward svc/load-test-webui 8089:8089
   Forwarding from 127.0.0.1:8089 -> 8089
   Forwarding from [::1]:8089 -> 8089

5. You can see the master logs by running:

.. code-block:: bash

  # Tailing the master pod logs directly
  $ kubectl logs -f pod/load-test-master-xxxxx

  # Using a selector to follow the master pod by labels
  $ kubectl logs -f -l locust.io/test-run=load-test,locust.io/component=master

6. Cleanup by deleting the ``LocustTest`` resource (this will also delete all managed resources):

.. code-block:: bash

  $ kubectl delete loadtest load-test


LocustTest CRD Configuration
----------------------------

General
~~~~~~~

``spec.image`` (string, required, default: ``locustio/locust:latest``)

    Container image for master and workers pods.

``spec.workers`` (integer, required, default: ``1``)

    Number of worker pods to run.

``spec.args`` (string, optional)

    Additional CLI flags, e.g. ``--run-time=5m --users=200 --spawn-rate=20``.

``spec.env`` (array, optional)

    List of environment variables to set in the container.

Locustfile source
~~~~~~~~~~~~~~~~~

``spec.locustfile`` (object, optional; choose **one**)

* ``content`` (string): inline locustfile.py

* ``configMap``: reference an existing ConfigMap

  * ``name`` (string, required)
  * ``key`` (string, default: ``locustfile.py``)

* Built into image

  The image contains a locustfile.
  If the filename isn't ``locustfile.py`` (default locustfile name), pass ``-f <custom/path/locustfile>`` via ``spec.args``.


Metadata
~~~~~~~~

``spec.labels`` / ``spec.annotations`` (object, optional)

  User-provided labels/annotations merged onto all managed resources.

Per-role overrides
~~~~~~~~~~~~~~~~~~

This allows customizing **master** and **worker** pods separately.

``spec.master`` / ``spec.worker`` (object, optional)

* ``labels`` / ``annotations`` (object, optional)
* ``resources`` (object, optional).

Example:
  .. code-block:: yaml

    master:
      labels:
        my.custom.label/is-locust-master: "true"
      resources:
        requests:
          cpu: "500m"
          memory: "256Mi"
        limits:
          cpu: "1"
          memory: "512Mi"

Extended
~~~~~~~~

``spec.imagePullPolicy`` (string, optional)

    The `image pull policy <https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy>`_ for master/worker pods.

``spec.imagePullSecrets`` (array, optional)

    The `image pull secrets <https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod>`_ for master/worker pods.
    e.g. ``[{ name: my-regcred }]`` for private registries.


Examples
--------

Inline locustfile
~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    apiVersion: locust.io/v1
    kind: LocustTest
    metadata:
      name: load-test-v1
    spec:
      image: locustio/locust:latest
      workers: 5
      args:
        --host http://my.site.com/api/v1
        --run-time=10m
        --users=500
        --spawn-rate=50
      env:
      - name: LOCUST_LOGLEVEL
        value: INFO
      locustfile:
        content: |
          from locust import HttpUser, task
          class TestUser(HttpUser):
              @task
              def index(self):
                  self.client.get("/")

External ConfigMap locustfile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: v2-locustfile
    data:
      mytest.py: |
        from locust import HttpUser, task
        class PingUser(HttpUser):
            @task
            def ping(self):
                self.client.get("/ping")
    ---
    apiVersion: locust.io/v1
    kind: LocustTest
    metadata:
      name: load-test-v2
    spec:
      workers: 5
      args:
        -f mytest.py
        --host http://my.site.com/api/v2
        --run-time=10m
        --users=500
        --spawn-rate=50
      locustfile:
        configMap:
          name: v2-locustfile

Custom Master/Worker pod configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    apiVersion: locust.io/v1
    kind: LocustTest
    metadata:
      name: locust-test
    spec:
      labels:
        # Merged into all managed resources labels
        my.custom.label/group: group1
      image: my-private-registry/custom-image:1.0.0
      imagePullSecrets:
        - name: regcred
      workers: 5
      master:
        annotations:
          # Merged into master pod annotations
          my.custom.annotations/version: "1.0.0"
        labels:
          # Merged into master pod labels
          my.custom.label/is-locust-master: "true"
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1"
            memory: "1Gi"
      worker:
        annotations:
          # Merged into worker pod annotations
          my.custom.annotations/version: "1.0.0"
        labels:
          # Merged into worker pod labels
          my.custom.label/is-locust-master: "false"
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1"
            memory: "1Gi"

Headless run
~~~~~~~~~~~~

.. code-block:: yaml

    apiVersion: locust.io/v1
    kind: LocustTest
    metadata:
      name: headless-test
    spec:
      workers: 2
      args:
        --host http://locust.io/
        --headless
        --run-time=5m
        --users=300
        --spawn-rate=30
      locustfile:
        content: |
          from locust import HttpUser, task
          class TestUser(HttpUser):
              @task
              def index(self):
                  self.client.get("/")

Upgrade
-------

Helm
~~~~

.. code-block:: bash

   $ helm repo update
   $ helm upgrade locust-operator locust-operator/locust-operator \
     --namespace locust-operator \
     --reuse-values

Helm `does not support updating or deleting CRDs <https://helm.sh/docs/chart_best_practices/custom_resource_definitions/#some-caveats-and-explanations>`_.
You may need to update the CRD manually when upgrading the operator.

.. code-block:: bash

   $ kubectl apply -f https://raw.githubusercontent.com/locustio/k8s-operator/refs/tags/helm-chart-<version>/charts/locust-operator/crds/locusttest.yaml

Uninstall
---------

1. Delete all ``LocustTest`` resources (optional but recommended)

.. code-block:: bash

   $ kubectl get locusttests --all-namespaces
   $ kubectl delete locusttests --all --all-namespaces

Helm
~~~~

.. code-block:: bash

   # Uninstall the Helm release
   $ helm uninstall locust-operator --namespace locust-operator
   # Remove the LocustTest CRD
   $ kubectl delete crd locusttests.locust.io

Manifest Files
~~~~~~~~~~~~~~

.. code-block:: bash

   $ kubectl delete -f locust-operator.yaml