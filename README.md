# nx3d

[![-missing homepage badge-](https://img.shields.io/badge/home-GitHub-blueviolet)](https://github.com/ekalosak/nx3d)
[![-missing docs badge-](https://img.shields.io/badge/docs-ReadTheDocs-blue)](https://nx3d.readthedocs.io/en/latest/)
[![-missing pypi badge-](https://img.shields.io/pypi/v/nx3d)](https://pypi.org/project/nx3d/)
[![-missing build status badge-](https://img.shields.io/github/workflow/status/ekalosak/nx3d/build)](https://github.com/ekalosak/nx3d/actions)

The missing 3D plotting functionality for the excellent `networkx` Python package.

![-missing image of frucht graph-](./data/frucht.gif)

# Installation
In your shell:
```sh
pip install nx3d
```

# Quickstart
After installation,

## From your shell
```sh
python -m nx3d
```

## In your Python REPL
```python
import nx3d
nx3d.demo()
```

# Usage
In your Python code:
```python
import networkx as nx
import nx3d

g = nx.frucht_graph()
nx3d.plot(g)
```

For more customization, use the `nx3d.plot_nx3d()` function.

# Contribute
Thank you for considering contributing to `nx3d`.

Currently, there's no enforced testing, formatting, linting, or typechecking with CI. Let's say that's intentional to
keep this young project lightweight.  With that in mind, the pre-commit hooks defined in `.pre-commit-config.yaml` apply
linting and formatting to keep the project clean. Please use the pre-commit hooks before opening a PR.

## Clone the code

## Setup the development environment

You can do this as you like, though you might consider:
1. Install `poetry`
2. Run `poetry shell`
3. Run `poetry install`
4. Verify the installation by running `python -m nx3d`

## Set up pre-commit
From this project's root, initialize pre-commit as follows:

```sh
pre-commit install
pre-commit run -a
```

## Update the docs
1. Update the inline docstrings and/or the files in the docs/ directory.
2. Navigate to the docs/ dir and run `make html`.

### First time updating the docs
I used `brew install python-sphinx`, see installation instructions on [www.sphinx-doc.org](https://www.sphinx-doc.org/en/master/usage/installation.html).

## Hack on some code
- heterogeneous sizes and colors
- node labels
- edge labels
- support for DiGraph and MultiDiGraph
- tests
  - for the trig: add collision nodes to the ends of the edges and check that they collide with source and sink nodes
  - for the API: fizzbuzz it, check some basic content of the ShowBase returned by `plot_nx3d`
  - CI running the tests and a badge
- interactive camera controls
- animation control via callbacks
- save video / snapshot to file
  (https://docs.panda3d.org/1.10/python/reference/direct.showbase.ShowBase?highlight=screenshot#direct.showbase.ShowBase.ShowBase.movie)

## Open a PR
- fork this repo
- push your code to your repo
- open a pull request against this repo

When it merges, CD will push to PyPi.
