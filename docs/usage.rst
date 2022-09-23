Usage
============

There are two main ways in which ``nx3d`` is intended to be used. First, as a quick, batteries-included way to visualize
your graph. Second, as a more involved tool for visualizing temporal processes over graphs. On this page, you will find
how-to-guides for both use-cases.

But before that, an explanation of the "special attributes" ``nx3d`` uses to keep track of the desired 3D render state.

Special graph attributes
--------------------------------------------

Please note that ``nx3d`` will modify your graph in place. By default, it will assign a set of static "special
attributes" to your graph's nodes and edges. ``nx3d`` uses these special attributes to control the state of the 3D
render. These attributes include 'color', 'label', and so on - see the :doc:`api` page for a complete list.

You can provide default values to ``nx3d.Nx3D.__init__`` e.g. with the ``edge_color`` argument. These static defaults
will be applied to your graph upon ``Nx3D`` initialization e.g. ``g.edges[e]['color'] == edge_color for e in g.edges``.
But you don't `have` to provide defaults - you can run ``nx3d.plot(g)`` with batteries included.

As you'll see in the "Plot my graph process" section below, you can update these attributes dynamically every
``state_trans_freq: float=1.`` seconds. These updates are automatically propagated to the 3D render. You need only
implement a ``state_trans_func: Callable[[nx.Graph, int, float], None]`` that updates the special attributes in place.

This way, you don't need to know what ``panda3d`` is to leverage its powerful 3D graphics engine in your project.

Plot my graph
-------------------------

To plot your graph, write something like the following:

.. code-block:: python

   import networkx as nx
   import nx3d

   def make_my_graph(...) -> nx.Graph:
      # for example, `return nx.frucht_graph()`
      ...

   g = make_my_graph()
   nx3d.plot(g, autolabel=True, edge_color=(0, 1, 0.5, 1))

For more info on the arguments to ``nx3d.plot``, see the :doc:`api` page.

Plot my graph process
-------------------------

To change the graph over time, the ``nx3d.Nx3D`` class has an optional argument for a state transition function. For
more details, see the :doc:`api` page - to see how to use it, read on below.

.. code-block:: python

   import networkx as nx
   import nx3d

   def my_graph_markov_process(g: nx.Graph, di: int, dt: float):
      """ update the special graph attributes in place, for a list of special attributes, see the API page """
      for nd in g:
          g.nodes[nd]['my_val'] += sum(nbrdict['my_val'] for nbrdict in g[nd].values())
          g.nodes[nd]['label'] = str(g.nodes[nd]['my_val'])

   def _init_my_graph(g):
      for nd in g:
          g.nodes[nd]['my_val'] = 0.00001

   g = nx.frucht_graph()
   _init_my_graph(g)
   nx3d.plot(
      g,
      state_trans_freq=1.,
      state_trans_func=my_graph_markov_process,
   )

Of course, you can bypass the Markov nature of the process by accumulating information in the graph outside the special
attributes.

For complete code examples, see the :doc:`examples` page.
