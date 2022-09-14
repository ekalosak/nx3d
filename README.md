# nx3d

[![-missing docs badge-](https://img.shields.io/badge/docs-GitHub-blue)](https://github.com/ekalosak/nx3d/)
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

Currently, there's no testing or enforced formatting with CI to keep this young project lightweight.
With that in mind, the pre-commit hooks defined in `.pre-commit-config.yaml` apply linting and formatting to keep the
project clean. Please use the pre-commit hooks before making a PR.

## Set up pre-commit
From this project's root, initialize pre-commit as follows:

```sh
pre-commit install
pre-commit run -a
```
