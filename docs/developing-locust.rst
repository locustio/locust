.. _developing-locust:

=================
Developing Locust
=================

You want to contribute to Locust? Great! Here is a list of `open bugs/feature requests <https://github.com/locustio/locust/issues>`_.

Install Locust for development
==============================

Fork Locust on `GitHub <https://github.com/locustio/locust/>`_ and then run

.. code-block:: console

    $ git clone git://github.com/<YourName>/locust.git # clone the repo
    $ pip3 install -e locust/                          # install in editable mode

Now the ``locust`` command will run *your* code with no need for reinstalling after making changes.

To contribute your changes, push to a branch in your repo and then `open a PR on github <https://github.com/locustio/locust/compare>`_. 

Before you open a pull request, make sure all the checks work. And if you are adding a feature, make sure it is documented (in ``docs/*.rst``).

Testing your changes
====================

We use `tox <https://tox.readthedocs.io/en/stable/>`_ to automate tests across multiple Python versions:

.. code-block:: console

    $ pip3 install tox
    $ tox
    ...
    py38: install_deps> python -I -m pip install cryptography mock pyquery retry
    py38: commands[0]> python3 -m pip install .
    ...
    py38: commands[1]> python3 -m unittest discover
    ...

To only run a specific suite or specific test you can call `pytest <https://docs.pytest.org/>`_ directly:

.. code-block:: console

    $ pytest locust/test/test_main.py::DistributedIntegrationTests::test_distributed_tags

Formatting and linting
======================

Locust uses `ruff <https://github.com/astral-sh/ruff/>`_ for formatting and linting. The build will fail if code does not adhere to it. If you run vscode it will automatically run every time you save a file, but if your editor doesn't support it you can run it manually:

.. code-block:: console

    $ pip3 install ruff
    $ python -m ruff --fix <file_or_folder_to_be_formatted>
    $ python -m ruff format <file_or_folder_to_be_formatted>

You can validate the whole project using tox:

.. code-block:: console

    $ tox -e ruff
    ruff: install_deps> python -I -m pip install ruff==0.1.13
    ruff: commands[0]> ruff check .
    ruff: commands[1]> ruff format --check
    104 files already formatted
      ruff: OK (1.41=setup[1.39]+cmd[0.01,0.01] seconds)
      congratulations :) (1.47 seconds)

Build documentation
===================

The documentation source is in the `docs/ <https://github.com/locustio/locust/tree/master/docs/>`_ directory. To build the documentation you first need to install the required Python packages:

.. code-block:: console

    $ pip3 install -r docs/requirements.txt

Then you can build the documentation locally using:

.. code-block:: console

    $ make build_docs
    
Then the documentation should be build and available at ``docs/_build/index.html``.


Making changes to Locust's Web UI
=================================

The modern Web UI is built using React and Typescript

Setup
-----

Node
````

Install node using nvm to easily switch between node version

- Copy and run the install line from `nvm <https://github.com/nvm-sh/nvm>`_ (starts with curl/wget ...)

- Verify nvm was installed correctly

.. code-block:: console

    $ nvm --version

- Install the proper Node version according to engines in the ``locust/webui/package.json``

.. code-block:: console

    $ nvm install {version}
    $ nvm alias default {version}

Yarn
````

- Install Yarn from their official website (avoid installing through Node if possible)
- Verify yarn was installed correctly

.. code-block:: console

    $ yarn --version

- Next in web, install all dependencies

.. code-block:: console

    $ cd locust/webui
    $ yarn


Developing
----------

To develop the frontend, run ``yarn dev``. This will start the Vite dev server and allow for viewing and editing the frontend, without needing to a run a locust web server

To develop while running a locust instance, run ``yarn dev:watch``. This will output the static files to the ``dist`` directory. Vite will automatically detect any changed files and re-build as needed. Simply refresh the page to view the changes

To compile the webui, run ``yarn build``

The frontend can additionally be built using make:

.. code-block:: console

    $ make frontend_build


Linting
-------

Run ``yarn lint`` to detect lint failures in the frontend project. Running ``yarn lint --fix`` will resolve any issues that are automatically resolvable. Your IDE can additionally be configured with ESLint to resolve these issues on save.

Formatting
----------

Run ``yarn format`` to fix any formatting issues in the frontend project. Once again your IDE can be configured to automatically format on save.

Typechecking
------------

We use Typescript in the frontend project. Run ``yarn type-check`` to find any issues.
