.. _developing-locust:

=================================
Developing and Documenting Locust
=================================

You want to contribute to Locust? Great! Here is a list of `open bugs/feature requests <https://github.com/locustio/locust/issues>`_.

Install Locust for development
==============================

Fork Locust on `GitHub <https://github.com/locustio/locust/>`_ and then

.. code-block:: sh

    # clone the repo:
    $ git clone git://github.com/<YourName>/locust.git

    # install the poetry build system, version 1.8.5, see https://python-poetry.org/docs/#installation

    # install the required poetry plugins:
    $ poetry self add "poethepoet[poetry_plugin]"
    $ poetry self add "poetry-dynamic-versioning[plugin]"

    # perform an editable install of the "locust" package along with the dev and test packages:
    $ poetry install --with dev,test

Now the ``poetry run locust`` command will run *your* code (with no need for reinstalling after making changes).

To contribute your changes, push to a branch in your repo and then `open a PR on github <https://github.com/locustio/locust/compare>`_. 

If you install `pre-commit <https://pre-commit.com/>`_, linting and format checks/fixes will be automatically performed before each commit.

Before you open a pull request, make sure all the tests work. And if you are adding a feature, make sure it is documented (in ``docs/*.rst``).

If you're in a hurry or don't have access to a development environment, you can simply use `Codespaces <https://github.com/features/codespaces>`_, the github cloud development environment.  On your fork page, just click on *Code* then on *Create codespace on <branch name>*, and voila, your ready to code and test.

Testing your changes
====================

We use `tox <https://tox.readthedocs.io/en/stable/>`_ to automate tests across multiple Python versions:

.. code-block:: console

    $ tox
    ...
    py39: commands[1]> python3 -m unittest discover
    ...

To only run a specific suite or specific test you can call `pytest <https://docs.pytest.org/>`_ directly:

.. code-block:: console

    $ pytest locust/test/test_main.py::DistributedIntegrationTests::test_distributed_tags

Debugging
=========

See: :ref:`running-in-debugger`.

Formatting and linting
======================

Locust uses `ruff <https://github.com/astral-sh/ruff/>`_ for formatting and linting. The build will fail if code does not adhere to it. If you run vscode it will automatically run every time you save a file, but if your editor doesn't support it you can run it manually:

.. code-block:: console

    $ ruff --fix <file_or_folder_to_be_formatted>
    $ ruff format <file_or_folder_to_be_formatted>

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

The documentation source is in the `docs/ <https://github.com/locustio/locust/tree/master/docs/>`_ directory. To build the documentation you'll need to `Install Locust for development`_ then

#. Install the documentation requirements:

    .. code-block:: console

        $ poetry install --with docs

#. Build the documentation locally:

    .. code-block:: console

        $ make build_docs
    
View your generated documentation by opening ``docs/_build/index.html``.


Making changes to Locust's Web UI
=================================

The Web UI is built using React and Typescript

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

- Next, install all dependencies

.. code-block:: console

    $ cd locust/webui
    $ yarn


Developing
----------

To develop while running a locust instance, run ``yarn watch``. This will output the static files to the ``dist`` directory. Vite will automatically detect any changed files and re-build as needed. Simply refresh the page to view the changes

In certain situations (usually when styling), you may want to develop the frontend without running a locust instance. Running ``yarn dev`` will start the Vite dev server and allow for viewing your changes.

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
