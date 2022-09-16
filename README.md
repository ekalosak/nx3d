# nx3d

[![-missing homepage-](https://img.shields.io/badge/home-GitHub-blueviolet)](https://github.com/ekalosak/nx3d)
[![-missing docs-](https://img.shields.io/badge/docs-ReadTheDocs-blue)](https://nx3d.readthedocs.io/en/latest/)
[![-missing pypi-](https://img.shields.io/pypi/v/nx3d)](https://pypi.org/project/nx3d/)
[![-missing build status-](https://img.shields.io/github/workflow/status/ekalosak/nx3d/Build%20nx3d%20and%20publish%20to%20PyPi)](https://github.com/ekalosak/nx3d/actions)

[![-missing status-](https://img.shields.io/badge/status-experimental-brightgreen)
[![-missing downloads-](https://img.shields.io/pypi/dw/nx3d)]

The missing 3D plotting functionality for the excellent `networkx` Python package.

![-missing gif of frucht graph-](https://raw.githubusercontent.com/ekalosak/nx3d/cf473d1dfab506ecd4044f4693c09aea0e1153ba/data/frucht.gif)

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
2. Navigate to the docs/ dir and run `make html` to preview your changes.
3. When you cut a PR, the CI will trigger a ReadTheDocs build.
4. When merged, the CD will publish those docs (3).

### First time updating the docs
I used `brew install python-sphinx`, see installation instructions on [www.sphinx-doc.org](https://www.sphinx-doc.org/en/master/usage/installation.html).

## Hack on some code
- NX-0 P2 support for DiGraph and MultiDiGraph
- NX-1 P2 better default camera behavior
  - set initial position to capture full graph
  - initial movement is spinning at ^ radius
  - wasd around sphere with constant radius
  - no control for 3.5 sec starts spinning again
  - gui
- NX-2 P2 implement demo with state transformation
- NX-3 P3 mouse click and pull expands graph
- NX-4 P3 tests
  - for the trig: add collision nodes to the ends of the edges and check that they collide with source and sink nodes
  - for the API: fizzbuzz it, check some basic content of the ShowBase returned by `plot_nx3d`
  - CI running the tests and a badge
- NX-9 P3 press r to reset
- NX-5 P4 heterogeneous sizes and colors
- NX-6 P4 save video / snapshot to file
  (https://docs.panda3d.org/1.10/python/reference/direct.showbase.ShowBase?highlight=screenshot#direct.showbase.ShowBase.ShowBase.movie)
- NX-8 P4 mouse click and drag on node pulls with stickyness on original location along node to free area and finally to
  gravity around destination node.
  - blocked by NX-3
- NX-7 P5 physics like goop so when moved
  - blocked by NX-3
- NX-10 P5 enable 'peek' with camera by shifting lense with u, i

## Open a PR
- fork this repo
- push your code to your repo
- open a pull request against this repo

When it merges, CD will push to PyPi.
