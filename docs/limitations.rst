Limitations
===============
``nx3d`` is still a work in progress (status: experimental). The major known limitations are listed on this page. For
more detail, see the issue tracker.


networkx graph types
---------------
Currently, this project only supports ``nx.Graph`` and ``nx.DiGraph``. Multigraphs are not yet supported.


large graphs
---------------
Currently, this project will start to clip (non-smooth 3d visuals) when the graph has >250 nodes on my 5yr old macbook.

graph attribute control
---------------
Currently, this project only supports changing colors and labels using graph attributes (e.g. ``g.nodes[nd]['color']``).
Dynamic positions, markers, shapes, and graph geometry are planned but not yet available.
