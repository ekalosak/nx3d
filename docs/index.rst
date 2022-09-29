.. nx3d documentation master file, created by
   sphinx-quickstart on Thu Sep 15 08:31:15 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to nx3d's documentation!
================================

``nx3d`` provides 3D plotting functionality for the ``networkx`` Python package.

The `project homepage <https://github.com/ekalosak/nx3d>`_ has quickstart instructions.

.. image:: https://raw.githubusercontent.com/ekalosak/nx3d/cf473d1dfab506ecd4044f4693c09aea0e1153ba/data/frucht.gif
   :width: 400

Alternatives
------------------------------------

There are several alternative 3D plotting tools for networkx graphs.
You may find your solution among these.
They are better suited to plotting scientific data in the main.


Using matplotlib
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- https://networkx.org/documentation/stable/auto_examples/3d_drawing/plot_basic.html#sphx-glr-auto-examples-3d-drawing-plot-basic-py


Using plotly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- https://plotly.com/python/v3/3d-network-graph/
- https://deepnote.com/@deepnote/3D-network-visualisations-using-plotly-a18c5e37-a517-4b27-bfde-1fee94a5760f
- https://towardsdatascience.com/visualize-high-dimensional-network-data-with-3d-360-degree-animated-scatter-plot-d583932d3693

Using Mayavi2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- https://networkx.org/documentation/stable/auto_examples/3d_drawing/mayavi2_spring.html


So why another one?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because there's the potential for richer visualization - one where your graph data can be visualized in interactive
layers. Because getting started should be a one-liner: . Because data should
be fun.


Hello world, start here
------------------------------------
Install with ``pip install nx3d``.
Check your installation with ``python -m nx3d autolabel``.
Use in your code like ``nx3d.plot(nx.random_lobster(100,.9,.9))``.
See the :doc:`examples` page and the :doc:`usage` next.


Limitations
------------------------------------
The major known limitations are listed below.

large graphs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Currently, this project will start to clip (non-smooth 3d visuals) when the graph has >250 nodes on my 5yr old macbook.

render attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``nx3d`` doesn't have all the same controls that Matplotlib does. While you can set size, label, color, and position -
some attributes like marker kind aren't yet available. See `this
milestone<https://github.com/ekalosak/nx3d/milestone/3`_ for progress on these features.

threading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The networkx graph controling the render state is singular, but it has no synchronization primitives. See Panda3D's docs
on threading if you need this functionality.

Code of Conduct
------------------------------------
`Contributor Covenant <https://www.contributor-covenant.org/version/2/1/code_of_conduct/>`_

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   install
   support
   examples
   usage
   api
   contribute
