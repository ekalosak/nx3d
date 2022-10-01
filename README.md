# nx3d

[![-missing homepage-](https://img.shields.io/badge/home-GitHub-blueviolet)](https://github.com/ekalosak/nx3d)
[![-missing docs-](https://img.shields.io/badge/docs-ReadTheDocs-blue)](https://nx3d.readthedocs.io/en/latest/)
[![-missing pypi-](https://img.shields.io/pypi/v/nx3d)](https://pypi.org/project/nx3d/)
[![-missing build status-](https://img.shields.io/github/workflow/status/ekalosak/nx3d/Build%20nx3d%20and%20publish%20to%20PyPi)](https://github.com/ekalosak/nx3d/actions)

[![-missing project maturity-](https://img.shields.io/badge/status-experimental-green)](https://nx3d.readthedocs.io/en/latest/maturity.html)
[![-missing download count-](https://img.shields.io/pypi/dw/nx3d)](https://pypistats.org/packages/nx3d)

The missing link between `panda3d` and `networkx`.

![-missing gif of frucht graph-](https://raw.githubusercontent.com/ekalosak/nx3d/cf473d1dfab506ecd4044f4693c09aea0e1153ba/data/frucht.gif)

# Installation
```sh
pip install nx3d
```

# Check your installation

## The four nx.Graph classes

### nx.Graph demo
```sh
python -m nx3d
```

### nx.DiGraph demo
```sh
python -m nx3d dir
```

### nx.MultiGraph demo
```sh
python -m nx3d mul
```

### nx.MultiDiGraph demo
```sh
python -m nx3d mul dir
```

## Dynamic graph processes

### Diffusion demo
```sh
python -m nx3d diffusion watt nolabel
```

### Game of Life demo
```sh
python -m nx3d life nofilter
```

# Usage
In your Python code:
```python
import networkx as nx
import nx3d

g = nx.frucht_graph()
nx3d.plot(g)
```

# Next steps
Check out the [docs](https://nx3d.readthedocs.io/en/latest/) for tutorials, how-to-guides, explanations, and reference
material.
