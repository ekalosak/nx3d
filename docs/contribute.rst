Contributing
================================
Thank you for considering contributing to ``nx3d``.

This project is free and open source, so the best way to contribute is by writing code.

This page describes the development cycle you may follow - it should be familiar to most developers.

1. Pick an issue
--------------------------------------
Navigate to the issue tracker and look for "good beginner issues".
Or if you have a bee in your bonnet about something, please feel free to go off king/queen/royal.

2. Clone the code
--------------------------------------
.. code-block:: sh

  cd ~/path/to-your/projects/
  git clone git@github.com:ekalosak/nx3d.git

3. Setup the development environment
--------------------------------------

You can do this as you like, though you might consider using pyenv and poetry for replicable virtual environments and
package management:

#. Install ``pyenv`` and ``pyenv-virtualenv`` for managing virtual environments.
#. Run ``pyenv install 3.10.7`` or whichever supported version of Python.
#. Run ``pyenv virtualenv 3.10.7 nx3d3107`` to create the virtual environment.
#. Run ``pyenv activate nx3d3107`` to activate the virtual environment. ``python --version`` should be correct.
#. Install ``poetry`` for managing dependencies and virtual environments.
#. Run ``poetry shell`` to open a clean shell. ``which python`` should be a poetry shim.
#. Run ``poetry install`` to install the project, dependencies, and developer dependencies.
#. Run ``poetry install . -e`` to install a development copy of ``nx3d``.

Verify the setup by running ``python -m nx3d``. You should see a popup appear with a neat little graph widget you can
spin around and zoom in on.

If you need to update project dependencies, note that that you `will` need to use poetry.

4. Solve the issue you picked
--------------------------------------
Ok now write code. Use ``pytest`` to make sure core functionality hasn't broken. Run ``python -m nx3d diffusion`` to
confirm integration works.

5. Set up pre-commit
--------------------------------------
The pre-commit hooks defined in ``.pre-commit-config.yaml`` apply linting and formatting to keep the project clean. Please
use the pre-commit hooks before opening a PR.

First time setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From this project's root, initialize pre-commit as follows:

.. code-block:: sh

  pre-commit install
  pre-commit run -a

6. Update the docs
--------------------------------------

#. Update the inline docstrings and/or the files in the docs/ directory.
#. Navigate to the docs/ dir and run ``make html`` to preview your changes.
#. When you cut a PR, the CI will trigger a ReadTheDocs build.
#. When merged, the CD will publish those docs (3).

First time updating the docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
I used ``brew install python-sphinx``, see installation instructions on
`www.sphinx-doc.org <https://www.sphinx-doc.org/en/master/usage/installation.html>`_.

7. Open a PR
--------------------------------------
Increment the version in the pyproject.toml and docs/conf.py files.
When a PR is created or updated, code checks will be run and documentation preview will be generated.
When a PR is merged, the code will be pushed to PyPi and the docs to ReadTheDocs.
