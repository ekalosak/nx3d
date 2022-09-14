# nx3d

The missing 3D plotting functionality for the excellent `networkx` Python package.

![frucht graph](./data/frucht.gif)

# Installation
In your shell:
```sh
pip install nx3d
```

# Test
In your Python REPL:
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
