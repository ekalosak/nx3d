Usage
============

There are two main ways in which ``nx3d`` is intended to be used. First, as a quick, batteries-included way to visualize
your graph. Second, as a more involved tool for visualizing temporal processes over graphs. On this page, you will find
how-to-guides for both use-cases.

But before that, an explanation of the "special attributes" ``nx3d`` uses to keep track of the desired 3D render state.

Render attributes
--------------------------------------------

Please note that ``nx3d`` will modify your graph in place. By default, it will assign a set of static render
attributes to your graph's nodes and edges. ``nx3d`` uses these attributes to control the state of the 3D
render. These attributes include 'color', 'label', and so on - see the :doc:`api` page for a complete list.

You can provide default values for render attributes to ``nx3d.Nx3D.__init__`` in the case you don't want to initialize
them per-element yourself. For example ``app=Nx3D(my_graph, edge_color=(0, 1, 0, 1)``.
These static defaults will be applied to your graph upon ``Nx3D`` initialization as ``g.edges[e]['color'] ==
edge_color for e in g.edges``.

In case you have no preference, sensible defaults are provided so you can get started with just ``nx3d.plot(g)``.

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

Animate my graph process
-------------------------

You can update render attributes dynamically by providing a ``state_trans_func: Callable[[nx.Graph, int, float],
None]``. This function, if provided, will update the graph in place every ``state_trans_freq: float=1.`` seconds. The
updated render attributes are automatically propagated to the 3D render with the built-in ``Nx3D.stateUpdateTask`` every
time the main loop ticks. With that in mind, you should make sure the ``state_trans_func`` doesn't take too long because
it does block the frame update rate.

.. code-block:: python

   import networkx as nx
   import nx3d

   def my_graph_process(g: nx.Graph, di: int, dt: float):
      """ update the render graph attributes in place, for a list of render attributes, see the API page """
      for n, nd in g.nodes(data=True):
          nd['my_val'] += sum(g.nodes[n1]['my_val'] for n1 in g[n])
          nd['label'] = str(nd['my_val']

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

The main loop
-------------------------

In short, you don't need to use the ``app.run()`` mainloop that's built in to panda3d.ShowBase. For example, a trivial
main loop is:

.. code-block:: python
   import networkx as nx
   import nx3d

   FPS = 32

   g = nx.erdos_renyi_graph(45,0.05)
   app = Nx3D(g)

   while 1:
      app.taskMgr.step()
      time.sleep(1 / FPS)

More information
-------------------------
For complete code examples, see the :doc:`examples` page.
For more detail on the arguments to the functions described on this page, see the :doc:`api` page.
