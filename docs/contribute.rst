Contributing
================================
Thank you for considering contributing to ``nx3d``.

This project is free and open source, so the best way to contribute is by writing code.

- Pick an issue from the issue tracker or bring your own issue.
- Clone the code
- Setup the dev environment
- Test the code with pytest
- Check the code with the pre-commits and make a PR

Setup the development environment
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

First time updating the docs
-------------------------------------------
I used ``brew install python-sphinx``, see installation instructions on
`www.sphinx-doc.org <https://www.sphinx-doc.org/en/master/usage/installation.html>`_.
