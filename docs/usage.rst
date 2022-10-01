Usage
============

There are a few ways in which ``nx3d`` is intended to be used. On this page, you will find how-to-guides for these known
use-cases. If your use-case isn't documented here, please feel free to submit an issue following :doc:`support`.

But before that, an explanation of the "render attributes" ``nx3d`` uses to keep track of the desired 3D render state.

Render attributes
--------------------------------------------

Please note that ``nx3d`` will modify your graph in place. By default, it will assign a set of static render
attributes to your graph's nodes and edges. ``nx3d`` reads these attributes in each frame update to control the state of
the 3D render. These attributes include 'color', 'label', and so on.

You can provide uniform static render attributes to ``nx3d.Nx3D.__init__`` in the case you don't want to initialize
them per-element yourself. For example ``app=Nx3D(my_graph, edge_color=(0, 1, 0, 1)`` will apply
``my_graph.edges[e]['color'] = edge_color for e in my_graph.edges`` uniformly across all edges.

In case you have no preference, sensible defaults are provided so you can get started with just ``nx3d.plot(g)``.

Plot a graph
-------------------------

To plot your graph, write something like the following:

.. code-block:: python

   import networkx as nx
   import nx3d

   g = nx.frucht_graph()
   nx3d.plot(g, autolabel=True, edge_color=(0, 1, 0.1, 1))

Animate a graph process
-------------------------

You can update render attributes dynamically by providing a ``state_trans_func: Callable[[nx.Graph, int, float],
None]``. This function, if provided, will update the graph in-place every ``state_trans_freq: float=1.`` seconds. The
updated render attributes are automatically propagated to the 3D render with the built-in ``Nx3D.stateUpdateTask`` every
time the main loop ticks.

Note that the state transformation frequency is independent of the 3D render's frame-rate - unless the state function
blocks for a noticable length of time.  With that in mind, you should make sure the ``state_trans_func`` doesn't take
too long to return.

The following minimal example shows how to control the ``'label'`` render attribute based on some simple graph process.

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
      state_trans_func=my_graph_process,
   )

Interact with a graph process
--------------------------------------------------

To interact with the graph process, you'll need to control your own main loop and react to the events that Nx3D
enqueues. As of ``nx3d 22.10.2``, you are limited to keyboard events, and the keys ``wasdio`` are reserved for camera
movement. An example of this usage is on the :doc:`examples` page.


More information
-------------------------
For complete code examples, see the :doc:`examples` page.
For more detail on the arguments to the functions described on this page, see the :doc:`api` page.
