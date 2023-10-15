.. _installation:

Installation
============

0. `Install Python <https://docs.python-guide.org/starting/installation/>`_ (3.8 or later)

1. Install the package (check `the wiki <https://github.com/locustio/locust/wiki/Installation>`_ if the installation fails)

.. code-block:: console

    $ pip3 install locust

2. Validate your installation

.. code-block:: console
    :substitutions:

    $ locust -V
    locust |version| from /usr/local/lib/python3.10/site-packages/locust (python 3.10.6)

3. Done! Now you can :ref:`create your first test <quickstart>`

Optional: CLI tab completion
----------------------------

Locust uses the argcomplete_ module to provide tab completions for the ``locust`` command line interface.
This is entirely optional; if you don't care about tab completion, you can skip this section entirely!
If you do want to enable tab completion, first install the ``argcomplete`` module
into the same environment where you installed ``locust``:

.. code-block:: console

    $ pip3 install argcomplete

Then add this line to your shell config file
(``~/.bashrc`` if you use ``bash``, ``~/.zshrc`` if you use ``zsh``):

.. code-block:: console

    eval "$(register-python-argcomplete locust)"

Restart your shell, and you should have working tab completion for the ``locust`` CLI!
If this doesn't work, `check the argcomplete documentation <https://kislyuk.github.io/argcomplete/>`_.

Pre-release builds
------------------

If you need the latest and greatest version of Locust and cannot wait for the next release, you can install a dev build like this:

.. code-block:: console

    $ pip3 install -U --pre locust

Pre-release builds are published every time a branch/PR is merged into master.

Install for development
-----------------------

If you want to modify Locust, or contribute to the project, see :ref:`developing-locust`.

.. _argcomplete: https://github.com/kislyuk/argcomplete